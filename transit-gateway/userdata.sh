yum update -y
yum install -y httpd
instance_id=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)
echo "$instance_id" > /var/www/html/index.html
service httpd start
