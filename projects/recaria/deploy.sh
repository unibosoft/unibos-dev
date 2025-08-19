#!/bin/bash
# Deployment script for recaria.org
# Run this script on the Oracle Cloud server

set -e

echo "=== Recaria Deployment Script ==="
echo "Unicorn Bodrum Technologies - v047-beta"
echo

# Variables
PROJECT_DIR="/home/ubuntu/recaria"
NGINX_CONF="/etc/nginx/sites-available/recaria"
SERVICE_FILE="/etc/systemd/system/recaria.service"

# Check if running as root for system configurations
if [[ $EUID -eq 0 ]]; then
    echo "Running as root - will configure system services"
    SUDO=""
else
    echo "Running as user - will use sudo for system configurations"
    SUDO="sudo"
fi

# Update system packages
echo "1. Updating system packages..."
$SUDO apt update && $SUDO apt upgrade -y

# Install required system packages
echo "2. Installing required system packages..."
$SUDO apt install -y nginx python3-pip python3-venv ufw

# Install Python dependencies
echo "3. Installing Python dependencies..."
cd $PROJECT_DIR
pip3 install -r requirements.txt

# Configure UFW firewall
echo "4. Configuring UFW firewall..."
$SUDO ufw --force enable
$SUDO ufw allow ssh
$SUDO ufw allow 'Nginx Full'
$SUDO ufw allow 80
$SUDO ufw allow 443
$SUDO ufw status

# Configure Nginx
echo "5. Configuring Nginx..."
$SUDO cp nginx_recaria.conf $NGINX_CONF
$SUDO ln -sf $NGINX_CONF /etc/nginx/sites-enabled/recaria
$SUDO rm -f /etc/nginx/sites-enabled/default
$SUDO nginx -t

# Configure systemd service
echo "6. Configuring systemd service..."
$SUDO cp recaria.service $SERVICE_FILE
$SUDO systemctl daemon-reload
$SUDO systemctl enable recaria

# Create necessary directories and set permissions
echo "7. Setting up directories and permissions..."
mkdir -p logs
mkdir -p recaria/media
mkdir -p recaria/staticfiles
$SUDO chown -R ubuntu:ubuntu $PROJECT_DIR

# Collect static files
echo "8. Collecting static files..."
cd recaria
python3.11 manage.py collectstatic --noinput

# Run database migrations
echo "9. Running database migrations..."
python3.11 manage.py migrate

# Stop Django development server if running
echo "10. Stopping development server..."
pkill -f "manage.py runserver" || true

# Start services
echo "11. Starting services..."
$SUDO systemctl start recaria
$SUDO systemctl restart nginx

# Check service status
echo "12. Checking service status..."
$SUDO systemctl status recaria --no-pager
$SUDO systemctl status nginx --no-pager

echo
echo "=== Deployment Complete ==="
echo "Application should be accessible at:"
echo "- http://your-server-ip"
echo "- https://recaria.org (if DNS is configured)"
echo
echo "To check logs:"
echo "- Application: sudo journalctl -u recaria -f"
echo "- Nginx: sudo tail -f /var/log/nginx/recaria_error.log"
echo "- Gunicorn: tail -f $PROJECT_DIR/logs/gunicorn_error.log"
echo
echo "To manage the service:"
echo "- Start: sudo systemctl start recaria"
echo "- Stop: sudo systemctl stop recaria"
echo "- Restart: sudo systemctl restart recaria"
echo "- Status: sudo systemctl status recaria"

