"""
Test script for OCR date parsing improvements
Tests various Turkish receipt date formats
"""

import os
import sys
from datetime import datetime

# Add backend to path
sys.path.insert(0, '/Users/berkhatirli/Desktop/unibos/backend')

# Import directly without Django setup for testing
from apps.documents.ocr_service import OCRProcessor

def test_date_extraction():
    """Test different date formats from receipts"""
    
    processor = OCRProcessor()
    
    # Test cases with various Turkish receipt date formats
    test_cases = [
        # Real receipt formats with hyphen (tire)
        ("TARİH: 30-05-2025 SAAT: 10:15", datetime(2025, 5, 30)),
        ("TARİH:06-06-2025", datetime(2025, 6, 6)),
        ("TARIH 25-12-2024", datetime(2024, 12, 25)),
        
        # Dot format (nokta)
        ("TARİH: 15.03.2025", datetime(2025, 3, 15)),
        ("TARİH:01.01.2025 14:30", datetime(2025, 1, 1)),
        
        # Slash format
        ("TARİH: 07/08/2025", datetime(2025, 8, 7)),
        ("TARIH:20/11/2024", datetime(2024, 11, 20)),
        
        # Without keyword
        ("30-05-2025 15:45", datetime(2025, 5, 30)),
        ("01.06.2025", datetime(2025, 6, 1)),
        
        # Two digit year
        ("TARİH: 30-05-25", datetime(2025, 5, 30)),
        ("15.03.24", datetime(2024, 3, 15)),
        
        # Turkish month names
        ("15 MAYIS 2025", datetime(2025, 5, 15)),
        ("1 OCAK 2025", datetime(2025, 1, 1)),
        ("30 ARALIK 2024", datetime(2024, 12, 30)),
        
        # Real receipt text samples
        ("""PAŞA LAR PETROL
        VERGİ NO: 123456789
        TARİH: 30-05-2025
        SAAT: 12:45
        TOPLAM: 500.00 TL""", datetime(2025, 5, 30)),
        
        ("""CK PETROL
        AKARYAKIT SATIŞ FİŞİ
        TARİH: 06-06-2025 SAAT: 14:20
        ÜRÜN: V-POWER 95
        LİTRE: 40.00
        TUTAR: 1,200.00 TL""", datetime(2025, 6, 6)),
    ]
    
    print("=" * 70)
    print("OCR DATE PARSING TEST RESULTS")
    print("=" * 70)
    
    passed = 0
    failed = 0
    
    for i, (text, expected_date) in enumerate(test_cases, 1):
        # Clean display text for output
        display_text = text.replace('\n', ' ')[:50] + ('...' if len(text) > 50 else '')
        
        # Extract date
        extracted_date = processor.extract_date(text)
        
        # Check result
        if extracted_date == expected_date:
            print(f"✅ Test {i:2d}: PASSED")
            print(f"   Text: {display_text}")
            print(f"   Expected: {expected_date.strftime('%d-%m-%Y') if expected_date else 'None'}")
            print(f"   Got: {extracted_date.strftime('%d-%m-%Y') if extracted_date else 'None'}")
            passed += 1
        else:
            print(f"❌ Test {i:2d}: FAILED")
            print(f"   Text: {display_text}")
            print(f"   Expected: {expected_date.strftime('%d-%m-%Y') if expected_date else 'None'}")
            print(f"   Got: {extracted_date.strftime('%d-%m-%Y') if extracted_date else 'None'}")
            failed += 1
        print()
    
    print("=" * 70)
    print(f"SUMMARY: {passed} passed, {failed} failed out of {passed + failed} tests")
    print(f"Success Rate: {(passed / (passed + failed) * 100):.1f}%")
    print("=" * 70)
    
    # Test full receipt parsing
    print("\n" + "=" * 70)
    print("FULL RECEIPT PARSING TEST")
    print("=" * 70)
    
    sample_receipt = """PAŞA LAR PETROL
AKARYAKIT SATIŞ FİŞİ
VERGİ NO: 123456789
ADRES: İSTANBUL

TARİH: 30-05-2025
SAAT: 12:45
FİŞ NO: 00142

ÜRÜN: KURŞUNSUZ 95
LİTRE: 25.00
BİRİM FİYAT: 32.50
TUTAR: 812.50

TOPLAM: 812.50 TL
KREDİ KARTI ****1234

TEŞEKKÜR EDERİZ"""
    
    result = processor.parse_receipt(sample_receipt)
    
    print("Parsed Receipt Data:")
    print(f"  Store Name: {result.get('store_name')}")
    print(f"  Transaction Date: {result.get('transaction_date')}")
    print(f"  Total Amount: {result.get('total_amount')}")
    print(f"  Receipt Number: {result.get('receipt_number')}")
    print(f"  Payment Method: {result.get('payment_method')}")
    print(f"  Card Last Digits: {result.get('card_last_digits')}")
    print(f"  Items Found: {len(result.get('items', []))}")
    
    if result.get('transaction_date'):
        print(f"\n✅ Date extraction successful: {result['transaction_date'].strftime('%d-%m-%Y')}")
    else:
        print("\n❌ Date extraction failed")

def test_fallback_ocr():
    """Test fallback OCR with updated date formats"""
    print("\n" + "=" * 70)
    print("FALLBACK OCR TEST")
    print("=" * 70)
    
    processor = OCRProcessor()
    
    # Temporarily disable tesseract to test fallback
    original_tesseract = processor.tesseract_available
    processor.tesseract_available = False
    
    # Get fallback text
    fallback_text = processor.fallback_ocr("/fake/path.jpg")
    
    print("Fallback OCR Text Sample:")
    print("-" * 40)
    print(fallback_text[:500])
    print("-" * 40)
    
    # Test date extraction from fallback
    extracted_date = processor.extract_date(fallback_text)
    if extracted_date:
        print(f"✅ Date extracted from fallback: {extracted_date.strftime('%d-%m-%Y')}")
    else:
        print("❌ No date extracted from fallback")
    
    # Restore original setting
    processor.tesseract_available = original_tesseract

if __name__ == "__main__":
    print("Starting OCR Date Parsing Tests...")
    print("Testing Turkish receipt date formats (DD-MM-YYYY with hyphen)")
    print()
    
    test_date_extraction()
    test_fallback_ocr()
    
    print("\n✅ Test completed successfully!")