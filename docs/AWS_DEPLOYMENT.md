# AWS Deployment Guide: Video Ads API

This guide will walk you through deploying the Video Ads API on AWS using EC2, RDS, and other AWS services.

## Table of Contents
- [AWS Deployment Guide: Video Ads API](#aws-deployment-guide-video-ads-api)
  - [Table of Contents](#table-of-contents)
  - [Prerequisites](#prerequisites)
  - [AWS Account Setup](#aws-account-setup)
  - [EC2 Instance Setup](#ec2-instance-setup)
  - [Security Group Configuration](#security-group-configuration)
  - [Database Setup](#database-setup)
  - [Application Deployment](#application-deployment)
  - [Domain and SSL Setup](#domain-and-ssl-setup)
  - [Monitoring and Maintenance](#monitoring-and-maintenance)
  - [Maintenance Commands](#maintenance-commands)
  - [Security Best Practices](#security-best-practices)
  - [Cost Optimization](#cost-optimization)
  - [Troubleshooting](#troubleshooting)
  - [Need Help?](#need-help)

## Prerequisites

1. AWS Account
2. Domain Name (optional)
3. SSH Client
4. Basic knowledge of Linux commands

## AWS Account Setup

1. Create an AWS Account:
   - Go to https://aws.amazon.com/
   - Click "Create an AWS Account"
   - Follow the registration process

2. Create an IAM User:
   - Go to IAM Console
   - Create a new user with programmatic access
   - Attach the following policies:
     - AmazonEC2FullAccess
     - AmazonRDSFullAccess
     - AmazonRoute53FullAccess
   - Save the Access Key ID and Secret Access Key

## EC2 Instance Setup

1. Launch EC2 Instance:
   ```bash
   # Using AWS CLI
   aws ec2 run-instances \
     --image-id ami-0c55b159cbfafe1f0 \
     --count 1 \
     --instance-type t2.micro \
     --key-name your-key-pair \
     --security-group-ids sg-xxxxxxxx \
     --subnet-id subnet-xxxxxxxx
   ```

2. Connect to Instance:
   ```bash
   # Using SSH
   ssh -i your-key-pair.pem ubuntu@your-instance-public-ip
   ```

3. Update System:
   ```bash
   sudo apt update
   sudo apt upgrade -y
   ```

4. Install Required Software:
   ```bash
   sudo apt install -y python3-pip python3-venv nginx supervisor
   ```

## Security Group Configuration

1. Create Security Group:
   ```bash
   aws ec2 create-security-group \
     --group-name VideoAdsAPI-SG \
     --description "Security group for Video Ads API"
   ```

2. Add Inbound Rules:
   ```bash
   aws ec2 authorize-security-group-ingress \
     --group-name VideoAdsAPI-SG \
     --protocol tcp \
     --port 22 \
     --cidr 0.0.0.0/0

   aws ec2 authorize-security-group-ingress \
     --group-name VideoAdsAPI-SG \
     --protocol tcp \
     --port 80 \
     --cidr 0.0.0.0/0

   aws ec2 authorize-security-group-ingress \
     --group-name VideoAdsAPI-SG \
     --protocol tcp \
     --port 443 \
     --cidr 0.0.0.0/0
   ```

## Database Setup

1. Create RDS Instance:
   ```bash
   aws rds create-db-instance \
     --db-instance-identifier video-ads-db \
     --db-instance-class db.t2.micro \
     --engine postgres \
     --master-username admin \
     --master-user-password your-password \
     --allocated-storage 20 \
     --vpc-security-group-ids sg-xxxxxxxx
   ```

2. Configure Database:
   ```bash
   # Connect to RDS
   psql -h your-rds-endpoint -U admin -d postgres

   # Create database and user
   CREATE DATABASE video_ads;
   CREATE USER api_user WITH PASSWORD 'your-password';
   GRANT ALL PRIVILEGES ON DATABASE video_ads TO api_user;
   ```

## Application Deployment

1. Clone Repository:
   ```bash
   git clone https://github.com/your-repo/video-ads-api.git
   cd video-ads-api
   ```

2. Create Virtual Environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install Dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure Environment:
   ```bash
   # Create .env file
   cat > .env << EOL
   YOUTUBE_API_KEY=your_youtube_api_key
   JWT_SECRET_KEY=your_jwt_secret_key
   DATABASE_URL=postgresql://api_user:your-password@your-rds-endpoint:5432/video_ads
   EOL
   ```

5. Configure Nginx:
   ```bash
   sudo nano /etc/nginx/sites-available/video-ads-api

   # Add this configuration
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }

   # Enable site
   sudo ln -s /etc/nginx/sites-available/video-ads-api /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

6. Configure Supervisor:
   ```bash
   sudo nano /etc/supervisor/conf.d/video-ads-api.conf

   # Add this configuration
   [program:video-ads-api]
   command=/home/ubuntu/video-ads-api/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
   directory=/home/ubuntu/video-ads-api
   user=ubuntu
   autostart=true
   autorestart=true
   stderr_logfile=/var/log/video-ads-api.err.log
   stdout_logfile=/var/log/video-ads-api.out.log

   # Reload supervisor
   sudo supervisorctl reread
   sudo supervisorctl update
   ```

## Domain and SSL Setup

1. Create Route 53 Hosted Zone:
   ```bash
   aws route53 create-hosted-zone \
     --name your-domain.com \
     --caller-reference $(date +%s)
   ```

2. Update Name Servers:
   - Copy the name servers from Route 53
   - Update your domain registrar's name servers

3. Request SSL Certificate:
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d your-domain.com
   ```

## Monitoring and Maintenance

1. Set up CloudWatch:
   ```bash
   # Install CloudWatch agent
   sudo apt install -y amazon-cloudwatch-agent

   # Configure agent
   sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-config-wizard
   ```

2. Create Backup Script:
   ```bash
   # Create backup script
   cat > backup.sh << EOL
   #!/bin/bash
   TIMESTAMP=$(date +%Y%m%d_%H%M%S)
   pg_dump -h your-rds-endpoint -U api_user video_ads > backup_$TIMESTAMP.sql
   aws s3 cp backup_$TIMESTAMP.sql s3://your-backup-bucket/
   EOL

   # Make executable
   chmod +x backup.sh

   # Add to crontab
   (crontab -l 2>/dev/null; echo "0 0 * * * /path/to/backup.sh") | crontab -
   ```

3. Set up Auto-scaling:
   ```bash
   # Create launch template
   aws ec2 create-launch-template \
     --launch-template-name VideoAdsAPI-Template \
     --version-description "Initial version" \
     --launch-template-data '{"ImageId":"ami-0c55b159cbfafe1f0","InstanceType":"t2.micro"}'

   # Create auto-scaling group
   aws autoscaling create-auto-scaling-group \
     --auto-scaling-group-name VideoAdsAPI-ASG \
     --launch-template LaunchTemplateName=VideoAdsAPI-Template \
     --min-size 1 \
     --max-size 3 \
     --desired-capacity 1 \
     --vpc-zone-identifier subnet-xxxxxxxx
   ```

## Maintenance Commands

1. Check Application Status:
   ```bash
   sudo supervisorctl status video-ads-api
   ```

2. Restart Application:
   ```bash
   sudo supervisorctl restart video-ads-api
   ```

3. Check Logs:
   ```bash
   tail -f /var/log/video-ads-api.err.log
   tail -f /var/log/video-ads-api.out.log
   ```

4. Update Application:
   ```bash
   cd /home/ubuntu/video-ads-api
   git pull
   source venv/bin/activate
   pip install -r requirements.txt
   sudo supervisorctl restart video-ads-api
   ```

## Security Best Practices

1. Regular Updates:
   ```bash
   sudo apt update
   sudo apt upgrade -y
   ```

2. Firewall Rules:
   ```bash
   sudo ufw allow 22
   sudo ufw allow 80
   sudo ufw allow 443
   sudo ufw enable
   ```

3. SSL Renewal:
   ```bash
   sudo certbot renew --dry-run
   ```

## Cost Optimization

1. Use Spot Instances for non-critical workloads
2. Implement auto-scaling based on demand
3. Use AWS Free Tier where possible
4. Monitor and optimize RDS instance size
5. Implement caching where appropriate

## Troubleshooting

1. Check Nginx Status:
   ```bash
   sudo systemctl status nginx
   ```

2. Check Supervisor Status:
   ```bash
   sudo supervisorctl status
   ```

3. Check Application Logs:
   ```bash
   sudo tail -f /var/log/video-ads-api.err.log
   ```

4. Check Database Connection:
   ```bash
   psql -h your-rds-endpoint -U api_user -d video_ads
   ```

## Need Help?

1. AWS Documentation: https://docs.aws.amazon.com/
2. AWS Support: https://aws.amazon.com/premiumsupport/
3. Stack Overflow: https://stackoverflow.com/questions/tagged/aws
4. GitHub Issues: https://github.com/your-repo/video-ads-api/issues 