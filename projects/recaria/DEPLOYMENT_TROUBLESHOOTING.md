# recaria Deployment Troubleshooting Guide

## Common Issues and Solutions

### 1. recaria.org Access Issues

**Problem**: Cannot access recaria.org website
**Possible Causes**:
- DNS not configured properly
- Oracle Cloud security groups blocking traffic
- Nginx not running or misconfigured
- SSL certificate issues

**Solutions**:
```bash
# Check if Nginx is running
sudo systemctl status nginx

# Check Nginx configuration
sudo nginx -t

# Check if ports are open
sudo ufw status
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :443

# Check DNS resolution
nslookup recaria.org
dig recaria.org

# Test local access
curl -I http://localhost
curl -I http://your-server-ip
```

### 2. Nginx Configuration Issues

**Problem**: Nginx fails to start or shows errors
**Solutions**:
```bash
# Test Nginx configuration
sudo nginx -t

# Check Nginx error logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/recaria_error.log

# Restart Nginx
sudo systemctl restart nginx

# Check if Nginx is listening on correct ports
sudo ss -tlnp | grep nginx
```

### 3. Gunicorn Service Issues

**Problem**: recaria service fails to start
**Solutions**:
```bash
# Check service status
sudo systemctl status recaria

# View service logs
sudo journalctl -u recaria -f

# Check Gunicorn logs
tail -f /home/ubuntu/recaria/logs/gunicorn_error.log

# Test Gunicorn manually
cd /home/ubuntu/recaria/recaria
gunicorn --config /home/ubuntu/recaria/gunicorn.conf.py recaria_backend.wsgi:application

# Restart service
sudo systemctl restart recaria
```

### 4. Oracle Cloud Security Groups

**Problem**: Traffic blocked by Oracle Cloud firewall
**Solutions**:
1. Log into Oracle Cloud Console
2. Go to Networking > Virtual Cloud Networks
3. Select your VCN > Security Lists
4. Add ingress rules:
   - Source: 0.0.0.0/0
   - Protocol: TCP
   - Port: 80, 443
   - Description: HTTP/HTTPS for recaria

### 5. UFW Firewall Issues

**Problem**: Local firewall blocking connections
**Solutions**:
```bash
# Check UFW status
sudo ufw status verbose

# Allow HTTP/HTTPS
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 'Nginx Full'

# Reset UFW if needed
sudo ufw --force reset
sudo ufw enable
```

### 6. SSL Certificate Issues

**Problem**: HTTPS not working
**Solutions**:
```bash
# Install Let's Encrypt (Certbot)
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d recaria.org -d www.recaria.org

# Test SSL renewal
sudo certbot renew --dry-run

# Update Nginx config with SSL paths
sudo nano /etc/nginx/sites-available/recaria
```

### 7. Static Files Not Loading

**Problem**: CSS, JS, images not loading
**Solutions**:
```bash
# Collect static files
cd /home/ubuntu/recaria/recaria
python3.11 manage.py collectstatic --noinput

# Check static files directory
ls -la /home/ubuntu/recaria/static/
ls -la /home/ubuntu/recaria/recaria/staticfiles/

# Check Nginx static file configuration
sudo nginx -t
```

### 8. Database Issues

**Problem**: Database errors or migrations needed
**Solutions**:
```bash
# Run migrations
cd /home/ubuntu/recaria/recaria
python3.11 manage.py migrate

# Check database file permissions
ls -la db.sqlite3

# Create superuser if needed
python3.11 manage.py createsuperuser
```

### 9. Python Dependencies Issues

**Problem**: Import errors or missing packages
**Solutions**:
```bash
# Install requirements
cd /home/ubuntu/recaria
pip3 install -r requirements.txt

# Check Python path
python3.11 -c "import sys; print('\n'.join(sys.path))"

# Test imports
python3.11 -c "import django, osmnx, shapely, networkx; print('All imports OK')"
```

### 10. Performance Issues

**Problem**: Slow response times or high load
**Solutions**:
```bash
# Check system resources
htop
df -h
free -h

# Check Gunicorn worker processes
ps aux | grep gunicorn

# Adjust Gunicorn workers in config
nano /home/ubuntu/recaria/gunicorn.conf.py

# Monitor logs for errors
tail -f /home/ubuntu/recaria/logs/gunicorn_error.log
sudo tail -f /var/log/nginx/recaria_error.log
```

## Quick Deployment Check

Run this command to check all services:
```bash
#!/bin/bash
echo "=== recaria Deployment Status ==="
echo "1. Nginx Status:"
sudo systemctl is-active nginx
echo "2. recaria Service Status:"
sudo systemctl is-active recaria
echo "3. UFW Status:"
sudo ufw status | head -5
echo "4. Port Check:"
sudo ss -tlnp | grep -E ':80|:443|:8000'
echo "5. Process Check:"
ps aux | grep -E 'nginx|gunicorn' | grep -v grep
echo "6. Disk Space:"
df -h /
echo "7. Memory Usage:"
free -h
```

## Emergency Recovery

If the site is completely down:
```bash
# Stop all services
sudo systemctl stop recaria
sudo systemctl stop nginx

# Check for port conflicts
sudo ss -tlnp | grep -E ':80|:443|:8000'

# Kill any conflicting processes
sudo pkill -f gunicorn
sudo pkill -f nginx

# Restart services
sudo systemctl start nginx
sudo systemctl start recaria

# Check status
sudo systemctl status nginx recaria
```

## Contact Information

For technical support:
- Developer: Unicorn Bodrum Technologies
- Project: recaria v047-beta
- Repository: [Project Repository URL]

