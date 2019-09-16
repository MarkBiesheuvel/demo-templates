Demo: VPC configurations
==

The goal of this project is to be able to quickly create different types of VPCs for the purpose of demos.

Multi-AZ VPC with public and private subnets
--

This is a typical configuration with public and private subnets.

There is a NAT gateway in each Availability Zone for fault tolerance. If there is an outage in the AZ with the NAT gateway, it won't affect the other AZs.

VPC endpoints
--

This is to demonstrate the use of VPC endpoints. This VPC does not contain any internet gateway or nat gateway. It is possible to use Session Manager to login to the machine as this makes use of the VPC endpoints.

Run commands such as these to demonstrate the difference between an interface endpoint (ssm), a gateway endpoint (s3) and no endpoint (kms).

```bash
dig ssm.eu-central-1.amazonaws.com
dig s3.eu-central-1.amazonaws.com
dig kms.eu-central-1.amazonaws.com

aws ssm list-commands
aws s3api list-buckets
aws kms list-keys
```

**Note:** replace `eu-central-1` by your current region name.
