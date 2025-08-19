#!/usr/bin/env python
"""
Test script to verify Documents module multi-select and recycle bin features
"""
import os
import django
import sys

# Add the backend directory to the path
sys.path.insert(0, '/Users/berkhatirli/Desktop/unibos/backend')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unibos_backend.settings.emergency')
django.setup()

from django.contrib.auth import get_user_model
from apps.documents.models import Document
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

def test_soft_delete_fields():
    """Test if soft delete fields exist in Document model"""
    print("\n=== Testing Soft Delete Fields ===")
    
    # Check if fields exist
    field_names = [f.name for f in Document._meta.fields]
    required_fields = ['is_deleted', 'deleted_at', 'deleted_by']
    
    for field in required_fields:
        if field in field_names:
            print(f"✓ Field '{field}' exists")
        else:
            print(f"✗ Field '{field}' MISSING")
    
    # Check for any documents
    total_docs = Document.objects.count()
    active_docs = Document.objects.filter(is_deleted=False).count()
    deleted_docs = Document.objects.filter(is_deleted=True).count()
    
    print(f"\n=== Document Statistics ===")
    print(f"Total documents: {total_docs}")
    print(f"Active documents: {active_docs}")
    print(f"Deleted documents (in recycle bin): {deleted_docs}")
    
    # Show some sample documents
    if active_docs > 0:
        print("\n=== Sample Active Documents ===")
        for doc in Document.objects.filter(is_deleted=False)[:3]:
            print(f"- {doc.original_filename} (ID: {doc.id})")
    
    if deleted_docs > 0:
        print("\n=== Sample Deleted Documents ===")
        for doc in Document.objects.filter(is_deleted=True)[:3]:
            days_old = (timezone.now() - doc.deleted_at).days if doc.deleted_at else 0
            print(f"- {doc.original_filename} (deleted {days_old} days ago)")

def test_bulk_operations():
    """Test bulk operations availability"""
    print("\n=== Testing Bulk Operations URLs ===")
    
    from django.urls import reverse
    
    urls_to_test = [
        'documents:bulk_delete',
        'documents:bulk_reprocess',
        'documents:recycle_bin',
        'documents:restore',
        'documents:permanent_delete',
        'documents:empty_recycle_bin',
        'documents:export'
    ]
    
    for url_name in urls_to_test:
        try:
            url = reverse(url_name)
            print(f"✓ URL '{url_name}' resolves to: {url}")
        except Exception as e:
            print(f"✗ URL '{url_name}' error: {e}")

def create_test_data():
    """Create some test documents if needed"""
    print("\n=== Creating Test Data (if needed) ===")
    
    # Get or create a test user
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'test@example.com', 'is_active': True}
    )
    
    if created:
        user.set_password('testpass123')
        user.save()
        print(f"Created test user: {user.username}")
    
    # Check if we need test documents
    user_docs = Document.objects.filter(user=user).count()
    
    if user_docs < 5:
        print(f"Creating test documents for user {user.username}...")
        
        for i in range(5):
            doc = Document.objects.create(
                user=user,
                document_type='receipt',
                original_filename=f'test_receipt_{i+1}.pdf',
                processing_status='completed',
                ocr_text=f'Sample OCR text for document {i+1}'
            )
            print(f"  Created: {doc.original_filename}")
        
        # Create some deleted documents for recycle bin
        for i in range(3):
            doc = Document.objects.create(
                user=user,
                document_type='invoice',
                original_filename=f'deleted_invoice_{i+1}.pdf',
                processing_status='completed',
                ocr_text=f'Sample OCR text for deleted document {i+1}',
                is_deleted=True,
                deleted_at=timezone.now() - timedelta(days=i+1),
                deleted_by=user
            )
            print(f"  Created deleted: {doc.original_filename} (deleted {i+1} days ago)")
    else:
        print(f"User {user.username} already has {user_docs} documents")

def check_templates():
    """Check if all required templates exist"""
    print("\n=== Checking Templates ===")
    
    import os
    
    template_dir = '/Users/berkhatirli/Desktop/unibos/backend/templates/documents'
    required_templates = [
        'dashboard_fixed.html',
        'recycle_bin.html',
        'document_list.html',
        'upload.html'
    ]
    
    for template in required_templates:
        path = os.path.join(template_dir, template)
        if os.path.exists(path):
            size = os.path.getsize(path)
            print(f"✓ Template '{template}' exists ({size} bytes)")
        else:
            print(f"✗ Template '{template}' MISSING")

if __name__ == '__main__':
    print("="*50)
    print("Documents Module Feature Test")
    print("="*50)
    
    test_soft_delete_fields()
    test_bulk_operations()
    check_templates()
    create_test_data()
    
    print("\n" + "="*50)
    print("Test Complete!")
    print("\nTo test in browser:")
    print("1. Login as 'testuser' with password 'testpass123'")
    print("2. Go to http://localhost:8000/documents/")
    print("3. Check the 'enable multi-select mode' checkbox")
    print("4. Click on 'recycle bin' link in top-right")
    print("="*50)