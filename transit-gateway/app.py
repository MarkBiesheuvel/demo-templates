#!/user/bin/env python3
from aws_cdk import (core,
    aws_ec2
)


class VpcStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, cidr: str, tg_id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        vpc = aws_ec2.Vpc(self, 'Vpc',
            cidr=cidr,
            enable_dns_hostnames=True,
            enable_dns_support=True,
            max_azs=2,
            nat_gateways=2,
        )

        attach = aws_ec2.CfnTransitGatewayAttachment(self, 'TransitGatewayAttachment',
            transit_gateway_id=tg_id,
            vpc_id=vpc.vpc_id,
            subnet_ids=[
                subnet.subnet_id
                for subnet in vpc.private_subnets
            ],
        )


class TransitStack(core.Stack):

    def __init__(self, scope: core.Construct, id:  list, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        tg = aws_ec2.CfnTransitGateway(self, 'TransitGateway',
            auto_accept_shared_attachments='enable',
            default_route_table_association='enable',
            default_route_table_propagation='enable',
            dns_support='enable',
        )

# Use the command `cdk deploy "*"` to deploy all stacks
app = core.App()

TransitStack(app, 'TransitGateway')

tg_id = 'tgw-04975fc0d40f7a750' # TODO: figure out a good way to share this

VpcStack(app, 'Network1', cidr='10.1.0.0/16', tg_id=tg_id),
VpcStack(app, 'Network2', cidr='10.2.0.0/16', tg_id=tg_id),
VpcStack(app, 'Network3', cidr='10.3.0.0/16', tg_id=tg_id),
VpcStack(app, 'Network4', cidr='10.4.0.0/16', tg_id=tg_id),

app.synth()
