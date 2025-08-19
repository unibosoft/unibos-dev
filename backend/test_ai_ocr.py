#!/usr/bin/env python
"""
Test AI-Enhanced OCR Processing
Tests both Hugging Face and fallback methods
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, '/Users/berkhatirli/Desktop/unibos/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unibos_backend.settings.emergency')
django.setup()

from apps.documents.ai_ocr_enhancer import AIReceiptAnalyzer

def test_ai_ocr():
    """Test AI OCR enhancement with sample receipt text"""
    
    # Sample Turkish receipt text with some OCR errors
    sample_ocr_text = """MIGR0S
TiCARET A.Ş.
BODRUM TURGUTRES
VERGl NO: 123456789
TARiH: 30-05-2025
SAAT: 14:35
FIS NO: 000142

URUN ADI         ADET  FIYAT   TUTAR
DOMATES KG       2.5   12.99   32.48
SALATALIK        1     8.99    8.99
BEYAZ PEYNIR     1     45.90   45.90
EKMEK            2     5.00    10.00

ARA TOPLAM              97.37
KDV %8                  7.79
TOPLAM                  105.16

KREDI KARTI ****1234
ONAY KODU: 123456

TESEKKUR EDERIZ
IYI GUNLER DILERIZ"""

    print("=" * 70)
    print("AI-ENHANCED OCR TEST")
    print("=" * 70)
    
    # Test with Hugging Face (free)
    print("\n1. Testing with Hugging Face API...")
    try:
        analyzer_hf = AIReceiptAnalyzer(provider="huggingface")
        
        # Test correction mode
        print("\n   a) Correction Mode:")
        result = analyzer_hf.analyze_receipt_with_ai(sample_ocr_text, enhance_mode="correction")
        if result.get('corrected_text'):
            print(f"      ✅ Text corrected: {len(result['corrected_text'])} chars")
        else:
            print("      ⚠️ No correction available")
        
        # Test quick mode
        print("\n   b) Quick Analysis Mode:")
        result = analyzer_hf.analyze_receipt_with_ai(sample_ocr_text, enhance_mode="quick")
        if result:
            print(f"      Store: {result.get('store_name', 'N/A')}")
            print(f"      Date: {result.get('date', 'N/A')}")
            print(f"      Total: {result.get('total', 'N/A')}")
        
        # Test full mode
        print("\n   c) Full Analysis Mode:")
        result = analyzer_hf.analyze_receipt_with_ai(sample_ocr_text, enhance_mode="full")
        if result:
            if result.get('store_info'):
                print(f"      Store: {result['store_info'].get('name', 'N/A')}")
            if result.get('financial'):
                print(f"      Total: {result['financial'].get('total', 'N/A')}")
            if result.get('items'):
                print(f"      Items: {len(result['items'])} products found")
            if result.get('ai_enhanced'):
                print(f"      ✅ AI Enhancement: Success")
        
    except Exception as e:
        print(f"   ❌ Hugging Face test failed: {str(e)}")
    
    # Test fallback mode (no API)
    print("\n2. Testing Fallback Mode (No API)...")
    try:
        analyzer_local = AIReceiptAnalyzer(provider="local")
        result = analyzer_local.analyze_receipt_with_ai(sample_ocr_text, enhance_mode="full")
        
        if result:
            print(f"   Store: {result.get('store_info', {}).get('name', 'N/A')}")
            print(f"   Date: {result.get('transaction', {}).get('date', 'N/A')}")
            print(f"   Total: {result.get('financial', {}).get('total', 'N/A')}")
            print(f"   Payment: {result.get('payment', {}).get('method', 'N/A')}")
            print(f"   Items: {len(result.get('items', []))} products")
            
            if not result.get('ai_enhanced', True):
                print("   ℹ️ Using rule-based fallback (no AI)")
    
    except Exception as e:
        print(f"   ❌ Fallback test failed: {str(e)}")
    
    # Test integration with OCR service
    print("\n3. Testing OCR Service Integration...")
    try:
        from apps.documents.ocr_service import OCRProcessor
        
        processor = OCRProcessor()
        if processor.ai_enhancer:
            print("   ✅ AI Enhancer initialized in OCR processor")
            print(f"   Provider: {processor.ai_enhancer.provider}")
        else:
            print("   ⚠️ AI Enhancer not available in OCR processor")
            
    except Exception as e:
        print(f"   ❌ OCR integration test failed: {str(e)}")
    
    # Test batch processing
    print("\n4. Testing Batch Processing...")
    try:
        from apps.documents.models import Document
        
        # Get sample documents
        sample_docs = Document.objects.filter(
            ocr_text__isnull=False
        ).exclude(ocr_text='')[:3]
        
        if sample_docs.exists():
            print(f"   Found {sample_docs.count()} documents to test")
            
            # Test batch analysis
            analyzer = AIReceiptAnalyzer(provider="huggingface")
            docs_data = [
                {'id': doc.id, 'ocr_text': doc.ocr_text[:500]}
                for doc in sample_docs
            ]
            
            results = analyzer.batch_analyze_documents(docs_data)
            print(f"   Processed: {len(results)} documents")
            
            for result in results[:2]:  # Show first 2
                doc_id = result.get('document_id')
                if result.get('error'):
                    print(f"   - Doc {doc_id}: ❌ {result['error']}")
                else:
                    print(f"   - Doc {doc_id}: ✅ AI Enhanced")
        else:
            print("   No documents with OCR text found for testing")
            
    except Exception as e:
        print(f"   ❌ Batch processing test failed: {str(e)}")
    
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print("✅ AI OCR Enhancer module loaded successfully")
    print("ℹ️ For production use, set HUGGINGFACE_API_KEY environment variable")
    print("ℹ️ Fallback mode works without API for basic extraction")
    
    # Check environment
    if os.getenv('HUGGINGFACE_API_KEY'):
        print("✅ HUGGINGFACE_API_KEY is set")
    else:
        print("⚠️ HUGGINGFACE_API_KEY not set - using fallback mode")
    
    if os.getenv('MISTRAL_API_KEY'):
        print("✅ MISTRAL_API_KEY is set")
    else:
        print("ℹ️ MISTRAL_API_KEY not set (optional, requires paid account)")

if __name__ == "__main__":
    test_ai_ocr()