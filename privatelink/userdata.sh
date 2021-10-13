yum update -y
yum install -y httpd
availability_zone=`curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone`
instance_id=`curl -s http://169.254.169.254/latest/meta-data/instance-id`
echo "<html><body><h1>$instance_id</h1><p>$availability_zone</p></body></html>" > /var/www/html/index.html
service httpd start
