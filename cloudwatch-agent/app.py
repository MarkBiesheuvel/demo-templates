#!/user/bin/env python3
from aws_cdk import (
    core,
    aws_autoscaling as autoscaling,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_lambda as lambda_,
    aws_logs as logs,
    aws_logs_destinations as logs_destinations,
    aws_s3_assets as s3_assets,
)


class CloudwatchAgentStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # IAM resources

        function_role = iam.Role(
            self, 'LambdaRole',
            assumed_by=iam.ServicePrincipal('lambda.amazonaws.com'),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AWSLambdaBasicExecutionRole'),
            ],
        )
        function_role.add_to_policy(
            iam.PolicyStatement(
                actions=['ec2:TerminateInstances'],
                resources=['*'],
            )
        )

        instance_role = iam.Role(
            self, 'Ec2Role',
            assumed_by=iam.ServicePrincipal('ec2.amazonaws.com'),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name('AmazonSSMManagedInstanceCore'),
                iam.ManagedPolicy.from_aws_managed_policy_name('CloudWatchAgentAdminPolicy'),
            ],
        )

        # Lambda resources

        function = lambda_.Function(
            self, 'Shutdown',
            runtime=lambda_.Runtime.PYTHON_3_7,  # Current version on my machines
            code=lambda_.Code.from_asset('files/shutdown'),
            handler='index.handler',
            role=function_role,
        )

        # Log resources

        awslogs_config = s3_assets.Asset(
            self, 'AwslogsConfig',
            path='./files/awslogs.conf',
            readers=[instance_role],
        )

        log_group = logs.LogGroup(
            self, 'LogSecure',
            removal_policy=core.RemovalPolicy.DESTROY,
        )

        logs.SubscriptionFilter(
            self, 'SshdSession',
            log_group=log_group,
            filter_pattern=logs.FilterPattern.all_terms('sshd', 'session opened'),
            destination=logs_destinations.LambdaDestination(function)
        )

        ## EC2 resources

        vpc = ec2.Vpc(
            self, 'Vpc',
            cidr='10.0.0.0/24',
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name='Public',
                    subnet_type=ec2.SubnetType.PUBLIC,
                )
            ],
        )

        key_pair = core.CfnParameter(
            self, 'KeyPair',
            type='AWS::EC2::KeyPair::KeyName',
        )

        # https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/EC2NewInstanceCWL.html
        user_data = ec2.UserData.for_linux()
        user_data.add_commands(
            'yum update -y',
            'yum install -y awslogs',
            'aws s3 cp s3://{bucket}/{key} /etc/awslogs/awslogs.conf'.format(
                bucket=awslogs_config.s3_bucket_name,
                key=awslogs_config.s3_object_key,
            ),
            'sed -i "s/LOG_GROUP_NAME/{log_group_name}/g" /etc/awslogs/awslogs.conf'.format(
                log_group_name=log_group.log_group_name,
            ),
            'sed -i "s/us-east-1/{region}/g" /etc/awslogs/awscli.conf'.format(
                region=self.region,
            ),
            'systemctl start awslogsd',
        )

        # Using an autoscaling group to utilize the rolling update
        asg = autoscaling.AutoScalingGroup(
            self, 'Instance',
            role=instance_role,
            vpc=vpc,
            user_data=user_data,
            key_name=key_pair.value_as_string,
            instance_type=ec2.InstanceType.of(
                instance_class=ec2.InstanceClass.BURSTABLE3_AMD,
                instance_size=ec2.InstanceSize.NANO,
            ),
            machine_image=ec2.AmazonLinuxImage(
              generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
              edition=ec2.AmazonLinuxEdition.STANDARD,
            ),
            min_capacity=3,
            max_capacity=3,
            update_type=autoscaling.UpdateType.ROLLING_UPDATE,
            rolling_update_configuration=autoscaling.RollingUpdateConfiguration(
                max_batch_size=3,
            )
        )

        asg.connections.allow_from_any_ipv4(ec2.Port.tcp(22))


app = core.App()
CloudwatchAgentStack(app, 'CloudwatchAgentDemo')
app.synth()

# Example:
# cdk deploy --parameters KeyPair="Ubuntu @ Desktop"
