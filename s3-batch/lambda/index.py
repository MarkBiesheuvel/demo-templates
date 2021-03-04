#!/usr/bin/env python3
import boto3
from os import environ

# Get settings from environment variables
ACCOUNT_ID = environ['ACCOUNT_ID']
ROLE_ARN = environ['ROLE_ARN']
BUCKET_NAME = environ['BUCKET_NAME']

# Initialize client here, for context re-use
s3_resource = boto3.resource('s3')
s3control_client = boto3.client('s3control')


# Get inventory of all objects in bucket
def generate_manifest_content(bucket_name):
    bucket = s3_resource.Bucket(bucket_name)

    return '\n'.join([
        '{bucket_name},{key}'.format(
            bucket_name=object.bucket_name,
            key=object.key
        )
        for object in bucket.objects.all()
    ])


# Uploads a file to S3 and returns the Object ARN & ETag
def upload_file(bucket_name, key, body):
    object = s3_resource.Object(bucket_name, key)

    object.put(
        Body=body
    )

    return object


# ...
def get_manifest_argument(bucket_name, file_name):
    # Generate and upload manifest file
    manifest_content = generate_manifest_content(bucket_name)
    manifest_object = upload_file(bucket_name, file_name, manifest_content)

    # Construct Object ARN
    object_arn = 'arn:aws:s3:::{bucket_name}/{key}'.format(
        bucket_name=manifest_object.bucket_name,
        key=manifest_object.key
    )

    # Remove the double quotes around the E-Tag
    e_tag = manifest_object.e_tag[1:-1]

    return {
        'Spec': {
            'Format': 'S3BatchOperations_CSV_20180820',
            'Fields': ['Bucket', 'Key']
        },
        'Location': {
            'ObjectArn': object_arn,
            'ETag': e_tag
        }
    }


# For this demo we won't need reports
def get_report_argument():
    return {
        'Enabled': False
    }


# Create S3 Batch operation
def create_tagging_job(account_id, role_arn, manifest, report):
    response = s3control_client.create_job(
        AccountId=account_id,
        RoleArn=role_arn,
        Report=report,
        Manifest=manifest,
        Priority=1,
        ConfirmationRequired=False,
        Description='Set tags on all objects',
        Operation={
            'S3PutObjectTagging': {
                'TagSet': [
                    {
                        'Key': 'Owner',
                        'Value': 'AWS Training and Certification'
                    },
                    {
                        'Key': 'Environment',
                        'Value': 'Production'
                    }
                ]
            }
        }
    )

    return response['JobId']


# Lambda handler / entry point
def handler(event, context):
    manifest = get_manifest_argument(BUCKET_NAME, 'manifest.csv')
    report = get_report_argument()

    job_id = create_tagging_job(ACCOUNT_ID, ROLE_ARN, manifest, report)

    print(job_id)


# If this file is invoked directly, run the handler function
# If not, then Lambda will invole it for us
if __name__ == '__main__':
    handler({}, None)
