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

    def __init__(self, scope: core.Construct, id: str, *,
            endpoint_service: ec2.CfnVPCEndpoint, **kwargs):
        super().__init__(scope, id, **kwargs)

        vpc = ec2.Vpc(self, 'Vpc',
            cidr='192.168.0.0/16',
            max_azs=2,
            nat_gateways=1,
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

        sg = ec2.SecurityGroup(self, 'EndpointSecurityGroup',
            vpc=vpc,
        )
        sg.add_ingress_rule(
            ec2.Peer.ipv4('0.0.0.0/0'),
            ec2.Port.tcp(80)
        )

        # ! Python substitution within CDK substitution within CloudFormation substitution !
        # First, python replace {endpoint_id} with the value of the logical_id property
        # The value of this property is like "${Token[PrivateLinkDemo...]}"
        # At `cdk synth` this will resolve to the logical ID in the output CloudFormation template
        # Lastly, CloudFormation will perform an Fn::Sub
        service_name = core.Fn.sub('com.amazonaws.vpce.${{AWS::Region}}.${{{endpoint_id}}}'.format(
            endpoint_id=endpoint_service.logical_id
        ))

        # TODO: replace by CDK construct when available
        endpoint = ec2.CfnVPCEndpoint(self, 'Endpoint',
            service_name=service_name,
            vpc_endpoint_type='Interface', # ec2.VpcEndpointType.INTERFACE
            vpc_id=vpc.vpc_id,
            security_group_ids=[
                sg.security_group_id,
            ],
            subnet_ids=[
                subnet.subnet_id
                for subnet in vpc.private_subnets
            ],
        )

        # TODO: make an output with a curl command
        # core.CfnOutput(self, 'Command',
        #     value=core.Fn.get_att(DnsEntries),
        # )


class DestinationVpc(core.Construct):

    def __init__(self, scope: core.Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        vpc = ec2.Vpc(self, 'Vpc',
            cidr='172.16.0.0/16',
            max_azs=2,
            nat_gateways=1,
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

        # TODO: replace by CDK construct when available
        service = ec2.CfnVPCEndpointService(self, 'Service',
            network_load_balancer_arns=[nlb.load_balancer_arn],
            acceptance_required=False,
        )
        self.endpoint_service = service


class PrivateLinkStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        destination = DestinationVpc(self, 'Destination')
        source = SourceVpc(self, 'Source', endpoint_service=destination.endpoint_service)


app = core.App()
transit_stack = PrivateLinkStack(app, 'PrivateLinkDemo')
app.synth()
