import asyncio
import base64
from typing import Optional
from app.core.config import settings

LANGUAGE_CODE_MAP = {
    "en": "en-IN",
    "ta": "ta-IN",
    "hi": "hi-IN",
    "te": "te-IN",
}


class SpeechService:
    """
    Speech-to-text and text-to-speech service.
    Uses OpenAI Whisper for transcription and gTTS for synthesis as defaults.
    """

    async def transcribe(self, audio_base64: str, language: str = "en") -> str:
        """Convert base64-encoded audio to text."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._transcribe_sync, audio_base64, language)

    def _transcribe_sync(self, audio_base64: str, language: str) -> str:
        if settings.OPENAI_API_KEY:
            return self._whisper_transcribe(audio_base64, language)
        return "[Speech recognition unavailable – configure OPENAI_API_KEY]"

    def _whisper_transcribe(self, audio_base64: str, language: str) -> str:
        try:
            import openai
            import tempfile
            import os

            client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
            audio_bytes = base64.b64decode(audio_base64)

            with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as f:
                f.write(audio_bytes)
                tmp_path = f.name

            try:
                with open(tmp_path, "rb") as audio_file:
                    result = client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        language=language if language != "en" else None,
                    )
                return result.text
            finally:
                os.unlink(tmp_path)
        except Exception as e:
            return f"[Transcription failed: {str(e)}]"

    async def synthesize(self, text: str, language: str = "en") -> Optional[str]:
        """Convert text to base64-encoded audio using gTTS."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._synthesize_sync, text, language)

    def _synthesize_sync(self, text: str, language: str) -> Optional[str]:
        try:
            from gtts import gTTS
            import io

            tts = gTTS(text=text, lang=language, slow=False)
            buf = io.BytesIO()
            tts.write_to_fp(buf)
            buf.seek(0)
            return base64.b64encode(buf.read()).decode("utf-8")
        except Exception:
            return None
