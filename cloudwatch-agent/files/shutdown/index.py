from boto3 import client
from base64 import b64decode
from gzip import GzipFile
from io import BytesIO
from json import loads as jsondecode

ec2 = client('ec2')


def gunzip(data):
    with GzipFile(fileobj=BytesIO(data), mode='rb') as gzip_file:
        return gzip_file.read().decode()


def handler(event, context):
    data = b64decode(event['awslogs']['data'])
    payload = jsondecode(gunzip(data))

    instance_id = payload['logStream']

    print('Terminating instance "{}"'.format(instance_id))

    ec2.terminate_instances(
        InstanceIds=[instance_id],
    )
