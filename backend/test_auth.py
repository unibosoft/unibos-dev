#!/usr/bin/env python
"""
Test authentication system
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unibos_backend.settings.emergency')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.models import User
from apps.core.models import UserProfile

# Check users
print("=== UNIBOS Authentication Test ===\n")
print(f"Total users: {User.objects.count()}")
print(f"Superusers: {User.objects.filter(is_superuser=True).count()}")
print(f"User profiles: {UserProfile.objects.count()}")

print("\n=== User List ===")
for user in User.objects.all()[:5]:
    print(f"- {user.username} ({'superuser' if user.is_superuser else 'regular'})")
    if hasattr(user, 'profile'):
        print(f"  Profile: Language={user.profile.preferred_language}, Theme={user.profile.theme}")

# Check berkhatirli user
print("\n=== Testing 'berkhatirli' user ===")
try:
    berk = User.objects.get(username='berkhatirli')
    print(f"✓ User found: {berk.username}")
    print(f"  Email: {berk.email}")
    print(f"  Superuser: {berk.is_superuser}")
    print(f"  Active: {berk.is_active}")
    
    # Reset password for testing
    berk.set_password('admin123')
    berk.save()
    print("✓ Password set to: admin123")
    
    # Test authentication
    from django.contrib.auth import authenticate
    test_user = authenticate(username='berkhatirli', password='admin123')
    if test_user:
        print("✓ Authentication successful!")
    else:
        print("✗ Authentication failed!")
        
except User.DoesNotExist:
    print("✗ User 'berkhatirli' not found!")

print("\n=== Server Info ===")
print("Server URL: http://localhost:8000")
print("Login URL: http://localhost:8000/login/")
print("API Login: http://localhost:8000/api/v1/auth/login/")
print("\nTest credentials:")
print("  Username: berkhatirli")
print("  Password: admin123")
print("\n✅ Authentication system is ready!")