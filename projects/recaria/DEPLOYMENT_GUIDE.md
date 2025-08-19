# recaria.org Production Deployment Guide

**Version:** v047-beta  
**Target Platform:** Oracle Cloud Infrastructure  
**Last Updated:** June 24, 2025  
**Prepared by:** Unicorn Bodrum Technologies  

## Overview

This comprehensive deployment guide provides detailed instructions for deploying the recaria location-based gaming platform to production environment on Oracle Cloud Infrastructure. The guide covers all aspects of deployment including server preparation, application configuration, security setup, and operational procedures.

## Prerequisites

### System Requirements

**Minimum Server Specifications:**
- CPU: 2 vCPUs (ARM or x86_64)
- RAM: 4 GB
- Storage: 20 GB SSD
- Network: Public IP address with HTTP/HTTPS access
- Operating System: Ubuntu 22.04 LTS or newer

**Required Software:**
- Python 3.11 or newer
- Nginx web server
- UFW firewall
- Git version control
- SSL certificate (Let's Encrypt recommended)

### Oracle Cloud Configuration

**Security Groups:**
- Ingress Rule: TCP Port 22 (SSH) from your IP
- Ingress Rule: TCP Port 80 (HTTP) from 0.0.0.0/0
- Ingress Rule: TCP Port 443 (HTTPS) from 0.0.0.0/0

**Network Configuration:**
- Virtual Cloud Network (VCN) with public subnet
- Internet Gateway configured
- Route table with 0.0.0.0/0 -> Internet Gateway

## Step-by-Step Deployment

### Step 1: Server Preparation

Connect to your Oracle Cloud instance via SSH:

```bash
ssh -i your-private-key.pem ubuntu@your-server-ip
```

Update the system packages:

```bash
sudo apt update && sudo apt upgrade -y
```

Install required system packages:

```bash
sudo apt install -y nginx python3-pip python3-venv git ufw curl wget
```

### Step 2: Project Deployment

Clone or upload the recaria project to the server:

```bash
cd /home/ubuntu
# If using git:
git clone your-repository-url recaria
# Or upload the project files via SCP
```

Navigate to the project directory:

```bash
cd /home/ubuntu/recaria
```

Install Python dependencies:

```bash
pip3 install -r requirements.txt
```

### Step 3: Database Setup

Run Django migrations to set up the database:

```bash
cd recaria
python3.11 manage.py migrate
```

Collect static files:

```bash
python3.11 manage.py collectstatic --noinput
```

Create a Django superuser (optional):

```bash
python3.11 manage.py createsuperuser
```

### Step 4: Application Configuration

Test the application locally:

```bash
python3.11 manage.py check
```

Test Gunicorn configuration:

```bash
cd /home/ubuntu/recaria/recaria
gunicorn --config ../gunicorn.conf.py --check-config recaria_backend.wsgi:application
```

### Step 5: Nginx Configuration

Copy the Nginx configuration:

```bash
sudo cp /home/ubuntu/recaria/nginx_recaria.conf /etc/nginx/sites-available/recaria
```

Enable the site:

```bash
sudo ln -sf /etc/nginx/sites-available/recaria /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
```

Test Nginx configuration:

```bash
sudo nginx -t
```

### Step 6: SSL Certificate Setup

Install Certbot for Let's Encrypt:

```bash
sudo apt install -y certbot python3-certbot-nginx
```

Obtain SSL certificate (replace with your domain):

```bash
sudo certbot --nginx -d recaria.org -d www.recaria.org
```

Test SSL renewal:

```bash
sudo certbot renew --dry-run
```

### Step 7: Systemd Service Configuration

Copy the systemd service file:

```bash
sudo cp /home/ubuntu/recaria/recaria.service /etc/systemd/system/
```

Reload systemd and enable the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable recaria
```

### Step 8: Firewall Configuration

Configure UFW firewall:

```bash
sudo ufw --force enable
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw status
```

### Step 9: Service Startup

Start the recaria service:

```bash
sudo systemctl start recaria
```

Start Nginx:

```bash
sudo systemctl restart nginx
```

Check service status:

```bash
sudo systemctl status recaria
sudo systemctl status nginx
```

### Step 10: Deployment Verification

Test the health endpoint:

```bash
curl -I http://your-server-ip/api/health/
curl -I https://recaria.org/api/health/
```

Test the main application:

```bash
curl -I http://your-server-ip/
curl -I https://recaria.org/
```

## Automated Deployment

For automated deployment, use the provided deployment script:

```bash
cd /home/ubuntu/recaria
chmod +x deploy.sh
./deploy.sh
```

The script will automatically:
- Update system packages
- Install dependencies
- Configure services
- Set up firewall
- Start all services
- Verify deployment

## Post-Deployment Configuration

### DNS Configuration

Configure your domain DNS settings:

**A Record:** recaria.org -> your-server-ip  
**CNAME Record:** www.recaria.org -> recaria.org  

### Monitoring Setup

Monitor application logs:

```bash
# Application logs
sudo journalctl -u recaria -f

# Nginx logs
sudo tail -f /var/log/nginx/recaria_access.log
sudo tail -f /var/log/nginx/recaria_error.log

# Gunicorn logs
tail -f /home/ubuntu/recaria/logs/gunicorn_error.log
```

### Backup Configuration

Set up automated backups:

```bash
# Create backup script
cat > /home/ubuntu/backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/ubuntu/backups"
mkdir -p $BACKUP_DIR

# Backup database
cp /home/ubuntu/recaria/recaria/db.sqlite3 $BACKUP_DIR/db_$DATE.sqlite3

# Backup data files
tar -czf $BACKUP_DIR/data_$DATE.tar.gz /home/ubuntu/recaria/recaria/data/

# Backup logs
tar -czf $BACKUP_DIR/logs_$DATE.tar.gz /home/ubuntu/recaria/logs/

# Clean old backups (keep 7 days)
find $BACKUP_DIR -name "*.sqlite3" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
EOF

chmod +x /home/ubuntu/backup.sh

# Add to crontab for daily backups
(crontab -l 2>/dev/null; echo "0 2 * * * /home/ubuntu/backup.sh") | crontab -
```

## Maintenance Procedures

### Regular Updates

Update the application:

```bash
cd /home/ubuntu/recaria
git pull origin main  # If using git
sudo systemctl restart recaria
```

Update system packages:

```bash
sudo apt update && sudo apt upgrade -y
sudo systemctl restart nginx
```

### Service Management

Common service management commands:

```bash
# Start services
sudo systemctl start recaria
sudo systemctl start nginx

# Stop services
sudo systemctl stop recaria
sudo systemctl stop nginx

# Restart services
sudo systemctl restart recaria
sudo systemctl restart nginx

# Check status
sudo systemctl status recaria
sudo systemctl status nginx

# View logs
sudo journalctl -u recaria -n 50
sudo journalctl -u nginx -n 50
```

### Performance Monitoring

Monitor system resources:

```bash
# CPU and memory usage
htop

# Disk usage
df -h

# Network connections
sudo ss -tlnp

# Process monitoring
ps aux | grep -E 'gunicorn|nginx'
```

### SSL Certificate Renewal

SSL certificates are automatically renewed by Certbot. To manually renew:

```bash
sudo certbot renew
sudo systemctl reload nginx
```

## Troubleshooting

### Common Issues

**Service won't start:**
```bash
# Check service status
sudo systemctl status recaria

# Check logs
sudo journalctl -u recaria -n 50

# Check configuration
cd /home/ubuntu/recaria/recaria
python3.11 manage.py check
```

**Nginx configuration errors:**
```bash
# Test configuration
sudo nginx -t

# Check error logs
sudo tail -f /var/log/nginx/error.log
```

**SSL certificate issues:**
```bash
# Check certificate status
sudo certbot certificates

# Renew certificates
sudo certbot renew --force-renewal
```

**Database issues:**
```bash
# Run migrations
cd /home/ubuntu/recaria/recaria
python3.11 manage.py migrate

# Check database permissions
ls -la db.sqlite3
```

### Emergency Recovery

If the site is completely down:

```bash
# Stop all services
sudo systemctl stop recaria nginx

# Check for port conflicts
sudo ss -tlnp | grep -E ':80|:443|:8000'

# Kill conflicting processes
sudo pkill -f gunicorn
sudo pkill -f nginx

# Restart services
sudo systemctl start nginx
sudo systemctl start recaria

# Verify status
sudo systemctl status nginx recaria
```

## Security Considerations

### Regular Security Updates

Keep the system updated:

```bash
# Weekly security updates
sudo apt update && sudo apt upgrade -y

# Monitor security advisories
sudo apt list --upgradable
```

### Log Monitoring

Monitor access logs for suspicious activity:

```bash
# Monitor failed login attempts
sudo grep "Failed password" /var/log/auth.log

# Monitor Nginx access logs
sudo tail -f /var/log/nginx/recaria_access.log | grep -E "40[0-9]|50[0-9]"
```

### Backup Verification

Regularly test backup restoration:

```bash
# Test database backup
cp /home/ubuntu/backups/db_latest.sqlite3 /tmp/test_db.sqlite3

# Test data backup
tar -tzf /home/ubuntu/backups/data_latest.tar.gz
```

## Performance Optimization

### Gunicorn Tuning

Adjust worker processes based on server resources:

```bash
# Edit gunicorn configuration
nano /home/ubuntu/recaria/gunicorn.conf.py

# Restart service
sudo systemctl restart recaria
```

### Nginx Optimization

Enable additional performance features:

```bash
# Edit Nginx configuration
sudo nano /etc/nginx/sites-available/recaria

# Test and reload
sudo nginx -t && sudo systemctl reload nginx
```

### Database Optimization

Regular database maintenance:

```bash
cd /home/ubuntu/recaria/recaria

# Vacuum database
echo "VACUUM;" | python3.11 manage.py dbshell

# Analyze database
echo "ANALYZE;" | python3.11 manage.py dbshell
```

## Support and Maintenance

### Contact Information

**Technical Support:**
- Developer: Unicorn Bodrum Technologies
- Project: recaria v047-beta
- Documentation: Available in project repository

### Maintenance Schedule

**Daily:**
- Monitor service status
- Check error logs
- Verify backup completion

**Weekly:**
- Update system packages
- Review access logs
- Performance monitoring

**Monthly:**
- SSL certificate verification
- Security audit
- Backup restoration testing

### Version Updates

When updating to new versions:

1. Create full backup
2. Test in staging environment
3. Update during maintenance window
4. Verify all functionality
5. Monitor for issues

This deployment guide provides comprehensive instructions for successful production deployment of the recaria platform. Follow all steps carefully and maintain regular monitoring and maintenance procedures for optimal performance and security.

