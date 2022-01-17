#!/usr/bin/env python3
import os
from constructs import Construct
from aws_cdk import (
    App,
    Stack,
    SecretValue,
    CfnOutput,
    aws_iam as iam,
    aws_s3_assets as assets,
)


class PermissionBoundaryDemoStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        cfn_role = iam.Role(self, 'CloudFormationRole',
            assumed_by=iam.ServicePrincipal('cloudformation.amazonaws.com'),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name('AmazonEC2FullAccess'),
                iam.ManagedPolicy.from_aws_managed_policy_name('IAMFullAccess'),
            ]
        )

        alice = iam.User(self, 'Alice',
            user_name='alice',
            password=SecretValue.ssm_secure(
                parameter_name='/demo/permission-boundary/password',
                version='2',
            ),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name('AmazonEC2ReadOnlyAccess'),
                iam.ManagedPolicy.from_aws_managed_policy_name('AWSCloudFormationFullAccess'),
            ],
        )
        alice.add_to_principal_policy(
            iam.PolicyStatement(
                actions=['iam:PassRole'],
                resources=[cfn_role.role_arn],
            )
        )
        alice.add_to_principal_policy(
            iam.PolicyStatement(
                actions=['iam:ListRoles'],
                resources=['*'],
            )
        )

        template = assets.Asset(self, 'Template',
            path='./files/template.yml',
            readers=[alice, cfn_role],
        )

        CfnOutput(self, 'TemplateUrl', value=template.http_url)


app = App()
PermissionBoundaryDemoStack(app, 'PermissionBoundaryDemo')
app.synth()
