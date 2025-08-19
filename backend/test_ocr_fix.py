#!/usr/bin/env python
"""
Test script to verify OCR functionality fixes
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unibos_backend.settings.emergency')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from apps.documents.ocr_service import OCRProcessor
from apps.documents.utils import ThumbnailGenerator, PaginationHelper
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('test_ocr')

def test_ocr_processor():
    """Test OCR processor functionality"""
    print("\n=== Testing OCR Processor ===")
    
    processor = OCRProcessor()
    print(f"Tesseract Available: {processor.tesseract_available}")
    print(f"OpenCV Available: {processor.cv2_available}")
    
    # Test with a sample image if available
    sample_images = [
        '/Users/berkhatirli/Desktop/unibos/backend/documents/2025/08/scanned_20250807_1840_0001.jpg'
    ]
    
    for image_path in sample_images:
        if os.path.exists(image_path):
            print(f"\nTesting OCR on: {os.path.basename(image_path)}")
            
            # Test for different document types
            for doc_type in ['receipt', 'invoice', 'other']:
                print(f"\n  Document Type: {doc_type}")
                result = processor.process_document(image_path, document_type=doc_type, force_ocr=True)
                
                if result['success']:
                    print(f"    ✓ OCR Success")
                    print(f"    - Text Length: {len(result.get('ocr_text', ''))}")
                    print(f"    - Confidence: {result.get('confidence', 0):.1f}%")
                    print(f"    - OCR Method: {result.get('ocr_method', 'unknown')}")
                    
                    # Show first 200 chars of extracted text
                    if result.get('ocr_text'):
                        preview = result['ocr_text'][:200].replace('\n', ' ')
                        print(f"    - Text Preview: {preview}...")
                else:
                    print(f"    ✗ OCR Failed: {result.get('error', 'Unknown error')}")
            
            break  # Test only first available image
    else:
        print("No sample images found for testing")
    
    return processor.tesseract_available

def test_thumbnail_generator():
    """Test thumbnail generator"""
    print("\n=== Testing Thumbnail Generator ===")
    
    generator = ThumbnailGenerator()
    print(f"PIL Available: {generator.pil_available}")
    
    if not generator.pil_available:
        print("✗ PIL not available - thumbnail generation disabled")
        return False
    
    # Test with a sample image
    sample_images = [
        '/Users/berkhatirli/Desktop/unibos/backend/documents/2025/08/scanned_20250807_1840_0001.jpg'
    ]
    
    for image_path in sample_images:
        if os.path.exists(image_path):
            print(f"\nGenerating thumbnail for: {os.path.basename(image_path)}")
            
            output_path = '/tmp/test_thumbnail.jpg'
            result = generator.generate_thumbnail(image_path, output_path)
            
            if result:
                print(f"✓ Thumbnail generated: {result}")
                if os.path.exists(result):
                    size = os.path.getsize(result)
                    print(f"  - File size: {size:,} bytes")
                    os.remove(result)  # Clean up
            else:
                print("✗ Thumbnail generation failed")
            
            break
    
    return generator.pil_available

def test_pagination_helper():
    """Test pagination helper"""
    print("\n=== Testing Pagination Helper ===")
    
    # Create a mock request object
    class MockRequest:
        def __init__(self, params):
            self.GET = params
    
    # Test different page sizes
    test_cases = [
        ({'page_size': '10'}, 10),
        ({'page_size': '25'}, 25),
        ({'page_size': '50'}, 50),
        ({'page_size': '100'}, 100),
        ({'page_size': '999'}, 100),  # Should clamp to max allowed
        ({}, 20),  # Default
    ]
    
    for params, expected in test_cases:
        request = MockRequest(params)
        result = PaginationHelper.get_page_size(request)
        status = "✓" if result == expected else "✗"
        print(f"{status} page_size={params.get('page_size', 'default')} -> {result} (expected {expected})")
    
    return True

def main():
    """Run all tests"""
    print("=" * 60)
    print("UNIBOS OCR Fix Verification")
    print("=" * 60)
    
    results = {
        'OCR Processor': test_ocr_processor(),
        'Thumbnail Generator': test_thumbnail_generator(),
        'Pagination Helper': test_pagination_helper()
    }
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name}: {status}")
    
    # Overall assessment
    all_passed = all(results.values())
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ ALL TESTS PASSED - OCR functionality is working!")
    else:
        print("⚠ SOME TESTS FAILED - Manual intervention may be needed")
        print("\nRecommendations:")
        if not results['OCR Processor']:
            print("- Install Tesseract: brew install tesseract tesseract-lang")
            print("- Install Python packages: pip install pytesseract pillow opencv-python-headless")
        if not results['Thumbnail Generator']:
            print("- Install Pillow: pip install pillow")
    print("=" * 60)

if __name__ == '__main__':
    main()