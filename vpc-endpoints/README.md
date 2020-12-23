# VPC endpoints

This is to demonstrate the use of VPC endpoints. This VPC does not contain any internet gateway or NAT gateway. It is still possible to use Session Manager to login to the machine since the Session Manager agent will make use of the VPC endpoints.

Run these commands to demonstrate the difference between an interface endpoint (like SSM), a gateway endpoint (like S3) and no endpoint (like KMS).

```sh
dig ssm.eu-central-1.amazonaws.com
dig s3.eu-central-1.amazonaws.com
dig kms.eu-central-1.amazonaws.com

aws ssm list-commands
aws s3api list-buckets
aws kms list-keys
```

**Note:** replace `eu-central-1` by your current region name.
