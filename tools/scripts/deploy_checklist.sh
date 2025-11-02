#!/bin/bash
# UNIBOS Deploy Checklist - Remote sync öncesi kontrol

echo "🔍 Checking remote dependencies..."

ssh rocksteady << 'REMOTE'
cd ~/unibos/backend

# 1. Check Python packages
echo "=== Required packages check ==="
./venv/bin/pip list | grep -E "(Django|Pillow|requests|aiohttp|psycopg2)" || {
    echo "⚠️ Missing packages detected"
    echo "Installing core packages..."
    ./venv/bin/pip install -q Django Pillow requests aiohttp psycopg2-binary djangorestframework django-cors-headers whitenoise
}

# 2. Test Django can start
echo "=== Django startup test ==="
timeout 5 ./venv/bin/python manage.py check --settings=unibos_backend.settings.development 2>&1 | head -5

# 3. Ensure Django is running
if ! pgrep -f "manage.py runserver" > /dev/null; then
    echo "Starting Django..."
    nohup ./venv/bin/python manage.py runserver 0.0.0.0:8000 --settings=unibos_backend.settings.development > /tmp/django.log 2>&1 &
    sleep 3
fi

echo "✅ Deploy check complete"
REMOTE
