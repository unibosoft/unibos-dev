#!/usr/bin/env python
"""
Test OCR structured data using Django shell
Run with: python manage.py shell < test_ocr_shell.py
"""

from apps.documents.models import Document, ParsedReceipt
from apps.documents.views import prepare_structured_data, get_receipt_items, get_category_breakdown, check_integration_status
from django.contrib.auth import get_user_model

User = get_user_model()

# Get a test user
user = User.objects.first()
if not user:
    print("No users found")
    exit()

print(f"Testing with user: {user.username}")

# Get recent documents
documents = Document.objects.filter(user=user)[:3]

for doc in documents:
    print(f"\n{'='*60}")
    print(f"Document #{doc.id}: {doc.original_filename}")
    print(f"Type: {doc.document_type}, Status: {doc.processing_status}")
    
    # Check for OCR text
    if doc.ocr_text:
        print(f"OCR text: {len(doc.ocr_text)} characters")
    else:
        print("No OCR text")
    
    # Check for ParsedReceipt
    has_parsed = hasattr(doc, 'parsed_receipt') and doc.parsed_receipt
    print(f"Has ParsedReceipt: {has_parsed}")
    
    # Prepare structured data
    structured_data = prepare_structured_data(doc)
    
    if structured_data and any(structured_data.values()):
        print("\nStructured Data:")
        
        if structured_data.get('store_info'):
            store = structured_data['store_info']
            print(f"  Store: {store.get('name', 'N/A')}")
            
        if structured_data.get('transaction'):
            trans = structured_data['transaction']
            if trans.get('date'):
                print(f"  Date: {trans['date']}")
            if trans.get('receipt_no'):
                print(f"  Receipt #: {trans['receipt_no']}")
        
        if structured_data.get('financial'):
            fin = structured_data['financial']
            if fin.get('total'):
                print(f"  Total: {fin.get('currency', 'TRY')} {fin['total']}")
        
        if structured_data.get('payment'):
            pay = structured_data['payment']
            if pay.get('method'):
                print(f"  Payment: {pay['method']}")
                if pay.get('card_digits'):
                    print(f"  Card: ****{pay['card_digits']}")
        
        if structured_data.get('items_summary'):
            items_sum = structured_data['items_summary']
            print(f"  Items: {items_sum.get('count', 0)} items")
    else:
        print("No structured data available")
        if doc.ocr_text:
            print(f"OCR text preview: {doc.ocr_text[:200]}...")
    
    # Check integration status
    status = check_integration_status(doc)
    print(f"\nIntegration Status:")
    print(f"  WIMM: {'Yes' if status['wimm'] else 'No'}")
    print(f"  Personal Inflation: {'Yes' if status['personal_inflation'] else 'No'}")
    print(f"  WIMS: {'Yes' if status['wims'] else 'No'}")
    print(f"  Currencies: {'Yes' if status['currencies'] else 'No'}")

print(f"\n{'='*60}")
print("Test completed!")