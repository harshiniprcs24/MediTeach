import asyncio
from typing import Optional
from app.core.config import settings

SUPPORTED_LANGUAGES = {"en", "ta", "hi", "te"}


class TranslationService:
    """
    Translates text between languages.
    Uses Google Translate API when configured, otherwise returns the original text.
    """

    async def translate(self, text: str, target_language: str, source_language: str = "en") -> str:
        if target_language == source_language or target_language not in SUPPORTED_LANGUAGES:
            return text
        if not text or not text.strip():
            return text

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self._translate_sync, text, target_language, source_language
        )

    def _translate_sync(self, text: str, target: str, source: str) -> str:
        try:
            from deep_translator import GoogleTranslator
            translated = GoogleTranslator(source=source, target=target).translate(text)
            return translated or text
        except ImportError:
            return text
        except Exception:
            return text

    async def translate_medicines(self, medicines: list, target_language: str) -> list:
        """Translate a list of medicine dicts to the target language."""
        if target_language == "en":
            return medicines

        translated = []
        for med in medicines:
            t_med = dict(med)
            if med.get("instructions"):
                t_med["instructions"] = await self.translate(med["instructions"], target_language)
            translated.append(t_med)
        return translated
