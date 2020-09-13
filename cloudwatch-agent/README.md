# CloudWatch Logs Agent

This demo uses the AWS Cloud Development Kit (CDK) to build a VPC containing 3 EC2 instances.

These instances run a userdata script during start-up that will:

- Install the CloudWatch Logs Agent via Yum
- Download and modify the `awslogs.conf` file
- Modify the `awscli.conf` to point to the correct region
- Start the agent

Log streams for each instance can be found in a Log Group like `CloudwatchAgentDemo-LogSecure1BF86934-IUKA0JX7Y455`. (The last part of the name is random.)

To deploy tis template you need to have the CDK CLI installed and run the command `cdk deploy --parameters KeyPair="Ubuntu @ Desktop"`. (Replace "Ubuntu @ Desktop" with the name of your EC2 key pair.)

## CloudWatch Logs Subscription Filter

This demo also creates a Log Subscription Filter which looks for the words `sshd` and `session opened`. This happens when someone succesfully connects to an EC2 instance over SSH. When this activity is detected a Lambda Function will be invocated which automatically terminates the EC2 instance.

You can try this out by connecting to one of the instances public IPs:

```bash
ssh ec2-user@255.255.255.255 -i ~/.ssh/id_rsa
```
