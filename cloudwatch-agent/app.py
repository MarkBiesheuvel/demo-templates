#!/user/bin/env python3
from aws_cdk import (core,
    aws_autoscaling as autoscaling,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_s3_assets as s3_assets,
)


class CloudwatchAgentStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        vpc = ec2.Vpc(self, 'Vpc',
            cidr='10.0.0.0/24',
            max_azs=1,
        )

        role = iam.Role(self, 'Ec2Role',
            assumed_by=iam.ServicePrincipal('ec2.amazonaws.com'),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name('AmazonSSMManagedInstanceCore'),
                iam.ManagedPolicy.from_aws_managed_policy_name('CloudWatchAgentAdminPolicy'),
            ],
        )

        awslogs_config = s3_assets.Asset(self, 'AwslogsConfig',
            path='./files/awslogs.conf',
            readers=[role],
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
            'sed -i "s/us-east-1/{region}/g" /etc/awslogs/awscli.conf'.format(
                region=self.region,
            ),
            'systemctl start awslogsd',
        )

        # Using an autoscaling group to utilize the rolling update
        autoscaling.AutoScalingGroup(self, 'Instance',
            role=role,
            vpc=vpc,
            user_data=user_data,
            instance_type=ec2.InstanceType.of(
                instance_class=ec2.InstanceClass.BURSTABLE3_AMD,
                instance_size=ec2.InstanceSize.NANO,
            ),
            machine_image=ec2.AmazonLinuxImage(
              generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
              edition=ec2.AmazonLinuxEdition.STANDARD,
            ),
            min_capacity=1,
            max_capacity=1,
            update_type=autoscaling.UpdateType.ROLLING_UPDATE,
        )


app = core.App()
CloudwatchAgentStack(app, 'CloudwatchAgentDemo')
app.synth()
