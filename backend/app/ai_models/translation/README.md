# Translation Models

Supports translation between English, Tamil, Hindi, and Telugu.

## Options

| Provider | Setup |
|---|---|
| Google Translate (deep-translator) | `pip install deep-translator` |
| LibreTranslate (self-hosted) | Set `TRANSLATION_PROVIDER=libretranslate` in `.env` |
| Helsinki-NLP (offline) | Place model weights here and update `translation_service.py` |
