# Multi-AZ VPC with public and private subnets

This is a typical VPC network configuration with both public and private subnets.

There is a NAT gateway in each Availability Zone for fault tolerance. If there is an outage in one AZ, this won't affect the other AZs.

You can deploy this stack by uploading it in the AWS Management Console or by running the following command on the CLI:

```sh
aws cloudformation create-stack --stack-name network --template-body file://multi-az-public-private-vpc/multi-az-public-private-vpc.yml
```
