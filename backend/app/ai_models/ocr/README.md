# OCR Models

Place custom OCR model weights here (e.g., fine-tuned TrOCR for handwritten prescriptions).

## Options

| Provider | Notes |
|---|---|
| Google Cloud Vision | Set `GOOGLE_CLOUD_CREDENTIALS` in `.env` |
| Tesseract (local) | Install `tesseract-ocr` + `pytesseract` |
| Custom TrOCR | Place model weights in this folder and update `ocr_service.py` |
