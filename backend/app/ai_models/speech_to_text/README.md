# Speech-to-Text Models

Converts patient voice queries to text in supported languages.

## Options

| Provider | Setup |
|---|---|
| OpenAI Whisper (API) | Set `OPENAI_API_KEY` in `.env` |
| Faster-Whisper (local) | `pip install faster-whisper`, place weights here |
| Vosk (offline) | Download language model and update `speech_service.py` |

## Supported Languages
- English (en-IN)
- Tamil (ta-IN)
- Hindi (hi-IN)
- Telugu (te-IN)
