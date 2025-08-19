#!/usr/bin/env python
"""
Test script to verify OCR structured data display in Document Detail View
"""

import os
import sys
import django

# Add backend directory to path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unibos_backend.settings.development')
django.setup()

from django.contrib.auth import get_user_model
from apps.documents.models import Document, ParsedReceipt, ReceiptItem
from apps.documents.views import prepare_structured_data, get_receipt_items, get_category_breakdown, check_integration_status
from decimal import Decimal
from datetime import datetime

User = get_user_model()

def test_structured_data():
    """Test structured data preparation for documents"""
    
    print("=" * 80)
    print("Testing OCR Structured Data Display")
    print("=" * 80)
    
    # Get a test user
    try:
        user = User.objects.first()
        if not user:
            print("No users found in database")
            return
        print(f"Using user: {user.username}")
    except Exception as e:
        print(f"Error getting user: {e}")
        return
    
    # Get documents with different states
    documents = Document.objects.filter(user=user).order_by('-uploaded_at')[:5]
    
    if not documents:
        print("No documents found for user")
        return
    
    print(f"\nFound {documents.count()} documents")
    print("-" * 80)
    
    for doc in documents:
        print(f"\n📄 Document #{doc.id}: {doc.original_filename}")
        print(f"   Type: {doc.document_type}")
        print(f"   Status: {doc.processing_status}")
        print(f"   Has OCR text: {'Yes' if doc.ocr_text else 'No'}")
        
        # Check if has ParsedReceipt
        has_parsed = hasattr(doc, 'parsed_receipt') and doc.parsed_receipt
        print(f"   Has ParsedReceipt: {'Yes' if has_parsed else 'No'}")
        
        # Test structured data preparation
        print("\n   Testing prepare_structured_data()...")
        structured_data = prepare_structured_data(doc)
        
        if structured_data and any(structured_data.values()):
            print("   ✅ Structured data prepared successfully:")
            
            # Store info
            if structured_data.get('store_info'):
                store = structured_data['store_info']
                print(f"      🏪 Store: {store.get('name', 'N/A')}")
                if store.get('address'):
                    print(f"         Address: {store['address'][:50]}...")
                if store.get('phone'):
                    print(f"         Phone: {store['phone']}")
            
            # Transaction info
            if structured_data.get('transaction'):
                trans = structured_data['transaction']
                if trans.get('date'):
                    print(f"      📅 Date: {trans['date']}")
                if trans.get('receipt_no'):
                    print(f"         Receipt #: {trans['receipt_no']}")
            
            # Financial info
            if structured_data.get('financial'):
                fin = structured_data['financial']
                if fin.get('total'):
                    print(f"      💰 Total: {fin.get('currency', 'TRY')} {fin['total']}")
                if fin.get('tax'):
                    print(f"         Tax: {fin.get('currency', 'TRY')} {fin['tax']}")
            
            # Payment info
            if structured_data.get('payment'):
                pay = structured_data['payment']
                if pay.get('method'):
                    print(f"      💳 Payment: {pay['method']}")
                    if pay.get('card_digits'):
                        print(f"         Card: ****{pay['card_digits']}")
            
            # Items summary
            if structured_data.get('items_summary'):
                items_sum = structured_data['items_summary']
                print(f"      📦 Items: {items_sum.get('count', 0)} items in {items_sum.get('categories', 0)} categories")
        else:
            print("   ⚠️ No structured data available")
            if doc.ocr_text:
                print(f"      OCR text exists ({len(doc.ocr_text)} chars)")
                # Show first 200 chars of OCR text
                print(f"      Preview: {doc.ocr_text[:200]}...")
        
        # Test receipt items
        print("\n   Testing get_receipt_items()...")
        items = get_receipt_items(doc)
        if items:
            print(f"   ✅ Found {len(items)} items:")
            for i, item in enumerate(items[:3]):  # Show first 3 items
                print(f"      {i+1}. {item.name} - Qty: {item.quantity} x {item.unit_price} = {item.total_price}")
            if len(items) > 3:
                print(f"      ... and {len(items) - 3} more items")
        else:
            print("   ⚠️ No items found")
        
        # Test category breakdown
        if items:
            print("\n   Testing get_category_breakdown()...")
            breakdown = get_category_breakdown(items)
            if breakdown:
                print(f"   ✅ Category breakdown:")
                for cat, data in breakdown.items():
                    print(f"      {cat}: {data['count']} items, Total: {data['total']}")
        
        # Test integration status
        print("\n   Testing check_integration_status()...")
        status = check_integration_status(doc)
        print(f"   Integration status:")
        print(f"      WIMM: {'✅' if status['wimm'] else '❌'}")
        print(f"      Personal Inflation: {'✅' if status['personal_inflation'] else '❌'}")
        print(f"      WIMS: {'✅' if status['wims'] else '❌'}")
        print(f"      Currencies: {'✅' if status['currencies'] else '❌'}")
        
        print("-" * 80)
    
    # Test with a document that has no ParsedReceipt but has OCR text
    print("\n" + "=" * 80)
    print("Testing document with OCR text but no ParsedReceipt:")
    print("=" * 80)
    
    doc_with_ocr = Document.objects.filter(
        user=user,
        ocr_text__isnull=False,
        document_type='receipt'
    ).exclude(
        id__in=ParsedReceipt.objects.values_list('document_id', flat=True)
    ).first()
    
    if doc_with_ocr:
        print(f"\n📄 Document #{doc_with_ocr.id}: {doc_with_ocr.original_filename}")
        print(f"   OCR text length: {len(doc_with_ocr.ocr_text)} chars")
        
        structured_data = prepare_structured_data(doc_with_ocr)
        if structured_data and any(structured_data.values()):
            print("   ✅ Successfully parsed OCR text to structured data!")
            
            # Show what was extracted
            if structured_data.get('store_info', {}).get('name'):
                print(f"      Store: {structured_data['store_info']['name']}")
            if structured_data.get('financial', {}).get('total'):
                print(f"      Total: {structured_data['financial']['total']}")
            if structured_data.get('transaction', {}).get('date'):
                print(f"      Date: {structured_data['transaction']['date']}")
        else:
            print("   ⚠️ Could not parse OCR text to structured data")
            print(f"   OCR text preview: {doc_with_ocr.ocr_text[:300]}...")
    else:
        print("No documents found with OCR text but without ParsedReceipt")
    
    print("\n" + "=" * 80)
    print("Test completed!")
    print("=" * 80)

if __name__ == "__main__":
    test_structured_data()