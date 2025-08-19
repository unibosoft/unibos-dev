#!/usr/bin/env python
"""
Test login functionality
"""
import requests
import json

# Test credentials
username = "berkhatirli"
password = "admin123"

print("=== UNIBOS Login Test ===\n")

# API Login test
print("Testing API login...")
api_url = "http://localhost:8000/api/v1/auth/login/"
response = requests.post(api_url, json={
    "username": username,
    "password": password
})

if response.status_code == 200:
    data = response.json()
    print(f"✓ API Login successful!")
    print(f"  Token: {data.get('token', 'N/A')[:20]}...")
    print(f"  User: {data.get('user', {}).get('username', 'N/A')}")
else:
    print(f"✗ API Login failed: {response.status_code}")
    print(f"  Response: {response.text}")

print("\n=== Login Info ===")
print("Web Login: http://localhost:8000/login/")
print("Username: berkhatirli")
print("Password: admin123")
print("\nAfter login, you should see your username in the top-right corner!")