#!/usr/bin/env python
"""Test and fix OCR for existing documents"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unibos_backend.settings.emergency')
sys.path.insert(0, '/Users/berkhatirli/Desktop/unibos/backend')
django.setup()

from apps.documents.models import Document
from apps.documents.ocr_service import OCRProcessor

def fix_all_documents():
    """Process OCR for all documents that don't have OCR text"""
    
    # Get documents without OCR
    documents = Document.objects.filter(ocr_text__isnull=True) | Document.objects.filter(ocr_text='')
    total = documents.count()
    
    print(f"Found {total} documents without OCR text")
    
    if total == 0:
        # Check all documents
        documents = Document.objects.all()
        total = documents.count()
        print(f"Checking all {total} documents...")
    
    # Initialize OCR processor
    ocr = OCRProcessor()
    
    processed = 0
    failed = 0
    
    for doc in documents:
        print(f"\nProcessing: {doc.original_filename}")
        
        try:
            # Process OCR
            result = ocr.process_document(
                doc.file_path.path,
                document_type=doc.document_type,
                force_ocr=True
            )
            
            if result['success'] and result.get('ocr_text'):
                # Save OCR text
                doc.ocr_text = result['ocr_text']
                doc.ocr_confidence = result.get('confidence', 0)
                doc.processing_status = 'completed'
                doc.save()
                
                processed += 1
                print(f"  ✓ OCR successful: {len(doc.ocr_text)} characters")
                print(f"  Method: {result.get('ocr_method', 'unknown')}")
                
                # Show first 100 chars
                preview = doc.ocr_text[:100].replace('\n', ' ')
                print(f"  Preview: {preview}...")
            else:
                failed += 1
                print(f"  ✗ OCR failed: {result.get('error', 'Unknown error')}")
                doc.processing_status = 'manual_review'
                doc.save()
                
        except Exception as e:
            failed += 1
            print(f"  ✗ Exception: {str(e)}")
            doc.processing_status = 'failed'
            doc.save()
    
    print(f"\n=== SUMMARY ===")
    print(f"Total documents: {total}")
    print(f"Successfully processed: {processed}")
    print(f"Failed: {failed}")
    
    # Show current status
    print(f"\n=== CURRENT STATUS ===")
    with_ocr = Document.objects.exclude(ocr_text__isnull=True).exclude(ocr_text='').count()
    without_ocr = Document.objects.filter(ocr_text__isnull=True) | Document.objects.filter(ocr_text='')
    without_ocr = without_ocr.count()
    
    print(f"Documents with OCR: {with_ocr}")
    print(f"Documents without OCR: {without_ocr}")
    print(f"Total: {Document.objects.count()}")

if __name__ == "__main__":
    fix_all_documents()