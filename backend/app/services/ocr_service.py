"""
OCR service for extracting text from invoices.
"""
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
from typing import Optional
import io
from app.core.config import settings

# Set Tesseract command path if configured
if settings.TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD


class OCRService:
    """Service for OCR text extraction."""
    
    @staticmethod
    def extract_text_from_image(image: Image.Image) -> str:
        """Extract text from a PIL Image."""
        try:
            text = pytesseract.image_to_string(image, lang='nor+eng')
            return text.strip()
        except Exception as e:
            raise Exception(f"OCR extraction failed: {str(e)}")
    
    @staticmethod
    def extract_text_from_pdf(pdf_path: str) -> str:
        """Extract text from a PDF file."""
        try:
            # Convert PDF to images
            images = convert_from_path(pdf_path, dpi=300)
            
            # Extract text from each page
            all_text = []
            for image in images:
                text = OCRService.extract_text_from_image(image)
                all_text.append(text)
            
            return "\n\n".join(all_text)
        except Exception as e:
            raise Exception(f"PDF OCR extraction failed: {str(e)}")
    
    @staticmethod
    def extract_text(file_path: str, mime_type: str) -> str:
        """Extract text from a file based on its MIME type."""
        if mime_type == "application/pdf":
            return OCRService.extract_text_from_pdf(file_path)
        elif mime_type.startswith("image/"):
            image = Image.open(file_path)
            return OCRService.extract_text_from_image(image)
        else:
            raise ValueError(f"Unsupported file type: {mime_type}")


ocr_service = OCRService()
