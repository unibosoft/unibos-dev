#!/usr/bin/env python
"""
Test script to verify document serving functionality
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unibos_backend.settings.emergency')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from apps.documents.models import Document

# Get or create test user
user, created = User.objects.get_or_create(
    username='testuser',
    defaults={'email': 'test@test.com'}
)
if created:
    user.set_password('testpass123')
    user.save()
    print(f"Created test user: {user.username}")
else:
    print(f"Using existing user: {user.username}")

# Check documents
documents = Document.objects.filter(user=user)
print(f"\nDocuments for {user.username}: {documents.count()}")

for doc in documents[:5]:
    print(f"\n  Document: {doc.original_filename}")
    print(f"    ID: {doc.id}")
    print(f"    Status: {doc.processing_status}")
    
    if doc.file_path:
        print(f"    File exists: {doc.file_path.name}")
        file_path = doc.file_path.path if hasattr(doc.file_path, 'path') else None
        if file_path and os.path.exists(file_path):
            print(f"    File on disk: YES ({os.path.getsize(file_path):,} bytes)")
        else:
            print(f"    File on disk: NO")
    
    if doc.thumbnail_path:
        print(f"    Thumbnail: {doc.thumbnail_path.name}")
        thumb_path = doc.thumbnail_path.path if hasattr(doc.thumbnail_path, 'path') else None
        if thumb_path and os.path.exists(thumb_path):
            print(f"    Thumb on disk: YES ({os.path.getsize(thumb_path):,} bytes)")
        else:
            print(f"    Thumb on disk: NO")
    
    # Test URL generation
    print(f"    View URL: /documents/document/{doc.id}/view/")

# Create test client
client = Client()
client.force_login(user)

# Test document view endpoint
if documents.exists():
    doc = documents.first()
    response = client.get(f'/documents/document/{doc.id}/view/')
    print(f"\nTesting document view for {doc.id}:")
    print(f"  Response status: {response.status_code}")
    print(f"  Content type: {response.get('Content-Type', 'N/A')}")
    print(f"  Content length: {response.get('Content-Length', 'N/A')}")
    
    if response.status_code == 200:
        print("  ✓ Document serving is working!")
    else:
        print(f"  ✗ Error: {response.content[:200] if response.content else 'No content'}")

print("\n" + "="*60)
print("TEST COMPLETE")
print("="*60)
print("\nTo access the documents page:")
print("1. Visit: http://localhost:8000/documents/")
print("2. Login with admin credentials")
print("3. Documents should display with working thumbnails and modal viewer")