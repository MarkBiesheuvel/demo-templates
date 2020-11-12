#!/user/bin/env python3
from json import dumps as json_encode
from aws_cdk import (
    core,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_neptune as neptune,
    aws_s3_assets as s3_assets,
)


class Instance(core.Construct):

    def __init__(
            self, scope: core.Construct, id: str,
            vpc: ec2.IVpc, cluster: neptune.CfnDBCluster,
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
            'cd ~', # Execute subsequent commands in home directory
            'wget https://archive.apache.org/dist/tinkerpop/3.4.1/apache-tinkerpop-gremlin-console-3.4.1-bin.zip',
            'unzip apache-tinkerpop-gremlin-console-3.4.1-bin.zip',
            'cd apache-tinkerpop-gremlin-console-3.4.1',
            'wget https://www.amazontrust.com/repository/SFSRootCAG2.pem',
            'aws s3 cp s3://{bucket}/{key} conf/neptune-remote.yaml'.format(
                bucket=config_asset.s3_bucket_name,
                key=config_asset.s3_object_key,
            ),
            'sed -i "s/ENDPOINT_URL/{endpoint_url}/g" conf/neptune-remote.yaml'.format(
                endpoint_url=cluster.endpoint,
            ),
            'systemctl start awslogsd',
        )

        ec2.Instance(
            self, 'Instance',
            role=role,
            vpc=vpc,
            security_group=sg,
            user_data=user_data,
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


class NeptuneCluster(core.Construct):

    def __init__(
            self, scope: core.Construct, id: str,
            vpc: ec2.IVpc, db_instance_class: str,
            **kwargs) -> None:
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

        subnet_group = neptune.CfnDBSubnetGroup(
            self, 'SubnetGroup',
            db_subnet_group_name='{}-subnet-group'.format(stack.stack_name.lower()),
            db_subnet_group_description='Private subnets',
            subnet_ids=[subnet.subnet_id for subnet in vpc.private_subnets]
        )

        cluster = neptune.CfnDBCluster(
            self, 'Cluster',
            db_subnet_group_name=subnet_group.ref,
            vpc_security_group_ids=[sg.security_group_id],
            associated_roles=[
                {
                    'roleArn': role.role_arn
                }
            ]
        )

        neptune.CfnDBInstance(
            self, 'Instance',
            db_cluster_identifier=cluster.ref,
            db_instance_class=db_instance_class,
        )

        self.endpoint = cluster.attr_endpoint
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
            db_instance_class='db.r5.large',
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
