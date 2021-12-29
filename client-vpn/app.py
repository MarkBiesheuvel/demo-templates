#!/usr/bin/env python3
import os
from constructs import Construct
from aws_cdk import (
    App,
    Environment,
    Stack,
    aws_ec2 as ec2,
)

server_certificate_arn = 'arn:aws:acm:eu-central-1:418155680583:certificate/7e649a4c-43a7-432f-8679-ee52bfb06b51'
client_certificate_arn = 'arn:aws:acm:eu-central-1:418155680583:certificate/b6fb3f8f-4d7e-4452-b5c2-1d6b1526f67c'

class ClientVpnStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        vpc = ec2.Vpc(
            self, 'Network',
            cidr='10.11.12.0/22',
            max_azs=3,
            nat_gateways=1,
        )

        vpc.add_client_vpn_endpoint(
            'VpnEndpoint',
            cidr='10.11.252.0/22', # Non-overlapping
            server_certificate_arn=server_certificate_arn,
            client_certificate_arn=client_certificate_arn,
        )


app = App()
ClientVpnStack(app, 'ClientVpn',
    env=Environment(
        account=os.getenv('CDK_DEFAULT_ACCOUNT'),
        region=os.getenv('CDK_DEFAULT_REGION')
    ),
)
app.synth()
