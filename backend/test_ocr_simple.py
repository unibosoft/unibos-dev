#!/usr/bin/env python
"""
Simple OCR date parsing test without Django dependency
"""

import sys
import os
from datetime import datetime

# Add backend to path
sys.path.insert(0, '/Users/berkhatirli/Desktop/unibos/backend')

# Mock Django settings to avoid import errors
class MockSettings:
    DEBUG = True

sys.modules['django.conf'] = type('module', (), {'settings': MockSettings()})

from apps.documents.ocr_service import OCRProcessor

def main():
    print("=" * 70)
    print("SIMPLE OCR DATE PARSING TEST")
    print("=" * 70)
    
    processor = OCRProcessor()
    
    # Test receipts with Turkish date formats
    test_receipts = [
        {
            'name': 'PAŞA LAR PETROL (30-05-2025)',
            'text': """PAŞA LAR PETROL
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

TEŞEKKÜR EDERİZ""",
            'expected_date': datetime(2025, 5, 30)
        },
        {
            'name': 'CK PETROL (06-06-2025)',
            'text': """CK PETROL
AKARYAKIT SATIŞ FİŞİ
TARİH: 06-06-2025 SAAT: 14:20
ÜRÜN: V-POWER 95
LİTRE: 40.00
TUTAR: 1,200.00 TL
KREDİ KARTI ****5678""",
            'expected_date': datetime(2025, 6, 6)
        },
        {
            'name': 'MİGROS (25-12-2024)',
            'text': """MİGROS
MİGROS TİCARET A.Ş.
MECLİS MAH.ATATÜRK CAD.NO:14 1/1 MO
SULTANBEYLİ / İSTANBUL

TARİH:25-12-2024  SAAT:15:45
FİŞ NO:0012

DOMATES SALÇA 830 GR       65.90
PEYNİR 600GR              125.00
SÜT 1L 3'LÜ                45.00

TOPLAM                    235.90
NAKİT                     250.00
PARA ÜSTÜ                  14.10""",
            'expected_date': datetime(2024, 12, 25)
        }
    ]
    
    print("\nTesting receipt parsing with Turkish date formats:\n")
    
    success_count = 0
    total_count = len(test_receipts)
    
    for receipt in test_receipts:
        print(f"Receipt: {receipt['name']}")
        print("-" * 50)
        
        # Parse the receipt
        parsed_data = processor.parse_receipt(receipt['text'])
        
        # Check date extraction
        extracted_date = parsed_data.get('transaction_date')
        expected_date = receipt['expected_date']
        
        print(f"  Store Name: {parsed_data.get('store_name', 'Not found')}")
        print(f"  Total Amount: {parsed_data.get('total_amount', 'Not found')}")
        print(f"  Payment Method: {parsed_data.get('payment_method', 'Not found')}")
        print(f"  Receipt Number: {parsed_data.get('receipt_number', 'Not found')}")
        
        if extracted_date:
            print(f"  Extracted Date: {extracted_date.strftime('%d-%m-%Y')}")
            if extracted_date == expected_date:
                print(f"  ✅ Date extraction CORRECT!")
                success_count += 1
            else:
                print(f"  ❌ Date mismatch! Expected: {expected_date.strftime('%d-%m-%Y')}")
        else:
            print(f"  ❌ No date extracted! Expected: {expected_date.strftime('%d-%m-%Y')}")
        
        # Also test direct date extraction
        direct_date = processor.extract_date(receipt['text'])
        if direct_date:
            print(f"  Direct extraction: {direct_date.strftime('%d-%m-%Y')}")
        
        print()
    
    # Test various date formats
    print("\n" + "=" * 70)
    print("TESTING INDIVIDUAL DATE FORMATS")
    print("=" * 70)
    
    date_tests = [
        ("30-05-2025", datetime(2025, 5, 30), "DD-MM-YYYY with hyphen"),
        ("06-06-2025", datetime(2025, 6, 6), "DD-MM-YYYY with hyphen"),
        ("25.12.2024", datetime(2024, 12, 25), "DD.MM.YYYY with dot"),
        ("15/03/2025", datetime(2025, 3, 15), "DD/MM/YYYY with slash"),
        ("TARİH: 30-05-2025", datetime(2025, 5, 30), "With TARİH keyword"),
        ("TARİH:06-06-2025 SAAT:14:20", datetime(2025, 6, 6), "With TARİH and time"),
        ("TARIH 25-12-2024", datetime(2024, 12, 25), "With TARIH (no İ)"),
        ("30-05-25", datetime(2025, 5, 30), "Two digit year"),
        ("15 MAYIS 2025", datetime(2025, 5, 15), "Turkish month name"),
        ("1 OCAK 2025", datetime(2025, 1, 1), "Turkish month (OCAK)"),
        ("30 ARALIK 2024", datetime(2024, 12, 30), "Turkish month (ARALIK)"),
    ]
    
    format_success = 0
    
    for date_text, expected, description in date_tests:
        result = processor.extract_date(date_text)
        if result == expected:
            print(f"  ✅ {description:35} '{date_text}' -> {result.strftime('%d-%m-%Y')}")
            format_success += 1
        else:
            if result:
                print(f"  ❌ {description:35} '{date_text}' -> Got {result.strftime('%d-%m-%Y')}, Expected {expected.strftime('%d-%m-%Y')}")
            else:
                print(f"  ❌ {description:35} '{date_text}' -> Failed (Expected {expected.strftime('%d-%m-%Y')})")
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Receipt Parsing: {success_count}/{total_count} successful ({success_count/total_count*100:.1f}%)")
    print(f"Date Format Tests: {format_success}/{len(date_tests)} successful ({format_success/len(date_tests)*100:.1f}%)")
    
    if success_count == total_count and format_success == len(date_tests):
        print("\n✅ ALL TESTS PASSED! OCR date parsing is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    print("Testing OCR Date Parsing for Turkish Receipts")
    print("Focus: DD-MM-YYYY format with hyphen (common in Turkish receipts)")
    print()
    main()