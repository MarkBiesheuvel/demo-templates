#!/user/bin/env python3
from aws_cdk import (
    core,
    aws_ec2 as ec2,
    aws_iam as iam,
)


class NitroEnclavesStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        vpc = ec2.Vpc(
            self, 'Vpc',
            cidr='10.11.12.0/24',
            max_azs=2,
            nat_gateways=1,
        )

        role = iam.Role(
            self, 'Ec2SsmRole',
            assumed_by=iam.ServicePrincipal('ec2.amazonaws.com'),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name('AmazonSSMManagedInstanceCore')
            ],
        )

        instance = ec2.Instance(
            self, 'Instance',
            role=role,
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnets=vpc.public_subnets),
            instance_type=ec2.InstanceType.of(
                instance_class=ec2.InstanceClass.BURSTABLE4_GRAVITON,
                instance_size=ec2.InstanceSize.NANO,
            ),
            machine_image=ec2.AmazonLinuxImage(
                cpu_type=ec2.AmazonLinuxCpuType.ARM_64,
                generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
            ),
        )

        # TODO: Wait for EnclaveOptions to be supported by CDK
        # https://github.com/aws/aws-cdk/issues/12170
        instance.instance.hibernation_options = {'configured': True}

app = core.App()
NitroEnclavesStack(app, 'EnclavesDemo')
app.synth()
