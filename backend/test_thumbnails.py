#!/usr/bin/env python
"""Test thumbnail accessibility"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unibos_backend.settings.emergency')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from apps.documents.models import Document
from django.conf import settings

print("=" * 50)
print("THUMBNAIL TEST REPORT")
print("=" * 50)

# Check media settings
print(f"\nMEDIA_ROOT: {settings.MEDIA_ROOT}")
print(f"MEDIA_URL: {settings.MEDIA_URL}")
print(f"DEBUG: {settings.DEBUG}")

# Get documents with thumbnails
docs_with_thumbnails = Document.objects.exclude(thumbnail_path='').exclude(thumbnail_path__isnull=True)
print(f"\nDocuments with thumbnails: {docs_with_thumbnails.count()}")

# Test first 5 documents
for doc in docs_with_thumbnails[:5]:
    print(f"\n📄 Document: {doc.original_filename}")
    print(f"   ID: {doc.id}")
    print(f"   Thumbnail field: {doc.thumbnail_path}")
    
    if doc.thumbnail_path:
        # Check if file exists
        full_path = os.path.join(settings.MEDIA_ROOT, str(doc.thumbnail_path))
        exists = os.path.exists(full_path)
        print(f"   Physical file exists: {'✅' if exists else '❌'}")
        
        if exists:
            file_size = os.path.getsize(full_path) / 1024  # KB
            print(f"   File size: {file_size:.2f} KB")
        
        # Print URL
        try:
            url = doc.thumbnail_path.url
            print(f"   URL: {url}")
            print(f"   Full URL: http://localhost:8000{url}")
        except Exception as e:
            print(f"   ❌ Error getting URL: {e}")

print("\n" + "=" * 50)
print("Test complete! Check if URLs work in browser.")
print("=" * 50)