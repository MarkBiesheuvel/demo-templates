#!/user/bin/env python3
from aws_cdk import (core,
    aws_ec2,
    aws_iam,
)

USER_DATA = '''#!/bin/sh
yum update -y
yum install -y httpd
availability_zone=`curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone`
instance_id=`curl -s http://169.254.169.254/latest/meta-data/instance-id`
echo "<html><body><h1>$instance_id</h1><p>$availability_zone</p></body></html>" > /var/www/html/index.html
service httpd start
''' # New line is important


class TransitStack(core.Stack):

    def __init__(self, scope: core.Construct, id:  list, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        tg = aws_ec2.CfnTransitGateway(self, 'TransitGateway',
            auto_accept_shared_attachments='enable',
            default_route_table_association='enable',
            default_route_table_propagation='enable',
            dns_support='enable',
        )

        core.CfnOutput(self, 'Export',
            value=tg.ref,
            export_name='TransitGatewayId'
        )


class IdentityStack(core.Stack):

    def __init__(self, scope: core.Construct, id:  list, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        role = aws_iam.Role(self, 'Ec2SsmRole',
            assumed_by=aws_iam.ServicePrincipal('ec2.amazonaws.com'),
            managed_policies=[
                aws_iam.ManagedPolicy.from_aws_managed_policy_name('AmazonSSMManagedInstanceCore')
            ],
        )

        profile = aws_iam.CfnInstanceProfile(self, 'Ec2SsmProfile',
            roles=[role.role_name],
        )

        core.CfnOutput(self, 'Export',
            value=profile.ref,
            export_name='InstanceProfileName'
        )


class VpcStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str,
            cidr: str,
            transit_stack: TransitStack,
            identity_stack: IdentityStack,
            **kwargs
    ) -> None:

        super().__init__(scope, id, **kwargs)

        vpc = aws_ec2.Vpc(self, 'Vpc',
            cidr=cidr,
            max_azs=3,
            subnet_configuration=[
                {
                    'cidrMask': 24,
                    'name': 'Private',
                    'subnetType': aws_ec2.SubnetType.ISOLATED,
                    #TODO: can't install httpd without internet connection
                },
            ],
        )

        instance_sg = aws_ec2.SecurityGroup(self, 'InstanceSecurityGroup',
            vpc=vpc,
        )
        instance_sg.add_ingress_rule(
            aws_ec2.Peer.ipv4('10.0.0.0/8'),
            aws_ec2.Port.tcp(80)
        )

        vpce_sg = aws_ec2.SecurityGroup(self, 'VpcEndpointSecurityGroup',
            vpc=vpc,
        )
        vpce_sg.add_ingress_rule(
            instance_sg,
            aws_ec2.Port.all_traffic()
        )

        ssm_endpoint = vpc.add_interface_endpoint('Ssm',
            service=aws_ec2.InterfaceVpcEndpointAwsService('ssm'),
            security_groups=[vpce_sg],
        )
        ssmmessages_endpoint = vpc.add_interface_endpoint('SsmMessages',
            service=aws_ec2.InterfaceVpcEndpointAwsService('ssmmessages'),
            security_groups=[vpce_sg],
        )
        ec2messages_endpoint = vpc.add_interface_endpoint('Ec2Messages',
            service=aws_ec2.InterfaceVpcEndpointAwsService('ec2messages'),
            security_groups=[vpce_sg],
        )

        if identity_stack is not None:
            self.add_dependency(identity_stack)

            ## Figure out why this class is not working
            # aws_ec2.Instance(self, 'Instance',
            #     vpc=vpc.vpc_id,
            #     vpc_subnets=vpc.isolated_subnets,
            #     machine_image=aws_ec2.AmazonLinuxImage(),
            #     instance_type=aws_ec2.InstanceType('t3.nano'),
            # )

            instance = aws_ec2.CfnInstance(self, 'Instance',
                subnet_id=vpc.isolated_subnets[0].subnet_id,
                image_id=aws_ec2.AmazonLinuxImage().get_image(self).image_id,
                security_group_ids=[instance_sg.security_group_id],
                instance_type='t3a.nano',
                iam_instance_profile=core.Fn.import_value('InstanceProfileName'),
                tags=[
                    core.CfnTag(key='Name', value='{}/Instance'.format(id)),
                ],
                user_data=core.Fn.base64(USER_DATA),
            )

            instance.node.add_dependency(ssm_endpoint)
            instance.node.add_dependency(ssmmessages_endpoint)
            instance.node.add_dependency(ec2messages_endpoint)

        if transit_stack is not None:
            self.add_dependency(transit_stack)

            attach = aws_ec2.CfnTransitGatewayAttachment(self, 'TransitGatewayAttachment',
                transit_gateway_id=core.Fn.import_value('TransitGatewayId'),
                vpc_id=vpc.vpc_id,
                subnet_ids=[
                    subnet.subnet_id
                    for subnet in vpc.isolated_subnets
                ],
            )

            for i, subnet in enumerate(vpc.isolated_subnets):
                aws_ec2.CfnRoute(self, 'TransitGatewayRoute{}'.format(i),
                    route_table_id=subnet.route_table.route_table_id,
                    transit_gateway_id =core.Fn.import_value('TransitGatewayId'),
                    destination_cidr_block='10.0.0.0/8'
                )


# Use the command `cdk deploy "*"` to deploy all stacks
app = core.App()

transit_stack = TransitStack(app, 'TransitGateway')
identity_stack = IdentityStack(app, 'Identity')

VpcStack(app, 'Network0', cidr='10.0.0.0/16', identity_stack=identity_stack, transit_stack=transit_stack)
VpcStack(app, 'Network1', cidr='10.1.0.0/16', identity_stack=identity_stack, transit_stack=transit_stack)
VpcStack(app, 'Network2', cidr='10.2.0.0/16', identity_stack=identity_stack, transit_stack=transit_stack)

VpcStack(app, 'Network9', cidr='10.9.0.0/16', identity_stack=identity_stack, transit_stack=None)


app.synth()
