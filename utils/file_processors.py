# utils/file_processors.py
import streamlit as st
from PIL import Image
import pytesseract
import cv2
import numpy as np
import os
from typing import Optional, Tuple, Dict
import tempfile
from pypdf import PdfReader
import warnings


warnings.filterwarnings('ignore', category=UserWarning)

warnings.filterwarnings('ignore', message='.*torch.classes.*')

# Set Tesseract path
TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

def enhance_image(image: np.ndarray, enhancement_type: str = 'default') -> np.ndarray:
    """Enhanced image preprocessing with multiple options"""
    if enhancement_type == 'document':
        # Optimize for document scanning
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        denoised = cv2.fastNlMeansDenoising(gray)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(denoised)
        thresh = cv2.adaptiveThreshold(
            enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )
        return thresh
        
    elif enhancement_type == 'handwriting':
        # Optimize for handwritten text
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        bilateral = cv2.bilateralFilter(enhanced, 9, 75, 75)
        thresh = cv2.adaptiveThreshold(
            bilateral, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )
        return thresh
        
    else:
        # Default enhancement
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        denoised = cv2.fastNlMeansDenoising(gray)
        thresh = cv2.adaptiveThreshold(
            denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )
        return thresh

def process_image(image: Image.Image, enhancement_type: str = 'default') -> Tuple[Optional[str], float, Dict]:
    """Process image with OCR and return text, confidence, and stats"""
    try:
        # Convert PIL Image to CV2 format
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Show preprocessing steps
        with st.expander("View Processing Steps"):
            col1, col2 = st.columns(2)
            with col1:
                st.image(cv_image, caption="Original Image")
            
            # Enhance image
            processed = enhance_image(cv_image, enhancement_type)
            with col2:
                st.image(processed, caption=f"Enhanced ({enhancement_type})")
        
        # Perform OCR
        data = pytesseract.image_to_data(
            processed, output_type=pytesseract.Output.DICT
        )
        
        # Calculate confidence
        confidences = [int(conf) for conf in data['conf'] if conf != '-1']
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        # Extract text
        text = pytesseract.image_to_string(processed)
        
        if text.strip():
            st.success(f"Text extracted with {avg_confidence:.2f}% confidence")
            
            # Show OCR details
            with st.expander("OCR Details"):
                st.json({
                    "confidence": avg_confidence,
                    "word_count": len(data['text']),
                    "enhancement_type": enhancement_type
                })
            
            return text.strip(), avg_confidence, {
                "confidence": avg_confidence,
                "word_count": len(data['text']),
                "enhancement_type": enhancement_type
            }
        else:
            st.warning("No text detected in image")
            return None, 0.0, {"error": "No text detected"}
            
    except Exception as e:
        st.error(f"Error processing image: {str(e)}")
        return None, 0.0, {"error": str(e)}

def process_pdf(pdf_file) -> Optional[str]:
    """Process PDF and extract text"""
    try:
        reader = PdfReader(pdf_file)
        text = ""
        
        # Show progress
        progress_bar = st.progress(0)
        for i, page in enumerate(reader.pages):
            text += page.extract_text()
            progress_bar.progress((i + 1) / len(reader.pages))
        
        if not text.strip():
            st.warning("No text extracted from PDF")
            return None
            
        st.success("PDF processed successfully!")
        return text
    except Exception as e:
        st.error(f"Error processing PDF: {str(e)}")
        return None

def process_video(video_file) -> Optional[str]:
    """Process video and extract information"""
    try:
        import moviepy.editor as mp
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
            tmp_file.write(video_file.read())
            video_path = tmp_file.name

        # Process video
        with mp.VideoFileClip(video_path) as video:
            # Get video information
            info = {
                "duration": video.duration,
                "fps": video.fps,
                "size": video.size,
                "has_audio": video.audio is not None
            }
            
            # Display video information
            st.subheader("Video Information:")
            for key, value in info.items():
                st.write(f"**{key.replace('_', ' ').title()}:** {value}")
        
        # Clean up
        os.unlink(video_path)
        
        return f"Video processed successfully. Duration: {info['duration']} seconds"
    except Exception as e:
        st.error(f"Error processing video: {str(e)}")
        return None

def process_batch_images(images: list) -> list:
    """Process multiple images in batch"""
    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, img_data in enumerate(images):
        try:
            status_text.text(f"Processing image {idx + 1}/{len(images)}: {img_data['name']}")
            
            # Process each image
            text, confidence, stats = process_image(
                img_data['image'],
                img_data.get('enhancement_type', 'default')
            )
            
            results.append({
                'filename': img_data['name'],
                'text': text,
                'confidence': confidence,
                'stats': stats
            })
            
            # Update progress
            progress_bar.progress((idx + 1) / len(images))
            
        except Exception as e:
            results.append({
                'filename': img_data['name'],
                'error': str(e)
            })
    
    status_text.text("Batch processing complete!")
    return results