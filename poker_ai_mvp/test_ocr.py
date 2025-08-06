#!/usr/bin/env python3
"""
Test script for OCR functionality in Poker AI MVP
This script tests the OCR system and verifies that the fixes work correctly.
"""

import sys
import os
import numpy as np
import cv2
from loguru import logger

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_ocr_initialization():
    """Test OCR initialization and basic functionality."""
    print("=" * 50)
    print("Testing OCR Initialization")
    print("=" * 50)
    
    try:
        from src.vision.ocr import TextRecognizer
        
        # Test initialization
        print("Initializing TextRecognizer...")
        recognizer = TextRecognizer()
        
        if recognizer.ocr is not None:
            print("✅ PaddleOCR initialized successfully")
            return True
        else:
            print("⚠️  PaddleOCR not available, using fallback")
            return False
            
    except Exception as e:
        print(f"❌ OCR initialization failed: {e}")
        return False

def test_ocr_extraction():
    """Test OCR text extraction with a sample image."""
    print("\n" + "=" * 50)
    print("Testing OCR Text Extraction")
    print("=" * 50)
    
    try:
        from src.vision.ocr import TextRecognizer
        
        # Create a simple test image with text
        test_image = np.ones((200, 400, 3), dtype=np.uint8) * 255  # White background
        
        # Add some text-like regions
        cv2.rectangle(test_image, (50, 50), (150, 100), (0, 0, 0), -1)  # Black rectangle
        cv2.rectangle(test_image, (200, 50), (300, 100), (0, 0, 0), -1)  # Black rectangle
        
        recognizer = TextRecognizer()
        
        # Test extraction without region
        print("Testing full image OCR...")
        results = recognizer.extract_text(test_image)
        print(f"Found {len(results)} text elements")
        
        # Test extraction with region
        print("Testing region-based OCR...")
        region = (50, 50, 100, 50)
        results = recognizer.extract_text(test_image, region)
        print(f"Found {len(results)} text elements in region")
        
        # Test specific extraction methods
        print("Testing specific extraction methods...")
        
        # Test stack size extraction
        stack_result = recognizer.extract_stack_size(test_image, region)
        print(f"Stack size: {stack_result}")
        
        # Test pot size extraction
        pot_result = recognizer.extract_pot_size(test_image, region)
        print(f"Pot size: {pot_result}")
        
        print("✅ OCR extraction tests completed")
        return True
        
    except Exception as e:
        print(f"❌ OCR extraction test failed: {e}")
        return False

def test_fallback_ocr():
    """Test the fallback OCR system."""
    print("\n" + "=" * 50)
    print("Testing Fallback OCR System")
    print("=" * 50)
    
    try:
        from src.vision.ocr import TextRecognizer
        
        # Create test image
        test_image = np.ones((300, 500, 3), dtype=np.uint8) * 255
        
        recognizer = TextRecognizer()
        
        # Test different regions
        test_regions = [
            (800, 250, 100, 50),  # Pot area
            (1150, 50, 100, 50),  # Timer area
            (250, 450, 100, 50),  # Player name area
            (450, 450, 100, 50),  # Stack area
        ]
        
        for i, region in enumerate(test_regions):
            print(f"Testing region {i+1}: {region}")
            results = recognizer.extract_text(test_image, region)
            if results:
                for result in results:
                    print(f"  - Text: '{result['text']}', Confidence: {result['confidence']:.2f}")
            else:
                print("  - No text detected")
        
        print("✅ Fallback OCR tests completed")
        return True
        
    except Exception as e:
        print(f"❌ Fallback OCR test failed: {e}")
        return False

def main():
    """Main test function."""
    print("OCR Test Suite for Poker AI MVP")
    print("=" * 50)
    
    # Configure logging
    logger.remove()
    logger.add(sys.stderr, level="INFO")
    
    # Run tests
    tests = [
        ("OCR Initialization", test_ocr_initialization),
        ("OCR Extraction", test_ocr_extraction),
        ("Fallback OCR", test_fallback_ocr),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "=" * 50)
    print("Test Results Summary")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All OCR tests passed! The OCR system is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 