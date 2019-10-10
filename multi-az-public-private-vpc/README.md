# Multi-AZ VPC with public and private subnets

This is a typical configuration with public and private subnets.

There is a NAT gateway in each Availability Zone for fault tolerance. If there is an outage in the AZ with the NAT gateway, it won't affect the other AZs.
