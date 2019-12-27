yum update -y
yum install -y httpd
ip=$(curl -s http://169.254.169.254/latest/meta-data/local-ipv4)
echo "$ip" > /var/www/html/index.html
service httpd start
