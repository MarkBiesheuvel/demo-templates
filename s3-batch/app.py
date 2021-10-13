#!/usr/bin/env python3
from aws_cdk import (
    core,
    aws_iam,
    aws_lambda,
    aws_s3
)


class S3BatchStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        bucket = aws_s3.Bucket(self, 'Bucket')

        batch_role = aws_iam.Role(
            self, 'BatchRole',
            assumed_by=aws_iam.ServicePrincipal('batchoperations.s3.amazonaws.com'),
        )
        bucket.grant_read_write(batch_role)

        function_role = aws_iam.Role(
            self, 'LambdaRole',
            assumed_by=aws_iam.ServicePrincipal('lambda.amazonaws.com'),
        )
        function_role.add_to_policy(
            aws_iam.PolicyStatement(
                effect=aws_iam.Effect.ALLOW,
                resources=[batch_role.role_arn],
                actions=['iam:PassRole']
            )
        )
        function_role.add_to_policy(
            aws_iam.PolicyStatement(
                effect=aws_iam.Effect.ALLOW,
                resources=['*'],
                actions=['s3:CreateJob']
            )
        )
        bucket.grant_read_write(function_role)

        function = aws_lambda.Function(
            self, 'Function',
            runtime=aws_lambda.Runtime.PYTHON_3_8,
            code=aws_lambda.Code.from_asset('lambda'),
            handler='index.handler',
            role=function_role,
            environment={
                'ACCOUNT_ID': self.account,
                'ROLE_ARN': batch_role.role_arn,
                'BUCKET_NAME': bucket.bucket_name
            }
        )


app = core.App()
S3BatchStack(app, 'S3BatchDemo')
app.synth()
