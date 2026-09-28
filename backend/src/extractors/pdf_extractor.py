import logging
from typing import Dict, Any, Optional
import pymupdf as fitz  # PyMuPDF
import easyocr
import numpy as np
import io
from PIL import Image

logger = logging.getLogger(__name__)

import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Initialize EasyOCR reader (loads model once)
try:
    # verbose=False prevents the progress bar from crashing the Windows console with unicode errors
    ocr_reader = easyocr.Reader(['en'], gpu=False, verbose=False)
except Exception as e:
    logger.error(f"Failed to init EasyOCR: {e}")
    ocr_reader = None

def extract_text_from_pdf(file_bytes: bytes) -> Dict[str, Any]:
    """
    Extracts text from a PDF file while preserving page boundaries.
    
    Args:
        file_bytes (bytes): The raw bytes of the uploaded PDF file.
        
    Returns:
        Dict[str, Any]: A dictionary containing extraction status, 
                        document metadata, and the extracted text per page.
    """
    try:
        if not file_bytes:
            return {
                "success": False,
                "error": "Empty file provided.",
                "text": "",
                "pages": []
            }

        # Open the document using PyMuPDF from bytes
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
        except Exception as e:
            logger.error(f"Failed to open PDF: {e}")
            return {
                "success": False,
                "error": "Invalid or unreadable PDF file.",
                "text": "",
                "pages": []
            }
            
        if doc.page_count == 0:
            return {
                "success": False,
                "error": "PDF file has no pages.",
                "text": "",
                "pages": []
            }

        extracted_pages = []
        full_text = []

        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            text = page.get_text("text").strip()
            
            # If standard text extraction fails (e.g., scanned PDF/image), use OCR
            if not text and ocr_reader is not None:
                try:
                    logger.info(f"No text found on page {page_num + 1}, attempting OCR...")
                    # Render the page to a high-resolution pixmap
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                    img_bytes = pix.tobytes("png")
                    img = Image.open(io.BytesIO(img_bytes))
                    img_np = np.array(img)
                    
                    # Perform OCR with EasyOCR
                    result = ocr_reader.readtext(img_np, detail=0, paragraph=True)
                    ocr_text = "\n".join(result).strip()
                    if ocr_text:
                        text = ocr_text
                except Exception as ocr_err:
                    logger.warning(f"OCR failed on page {page_num + 1}: {ocr_err}")

            # Store per-page data
            extracted_pages.append({
                "page_number": page_num + 1,
                "text": text
            })
            if text:
                full_text.append(text)

        
        combined_text = "\n\n--- PAGE BREAK ---\n\n".join(full_text)
        page_count = doc.page_count
        doc.close()

        if not combined_text.strip():
            return {
                "success": False,
                "error": "No extractable text found in PDF (might be scanned or image-based).",
                "text": "",
                "pages": extracted_pages
            }

        return {
            "success": True,
            "metadata": {
                "page_count": page_count
            },
            "text": combined_text,
            "pages": extracted_pages
        }

    except Exception as e:
        logger.exception(f"Unexpected error during PDF extraction: {e}")
        return {
            "success": False,
            "error": f"Internal extraction error: {str(e)}",
            "text": "",
            "pages": []
        }
