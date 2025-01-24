import os
import pytesseract
from PIL import Image
import streamlit as st

def test_tesseract_installation():
    print("Testing Tesseract OCR installation...")
    
    # Check Tesseract path
    tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    print(f"\nChecking Tesseract at: {tesseract_path}")
    
    if os.path.exists(tesseract_path):
        print("✅ Tesseract executable found!")
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
        
        # Create a simple test image
        from PIL import Image, ImageDraw
        
        # Create a white image with black text
        img = Image.new('RGB', (200, 50), color='white')
        d = ImageDraw.Draw(img)
        d.text((10,10), "Test OCR", fill='black')
        
        try:
            # Try to extract text
            text = pytesseract.image_to_string(img)
            print(f"\n✅ OCR Test successful!")
            print(f"Extracted text: {text}")
            return True
        except Exception as e:
            print(f"\n❌ OCR Test failed: {str(e)}")
            return False
    else:
        print(f"\n❌ Tesseract not found at: {tesseract_path}")
        return False

if __name__ == "__main__":
    test_tesseract_installation()