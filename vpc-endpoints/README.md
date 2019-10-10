# VPC endpoints

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
