#!/usr/bin/env python
"""
Test script to verify OCR date parsing improvements
Works with real Django models and database
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, '/Users/berkhatirli/Desktop/unibos/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unibos_backend.settings.development')
django.setup()

from datetime import datetime
from apps.documents.models import Document
from apps.documents.ocr_service import OCRProcessor

def test_real_documents():
    """Test OCR on real documents in database"""
    print("=" * 70)
    print("TESTING OCR ON REAL DOCUMENTS")
    print("=" * 70)
    
    # Get recent receipts
    receipts = Document.objects.filter(document_type='receipt').order_by('-created_at')[:5]
    
    if receipts:
        print(f"\nFound {receipts.count()} recent receipts:\n")
        
        processor = OCRProcessor()
        
        for doc in receipts:
            print(f"Document ID: {doc.id}")
            print(f"  Name: {doc.name}")
            print(f"  Created: {doc.created_at}")
            
            # Check if has parsed receipt
            if hasattr(doc, 'parsed_receipt'):
                pr = doc.parsed_receipt
                print(f"  Current parsed date: {pr.transaction_date}")
            
            # Try to re-process with new OCR
            if doc.file_path and os.path.exists(doc.file_path.path):
                try:
                    result = processor.process_document(
                        doc.file_path.path,
                        document_type='receipt',
                        force_ocr=True
                    )
                    
                    if result['success']:
                        parsed_data = result.get('parsed_data', {})
                        if parsed_data.get('transaction_date'):
                            print(f"  ✅ New parsed date: {parsed_data['transaction_date']}")
                        else:
                            print(f"  ⚠️ No date extracted")
                        
                        if result.get('ocr_text'):
                            # Show first few lines of OCR text
                            lines = result['ocr_text'].split('\n')[:5]
                            print(f"  OCR preview: {' | '.join(line.strip() for line in lines if line.strip())[:100]}...")
                    else:
                        print(f"  ❌ OCR failed: {result.get('error')}")
                except Exception as e:
                    print(f"  ❌ Error: {str(e)}")
            else:
                print(f"  ⚠️ File not found")
            
            print()
    else:
        print("No receipts found in database")

def test_sample_texts():
    """Test various sample receipt texts"""
    print("\n" + "=" * 70)
    print("TESTING SAMPLE RECEIPT TEXTS")
    print("=" * 70)
    
    processor = OCRProcessor()
    
    sample_receipts = [
        {
            'name': 'PAŞA LAR PETROL Receipt',
            'text': """PAŞA LAR PETROL
AKARYAKIT SATIŞ FİŞİ
VERGİ NO: 123456789
TARİH: 30-05-2025
SAAT: 12:45
FİŞ NO: 00142
TOPLAM: 812.50 TL
KREDİ KARTI ****1234"""
        },
        {
            'name': 'CK PETROL Receipt',
            'text': """CK PETROL
AKARYAKIT SATIŞ FİŞİ
TARİH: 06-06-2025 SAAT: 14:20
ÜRÜN: V-POWER 95
LİTRE: 40.00
TUTAR: 1,200.00 TL"""
        },
        {
            'name': 'Turkish Market Receipt',
            'text': """MİGROS
MİGROS TİCARET A.Ş.
TARİH:25-12-2024  SAAT:15:45
FİŞ NO:0012
DOMATES SALÇA 830 GR       65.90
PEYNİR 600GR              125.00
TOPLAM                    190.90
NAKİT                     200.00
PARA ÜSTÜ                   9.10"""
        }
    ]
    
    for sample in sample_receipts:
        print(f"\n{sample['name']}:")
        print("-" * 40)
        
        # Parse the receipt
        parsed = processor.parse_receipt(sample['text'])
        
        print(f"  Store: {parsed.get('store_name', 'Unknown')}")
        print(f"  Date: {parsed.get('transaction_date')}")
        print(f"  Total: {parsed.get('total_amount')}")
        print(f"  Payment: {parsed.get('payment_method', 'Unknown')}")
        
        if parsed.get('transaction_date'):
            print(f"  ✅ Date extraction successful: {parsed['transaction_date'].strftime('%d-%m-%Y')}")
        else:
            print(f"  ❌ Date extraction failed")

def test_date_formats():
    """Test specific date format patterns"""
    print("\n" + "=" * 70)
    print("TESTING DATE FORMAT PATTERNS")
    print("=" * 70)
    
    processor = OCRProcessor()
    
    date_samples = [
        ("30-05-2025", "Hyphen format"),
        ("06.06.2025", "Dot format"),
        ("15/03/2025", "Slash format"),
        ("TARİH: 30-05-2025", "With TARİH keyword"),
        ("TARIH:06-06-2025 SAAT:14:20", "With time"),
        ("25 MAYIS 2025", "Turkish month name"),
        ("TARİH: 01-01-25", "Two digit year"),
    ]
    
    print("\nDate extraction results:")
    for date_text, description in date_samples:
        result = processor.extract_date(date_text)
        if result:
            print(f"  ✅ {description:25} '{date_text:20}' -> {result.strftime('%d-%m-%Y')}")
        else:
            print(f"  ❌ {description:25} '{date_text:20}' -> Failed")

if __name__ == "__main__":
    print("OCR Date Parsing Improvements Test")
    print("Testing Turkish receipt date formats (DD-MM-YYYY)")
    print()
    
    try:
        test_date_formats()
        test_sample_texts()
        test_real_documents()
        
        print("\n" + "=" * 70)
        print("✅ All tests completed successfully!")
        print("=" * 70)
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()