# VPC endpoints

This is to demonstrate the use of VPC endpoints. This VPC does not contain any internet gateway or NAT gateway. It is still possible to use Session Manager to login to the machine since the Session Manager agent will make use of the VPC endpoints.

Run these commands to demonstrate the difference between an interface endpoint (like SSM), a gateway endpoint (like DynamoDB) and no endpoint (like KMS).

```sh
# Fetching current region
REGION=$(curl -s 169.254.169.254/latest/meta-data/placement/region)

# Connecting to DynamoDB via an VPC Gateway Endpoint
dig dynamodb.$REGION.amazonaws.com
aws dynamodb list-tables

# Other public APIs are unreachable
dig kms.$REGION.amazonaws.com
aws kms list-keys

# Connecting to Systems Manager via an VPC Interface Endpoint
dig ssm.$REGION.amazonaws.com
aws ssm list-commands
```
