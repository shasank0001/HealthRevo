import pytesseract
from PIL import Image
import cv2
import numpy as np
from typing import Optional, Dict
import os
import tempfile
from pdf2image import convert_from_path
from app.config import settings


class OCRService:
    """Optical Character Recognition service for prescription processing."""
    
    def __init__(self):
        # Set tesseract command path if specified
        if settings.tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = settings.tesseract_cmd
    
    async def process_file(self, file_path: str) -> Dict[str, str]:
        """Process uploaded file and extract text using OCR."""
        
        try:
            file_extension = os.path.splitext(file_path)[1].lower()
            
            if file_extension == '.pdf':
                return await self._process_pdf(file_path)
            elif file_extension in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
                return await self._process_image(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "text": ""
            }
    
    async def _process_pdf(self, pdf_path: str) -> Dict[str, str]:
        """Process PDF file by converting to images and running OCR."""
        
        try:
            # Convert PDF to images
            images = convert_from_path(pdf_path, dpi=300)
            
            extracted_text = ""
            
            for i, image in enumerate(images):
                # Save temporary image
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                    image.save(tmp_file.name, 'PNG')
                    
                    # Process the image
                    page_result = await self._process_image(tmp_file.name)
                    
                    if page_result["success"]:
                        extracted_text += f"\\n--- Page {i+1} ---\\n{page_result['text']}\\n"
                    
                    # Clean up temporary file
                    os.unlink(tmp_file.name)
            
            return {
                "success": True,
                "text": extracted_text.strip(),
                "error": None
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"PDF processing failed: {str(e)}",
                "text": ""
            }
    
    async def _process_image(self, image_path: str) -> Dict[str, str]:
        """Process image file and extract text using OCR."""
        
        try:
            # Load image using OpenCV
            image = cv2.imread(image_path)
            
            if image is None:
                raise ValueError("Could not load image file")
            
            # Preprocess image for better OCR results
            processed_image = self._preprocess_image(image)
            
            # Convert back to PIL Image for pytesseract
            processed_pil = Image.fromarray(processed_image)
            
            # Extract text using Tesseract
            extracted_text = pytesseract.image_to_string(
                processed_pil,
                lang='eng',
                config='--psm 6'  # Assume uniform block of text
            )
            
            return {
                "success": True,
                "text": extracted_text.strip(),
                "error": None
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Image processing failed: {str(e)}",
                "text": ""
            }
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image to improve OCR accuracy."""
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        
        # Apply adaptive thresholding for better contrast
        thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        # Apply morphological operations to clean up
        kernel = np.ones((1, 1), np.uint8)
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        # Resize image for better OCR (if too small)
        height, width = cleaned.shape
        if height < 300 or width < 300:
            scale_factor = max(300/height, 300/width)
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            cleaned = cv2.resize(cleaned, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
        
        return cleaned
    
    def get_text_confidence(self, image_path: str) -> float:
        """Get OCR confidence score for the extracted text."""
        
        try:
            image = Image.open(image_path)
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            
            # Calculate average confidence
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            
            if confidences:
                return sum(confidences) / len(confidences)
            else:
                return 0.0
        
        except Exception:
            return 0.0
