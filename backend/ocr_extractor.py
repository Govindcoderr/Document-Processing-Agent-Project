import os
import pytesseract
from pdf2image import convert_from_bytes
from fastapi import HTTPException
from PIL import Image, ImageEnhance, ImageFilter, UnidentifiedImageError
import io, cv2, numpy as np

#  Configure paths
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
POPPLER_PATH = r"C:\Program Files\poppler-25.07.0\Library\bin"

# Add poppler to PATH
os.environ["PATH"] += os.pathsep + POPPLER_PATH


def preprocess_image(image_bytes: bytes) -> Image.Image:
    """
    Enhance image using OpenCV (if available) for better OCR accuracy.
    Falls back to Pillow if OpenCV fails.
    """
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("Empty image input for OpenCV")

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        processed = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 15
        )
        return Image.fromarray(processed)

    except Exception as e:
        print("OpenCV preprocessing failed, using Pillow:", e)
        image = Image.open(io.BytesIO(image_bytes)).convert("L")
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)
        return image.filter(ImageFilter.SHARPEN)


def extract_text_from_image(file_bytes: bytes) -> str:
    """
    Extract text from uploaded invoice (PDF or image)
    with preprocessing for best OCR accuracy.
    Works for: PDF, PNG, JPG, JPEG.
    """
    text = ""
    print(f" Uploaded file size: {len(file_bytes)} bytes")

    # ---------- Try PDF First ----------
    try:
        images = convert_from_bytes(file_bytes, poppler_path=POPPLER_PATH)
        print(f"PDF converted to {len(images)} image(s).")
        for img in images:
            img_bytes = io.BytesIO()
            img.save(img_bytes, format="PNG")
            processed = preprocess_image(img_bytes.getvalue())
            text += pytesseract.image_to_string(processed)
        if text.strip():
            print(" Extracted text using OCR on PDF")
            return text
    except Exception as e:
        print(" PDF read failed, trying as image instead:", e)

    # ---------- Try Image Next ----------
    try:
        processed = preprocess_image(file_bytes)
        text += pytesseract.image_to_string(processed)
        if text.strip():
            print(" Extracted text using OCR on image")
            return text
    except UnidentifiedImageError:
        raise HTTPException(status_code=400, detail="Uploaded file is neither a valid PDF nor an image.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"OCR error: {e}")

    raise HTTPException(status_code=400, detail="No text detected in the file.")
