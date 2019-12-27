#!/user/bin/env python3
from aws_cdk import (core,
    aws_ec2 as ec2,
    aws_iam as iam,
)

try:
    with open('./userdata.sh', 'r') as file:
        raw_user_data = file.read()
except OSError:
    print('Failed to get UserData script')


class TransitMemberVpc(core.Construct):

    def __init__(self, scope: core.Construct, id: str, *,
            cidr_range: str,
            transit_gateway: ec2.CfnTransitGateway,
            role: iam.IRole,
            **kwargs):
        super().__init__(scope, id, **kwargs)

        vpc = ec2.Vpc(self, 'Vpc',
            cidr=cidr_range,
            max_azs=2,
        )

        sg = ec2.SecurityGroup(self, 'InstanceSecurityGroup',
            vpc=vpc,
        )
        sg.add_ingress_rule(
            ec2.Peer.ipv4('10.0.0.0/8'),
            ec2.Port.tcp(80)
        )

        user_data = ec2.UserData.for_linux()
        user_data.add_commands(raw_user_data)

        ec2.Instance(self, 'Instance',
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

        # TODO: replace by CDK construct when available
        attachment = ec2.CfnTransitGatewayAttachment(self, 'TransitGatewayAttachment',
            transit_gateway_id=transit_gateway.ref,
            vpc_id=vpc.vpc_id,
            subnet_ids=[
                subnet.subnet_id
                for subnet in vpc.private_subnets
            ],
        )

        for i, subnet in enumerate(vpc.private_subnets):
            # TODO: replace by CDK construct when available
            ec2.CfnRoute(self, 'TransitGatewayRoute{}'.format(i),
                route_table_id=subnet.route_table.route_table_id,
                transit_gateway_id=transit_gateway.ref,
                destination_cidr_block='10.0.0.0/8'
            )


class TransitGatewayStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, cidr_ranges: list, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # TODO: replace by CDK construct when available
        tg = ec2.CfnTransitGateway(self, 'TransitGateway',
            auto_accept_shared_attachments='enable',
            default_route_table_association='enable',
            default_route_table_propagation='enable',
            dns_support='enable',
        )

        role = iam.Role(self, 'Ec2SsmRole',
            assumed_by=iam.ServicePrincipal('ec2.amazonaws.com'),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name('AmazonSSMManagedInstanceCore')
            ],
        )

        member_vpcs = [
            TransitMemberVpc(self, 'Member{}'.format(i + 1),
                cidr_range=cidr_range,
                transit_gateway=tg,
                role=role,
            )
            for i, cidr_range in enumerate(cidr_ranges)
        ]


app = core.App()

transit_stack = TransitGatewayStack(app, 'TransitGatewayDemo', cidr_ranges=[
    '10.1.0.0/16',
    '10.2.0.0/16',
    '10.3.0.0/16',
    '10.4.0.0/16',
])


app.synth()
