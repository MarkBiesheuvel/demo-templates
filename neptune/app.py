#!/usr/bin/env python3
from json import dumps as json_encode
from aws_cdk import (
    core,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_neptune as neptune,
    aws_s3_assets as s3_assets,
)


class NeptuneCluster(core.Construct):

    def __init__(
            self, scope: core.Construct, id: str,
            vpc: ec2.IVpc, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        stack = core.Stack.of(self)

        role = iam.Role(
            self, 'NeptuneRole',
            assumed_by=iam.ServicePrincipal('rds.amazonaws.com'),
        )

        sg = ec2.SecurityGroup(
            self, 'SecurityGroup',
            vpc=vpc,
        )

        cluster = neptune.DatabaseCluster(
            self, 'Cluster',
            vpc=vpc,
            instance_type=neptune.InstanceType.R5_LARGE,
            associated_roles=[role],
            security_groups=[sg],
            removal_policy=core.RemovalPolicy.DESTROY,
        )

        self.endpoint = cluster.cluster_endpoint.hostname
        self.role = role
        self.security_group = sg


class Instance(core.Construct):

    def __init__(
            self, scope: core.Construct, id: str,
            vpc: ec2.IVpc, cluster: NeptuneCluster,
            **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        role = iam.Role(
            self, 'Ec2Role',
            assumed_by=iam.ServicePrincipal('ec2.amazonaws.com'),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name('AmazonSSMManagedInstanceCore'),
            ],
        )

        config_asset = s3_assets.Asset(
            self, 'ConfigYaml',
            path='./files/neptune-remote.yaml',
            readers=[role],
        )

        sg = ec2.SecurityGroup(
            self, 'SecurityGroup',
            vpc=vpc,
        )

        user_data = ec2.UserData.for_linux()
        user_data.add_commands(
            'yum update -y',
            'yum install -y java-1.8.0-devel',
            'cd ~',
            # Install the CA certificate
            'mkdir /tmp/certs/',
            'cp /etc/pki/java/cacerts /tmp/certs/cacerts',
            'wget https://www.amazontrust.com/repository/SFSRootCAG2.cer',
            'keytool -importcert -alias neptune-ca -keystore /tmp/certs/cacerts -file /root/SFSRootCAG2.cer -noprompt -storepass changeit',
            # Download Gremlin console
            'wget https://archive.apache.org/dist/tinkerpop/3.4.8/apache-tinkerpop-gremlin-console-3.4.8-bin.zip',
            'unzip apache-tinkerpop-gremlin-console-3.4.8-bin.zip',
            # Download default configuration and update endpoint url
            'cd apache-tinkerpop-gremlin-console-3.4.8',
            'aws s3 cp s3://{bucket}/{key} conf/neptune-remote.yaml'.format(
                bucket=config_asset.s3_bucket_name,
                key=config_asset.s3_object_key,
            ),
            'sed -i "s/ENDPOINT_URL/{endpoint_url}/g" conf/neptune-remote.yaml'.format(
                endpoint_url=cluster.endpoint,
            ),
        )

        ec2.Instance(
            self, 'Instance',
            role=role,
            vpc=vpc,
            security_group=sg,
            user_data=user_data,
            user_data_causes_replacement=True,
            instance_type=ec2.InstanceType.of(
                instance_class=ec2.InstanceClass.BURSTABLE3_AMD,
                instance_size=ec2.InstanceSize.NANO,
            ),
            machine_image=ec2.AmazonLinuxImage(
              generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
            ),
        )

        self.role = role
        self.security_group = sg


class NeptuneStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        stack = core.Stack.of(self)

        vpc = ec2.Vpc(
            self, 'Vpc',
            cidr='10.0.0.0/24',
            max_azs=2,  # Need at least 2 AZs for Neptune
            nat_gateways=1,  # Saving on cost by only using 1 NAT
        )

        # Custom Neptune construct
        cluster = NeptuneCluster(
            self, 'Cluster',
            vpc=vpc,
        )

        # An EC2 instance to run commands from
        instance = Instance(
            self, 'Instance',
            vpc=vpc,
            cluster=cluster,
        )

        # Allow EC2 instance connect to Neptune cluster
        cluster.security_group.add_ingress_rule(
            instance.security_group,
            ec2.Port.tcp(8182)
        )

        # Demo files
        vertices_asset = s3_assets.Asset(
            self, 'VerticesCsv',
            path='./files/vertices.csv',
            readers=[cluster.role],
        )
        edges_asset = s3_assets.Asset(
            self, 'EdgesCsv',
            path='./files/edges.csv',
            readers=[cluster.role],
        )

        core.CfnOutput(
            self, 'Command1LoadVertices',
            value='curl -X POST -H \'{headers}\' {url} -d \'{request_body}\''.format(
                headers='Content-Type: application/json',
                url='https://{endpoint}:8182/loader'.format(endpoint=cluster.endpoint),
                request_body=json_encode({
                    'failOnError': 'FALSE',
                    'format': 'csv',
                    'region': stack.region,
                    'iamRoleArn': cluster.role.role_arn,
                    'source': 's3://{bucket}/{key}'.format(
                        bucket=vertices_asset.s3_bucket_name,
                        key=vertices_asset.s3_object_key,
                    ),
                }),
            )
        )

        core.CfnOutput(
            self, 'Command2LoadEdges',
            value='curl -X POST -H \'{headers}\' {url} -d \'{request_body}\''.format(
                headers='Content-Type: application/json',
                url='https://{endpoint}:8182/loader'.format(endpoint=cluster.endpoint),
                request_body=json_encode({
                    'failOnError': 'FALSE',
                    'format': 'csv',
                    'region': stack.region,
                    'iamRoleArn': cluster.role.role_arn,
                    'source': 's3://{bucket}/{key}'.format(
                        bucket=edges_asset.s3_bucket_name,
                        key=edges_asset.s3_object_key,
                    ),
                }),
            )
        )

        core.CfnOutput(
            self, 'Command3ListAllVertices',
            value=':remote connect tinkerpop.server conf/neptune-remote.yaml',
        )

        core.CfnOutput(
            self, 'Command4ListAllVertices',
            value=':remote console',
        )

        core.CfnOutput(
            self, 'Command5ListAllGamers',
            value='g.V().hasLabel("person")',
        )

        core.CfnOutput(
            self, 'Command6ListAllGamers',
            value='g.V().hasLabel("game").groupCount().by("GameGenre")',
        )

        core.CfnOutput(
            self, 'Command7ListAllGamers',
            value='g.V().has("GamerAlias","groundWalker").as("TargetGamer").out("likes").aggregate("self").in("likes").where(neq("TargetGamer")).out("likes").where(without("self")).dedup().values("GameTitle")',
        )




app = core.App()
NeptuneStack(app, 'NeptuneDemo')
app.synth()
