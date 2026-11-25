import asyncio
from pathlib import Path
from typing import Optional

from app.core.config import settings


class OCRService:
    """
    OCR service that extracts text from prescription images.
    Uses Google Cloud Vision when credentials are configured,
    otherwise falls back to pytesseract for local/offline use.
    """

    async def extract_text(self, file_path: str) -> str:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._extract_sync, file_path)

    def _extract_sync(self, file_path: str) -> str:
        if settings.GOOGLE_CLOUD_CREDENTIALS:
            return self._google_vision_ocr(file_path)
        return self._tesseract_ocr(file_path)

    def _google_vision_ocr(self, file_path: str) -> str:
        try:
            from google.cloud import vision
            import os
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = settings.GOOGLE_CLOUD_CREDENTIALS

            client = vision.ImageAnnotatorClient()
            with open(file_path, "rb") as f:
                content = f.read()
            image = vision.Image(content=content)
            response = client.text_detection(image=image)
            if response.error.message:
                raise RuntimeError(response.error.message)
            texts = response.text_annotations
            return texts[0].description if texts else ""
        except Exception as e:
            # Fall back to tesseract
            return self._tesseract_ocr(file_path)

    def _tesseract_ocr(self, file_path: str) -> str:
        try:
            import pytesseract
            from PIL import Image

            # On Windows, pytesseract cannot find the Tesseract binary from PATH
            # when the server is started from a virtual environment. Set the
            # absolute path explicitly. The fallback covers Linux/macOS where
            # Tesseract is on PATH as 'tesseract'.
            import os
            WINDOWS_TESSERACT = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
            if os.path.isfile(WINDOWS_TESSERACT):
                pytesseract.pytesseract.tesseract_cmd = WINDOWS_TESSERACT

            img = Image.open(file_path)
            # Try multiple languages: English + Indic scripts
            text = pytesseract.image_to_string(img, lang="eng")
            return text.strip()
        except Exception as e:
            return f"[OCR unavailable: {str(e)}]"
