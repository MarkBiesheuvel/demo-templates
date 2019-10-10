# Load Balanced Web App

This demo shows a web application which is load balanced across multiple instance and thus multiple availability zones.

To run this demo you will need public and private subnets in multiple availability zones. For example, using the [Multi-AZ VPC with public and private subnets](multi-az-public-private-vpc) demo.

When the web application is running you can navigate to the load balancer DNS name to show different instances responding to the requests.

You can terminate an instance or use Session Manager to stop `httpd` in order to demonstrate the process of the health check failing. Auto Scaling will then terminate the instance and start a new one.
