#!/usr/bin/env python3
from os import environ
from aws_cdk import (
    core,
    aws_certificatemanager as acm,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_route53 as route53,
    aws_s3_assets as s3_assets,
)


class NitroEnclavesStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        domain_name = self.node.try_get_context('domain_name')

        subdomain = 'enclave.{}'.format(domain_name)

        zone = route53.HostedZone.from_lookup(
            self, 'Zone',
            domain_name=domain_name,
        )

        certificate = acm.DnsValidatedCertificate(
            self, 'Certificate',
            domain_name=subdomain,
            hosted_zone=zone,
        )

        vpc = ec2.Vpc(
            self, 'Vpc',
            cidr='10.11.12.0/24',
            max_azs=2,
            # Only need public IPs, so no need for private subnets
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name='public',
                    subnet_type=ec2.SubnetType.PUBLIC
                )
            ]
        )

        role = iam.Role(
            self, 'Ec2SsmRole',
            assumed_by=iam.ServicePrincipal('ec2.amazonaws.com'),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name('AmazonSSMManagedInstanceCore')
            ],
        )

        role.add_to_policy(
            iam.PolicyStatement(
                actions=['ec2:AssociateEnclaveCertificateIamRole'],
                resources=[
                    certificate.certificate_arn,
                    role.role_arn,
                ],
            )
        )

        role.add_to_policy(
            iam.PolicyStatement(
                actions=['s3:GetObject'],
                resources=['arn:aws:s3:::aws-ec2-enclave-certificate-*/*'],
            )
        )

        role.add_to_policy(
            iam.PolicyStatement(
                actions=['kms:Decrypt'],
                resources=['arn:aws:kms:*:*:key/*'],
            )
        )

        role.add_to_policy(
            iam.PolicyStatement(
                actions=['iam:GetRole'],
                resources=[role.role_arn],
            )
        )

        nginx_config = s3_assets.Asset(
            self, 'NginxConfig',
            path='./files/nginx.conf',
            readers=[role],
        )

        enclave_config = s3_assets.Asset(
            self, 'EncalveConfig',
            path='./files/acm.yaml',
            readers=[role],
        )

        # Source: https://docs.aws.amazon.com/enclaves/latest/user/nitro-enclave-refapp.html
        user_data = ec2.UserData.for_linux()
        user_data.add_commands(
            'curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"',
            'unzip awscliv2.zip',
            './aws/install',
            '/usr/local/bin/aws ec2 associate-enclave-certificate-iam-role --certificate-arn {certificate_arn} --role-arn {role_arn} --region {region}'.format(
                certificate_arn=certificate.certificate_arn,
                role_arn=role.role_arn,
                region=self.region,
            ),
            'aws s3 cp s3://{bucket}/{key} /etc/nginx/nginx.conf'.format(
                bucket=nginx_config.s3_bucket_name,
                key=nginx_config.s3_object_key,
            ),
            'sed -i "s+DOMAIN_NAME+{domain_name}+g" /etc/nginx/nginx.conf'.format(
                domain_name=subdomain,
            ),
            'aws s3 cp s3://{bucket}/{key} /etc/nitro_enclaves/acm.yaml'.format(
                bucket=enclave_config.s3_bucket_name,
                key=enclave_config.s3_object_key,
            ),
            'sed -i "s+CERTIFICATE_ARN+{certificate_arn}+g" /etc/nitro_enclaves/acm.yaml'.format(
                certificate_arn=certificate.certificate_arn,
            ),
            'systemctl start nitro-enclaves-acm.service',
            'systemctl enable nitro-enclaves-acm',
        )

        instance = ec2.Instance(
            self, 'Instance',
            role=role,
            vpc=vpc,
            user_data=user_data,
            # AWS Marketplace AMI: AWS Certificate Manager for Nitro Enclaves
            # Source: https://aws.amazon.com/marketplace/server/configuration?productId=3f5ee4f8-1439-4bce-ac57-e794a4ca82f9&ref_=psb_cfg_continue
            machine_image=ec2.MachineImage.lookup(
                name='ACM-For-Nitro-Enclaves-*',
                owners=['679593333241'],
            ),
            # Nitro Enclaves requires at least 4 vCPUs and does not run on Graviton
            instance_type=ec2.InstanceType.of(
                instance_class=ec2.InstanceClass.COMPUTE5_AMD,
                instance_size=ec2.InstanceSize.XLARGE,
            ),
        )

        # Unsupported property by CDK
        instance.instance.enclave_options = {'enabled': True}

        # Allow inbound HTTPS requests
        instance.connections.allow_from_any_ipv4(ec2.Port.tcp(443))

        # CDK route53 construct does not support EC2 instance as target
        route53.CfnRecordSet(
            self, 'DnsRecord',
            name=subdomain,
            type='A',
            ttl='60',
            resource_records=[instance.instance_public_ip],
            hosted_zone_id=zone.hosted_zone_id,
        )


app = core.App()
NitroEnclavesStack(
    app, 'EnclavesDemo',
    env=core.Environment(
        account=environ['CDK_DEFAULT_ACCOUNT'],
        region=environ['CDK_DEFAULT_REGION'],
    )
)
app.synth()
