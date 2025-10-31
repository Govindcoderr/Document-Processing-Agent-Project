# # backend/ocr_extractor.py
# import pytesseract
# from pdf2image import convert_from_bytes
# from PIL import Image, ImageEnhance, ImageFilter, UnidentifiedImageError
# import io
# import os
# import cv2
# import numpy as np

# # ✅ Configure paths
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
# POPPLER_PATH = r"C:\poppler-25.07.0\Library\bin"


# def preprocess_image(image_bytes: bytes) -> Image.Image:
#     """
#     Preprocess image bytes using OpenCV adaptive thresholding,
#     and fallback to Pillow enhancements if OpenCV fails.
#     """
#     try:
#         # 🔹 Try OpenCV
#         nparr = np.frombuffer(image_bytes, np.uint8)
#         img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
#         gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#         processed = cv2.adaptiveThreshold(
#             gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 15
#         )
#         return Image.fromarray(processed)
#     except Exception as e:
#         # 🔹 Fallback to Pillow
#         print("⚠️ CV2 preprocessing failed, using Pillow:", e)
#         image = Image.open(io.BytesIO(image_bytes)).convert("L")
#         enhancer = ImageEnhance.Contrast(image)
#         image = enhancer.enhance(2.0)
#         return image.filter(ImageFilter.SHARPEN)


# def extract_text_from_image(file_bytes: bytes) -> str:
#     """
#     Extract text from uploaded invoice (PDF or image),
#     with intelligent preprocessing for better OCR accuracy.
#     """
#     text = ""

#     # Try PDF first
#     try:
#         images = convert_from_bytes(file_bytes, poppler_path=POPPLER_PATH)
#         for img in images:
#             img_bytes = io.BytesIO()
#             img.save(img_bytes, format="PNG")  # Convert each page to bytes
#             processed = preprocess_image(img_bytes.getvalue())
#             text += pytesseract.image_to_string(processed)
#         if text.strip():
#             print("✅ Extracted text using OCR on PDF")
#             return text
#     except Exception as e:
#         print("⚠️ PDF read failed, trying as image:", e)

#     # Try Image next
#     try:
#         processed = preprocess_image(file_bytes)
#         text += pytesseract.image_to_string(processed)
#         if text.strip():
#             print("✅ Extracted text using OCR on image")
#             return text
#     except UnidentifiedImageError:
#         raise RuntimeError("Uploaded file is neither a valid PDF nor an image.")
#     except Exception as e:
#         raise RuntimeError(f"OCR failed: {e}")

#     raise RuntimeError("No text detected in the image.")



import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image, ImageEnhance, ImageFilter, UnidentifiedImageError
import io, os, cv2, numpy as np
from fastapi import HTTPException

# ✅ Configure paths
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
POPPLER_PATH = r"C:\poppler-25.07.0\Library\bin"
# Add poppler to PATH (temporary runtime fix)
os.environ["PATH"] += os.pathsep + POPPLER_PATH


def preprocess_image(image_bytes: bytes) -> Image.Image:
    """
    Preprocess image bytes for OCR:
    1️⃣ Try OpenCV adaptive thresholding (best for faded/uneven images)
    2️⃣ Fallback to Pillow if OpenCV fails
    """
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("Empty image input for OpenCV")

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        processed = cv2.adaptiveThreshold(
            gray, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 31, 15
        )
        return Image.fromarray(processed)

    except Exception as e:
        print("⚠️ CV2 preprocessing failed, using Pillow:", e)
        image = Image.open(io.BytesIO(image_bytes)).convert("L")
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)
        return image.filter(ImageFilter.SHARPEN)


def extract_text_from_image(file_bytes: bytes) -> str:
    """
    Extract text from uploaded invoice (PDF or image)
    with preprocessing for best OCR accuracy.
    """
    text = ""
    print(f"📂 Uploaded file size: {len(file_bytes)} bytes")

    # ---------- PDF Handling ----------
    try:
        images = convert_from_bytes(file_bytes, poppler_path=POPPLER_PATH)
        for img in images:
            img_bytes = io.BytesIO()
            img.save(img_bytes, format="PNG")
            processed = preprocess_image(img_bytes.getvalue())
            text += pytesseract.image_to_string(processed)
        if text.strip():
            print("✅ Extracted text using OCR on PDF")
            return text
    except Exception as e:
        print("⚠️ PDF read failed, trying as image:", e)

    # ---------- Image Handling ----------
    try:
        processed = preprocess_image(file_bytes)
        text += pytesseract.image_to_string(processed)
        if text.strip():
            print("✅ Extracted text using OCR on image")
            return text
    except UnidentifiedImageError:
        raise HTTPException(status_code=400, detail="Uploaded file is neither a valid PDF nor an image.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"OCR error: {e}")

    raise HTTPException(status_code=400, detail="No text detected in the image.")
