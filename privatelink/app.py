#!/user/bin/env python3
from aws_cdk import (core,
    aws_autoscaling as autoscaling,
    aws_ec2 as ec2,
    aws_elasticloadbalancingv2 as elbv2,
    aws_iam as iam,
)

try:
    with open('./userdata.sh', 'r') as file:
        raw_user_data = file.read()
except OSError:
    print('Failed to get UserData script')


class SourceVpc(core.Construct):

    def __init__(self, scope: core.Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        vpc = ec2.Vpc(self, 'Vpc',
            cidr='192.168.0.0/16',
            max_azs=2,
        )

        role = iam.Role(self, 'Ec2SsmRole',
            assumed_by=iam.ServicePrincipal('ec2.amazonaws.com'),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name('AmazonSSMManagedInstanceCore')
            ],
        )

        ec2.Instance(self, 'Instance',
            role=role,
            vpc=vpc,
            instance_type=ec2.InstanceType.of(
                instance_class=ec2.InstanceClass.BURSTABLE3_AMD,
                instance_size=ec2.InstanceSize.NANO,
            ),
            machine_image=ec2.AmazonLinuxImage(
              generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
            ),
        )

class DestinationVpc(core.Construct):

    def __init__(self, scope: core.Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        vpc = ec2.Vpc(self, 'Vpc',
            cidr='172.16.0.0/16',
            max_azs=2,
        )

        user_data = ec2.UserData.for_linux()
        user_data.add_commands(raw_user_data)

        role = iam.Role(self, 'Ec2SsmRole',
            assumed_by=iam.ServicePrincipal('ec2.amazonaws.com'),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name('AmazonSSMManagedInstanceCore')
            ],
        )

        asg = autoscaling.AutoScalingGroup(self, 'ASG',
            role=role,
            vpc=vpc,
            user_data=user_data,
            instance_type=ec2.InstanceType.of(
                instance_class=ec2.InstanceClass.BURSTABLE3_AMD,
                instance_size=ec2.InstanceSize.NANO,
            ),
            machine_image=ec2.AmazonLinuxImage(
              generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
            ),
            min_capacity=4,
            desired_capacity=4,
            max_capacity=4,
            update_type=autoscaling.UpdateType.ROLLING_UPDATE,
        )

        asg.connections.allow_from_any_ipv4(ec2.Port.tcp(80))

        # Only possible with ALB
        # asg.scale_on_request_count('AModestLoad',
        #   target_requests_per_second=1
        # )

        nlb = elbv2.NetworkLoadBalancer (self, 'NLB',
            vpc=vpc,
            internet_facing=False,
            cross_zone_enabled=True,
        )

        listener = nlb.add_listener('Listener',
            port=80,
        )

        target_group = listener.add_targets('Target',
            port=80,
            deregistration_delay=core.Duration.seconds(10),
            targets=[asg],
        )


class PrivateLinkStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        SourceVpc(self, 'Source')
        DestinationVpc(self, 'Destination')


app = core.App()
transit_stack = PrivateLinkStack(app, 'PrivateLinkDemo')
app.synth()
