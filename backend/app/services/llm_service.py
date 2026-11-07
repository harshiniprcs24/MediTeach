from typing import List, Dict, Optional
from app.core.config import settings

SYSTEM_PROMPT = """You are MediTeach AI, a compassionate and knowledgeable health assistant 
specializing in medication guidance and general health education. You help patients understand 
their prescriptions, medications, dosages, and general health queries.

Guidelines:
- Always remind users to consult a qualified doctor for medical decisions.
- Provide clear, simple explanations suitable for patients with limited medical knowledge.
- Support multilingual responses when the user writes in Tamil, Hindi, or Telugu.
- Never diagnose conditions – only provide educational information.
- Be empathetic, patient, and easy to understand.
"""


class LLMService:
    """
    LLM service using OpenAI ChatCompletion.
    Falls back to a stub response when no API key is configured.
    """

    async def chat(self, message: str, history: List[Dict[str, str]]) -> str:
        if not settings.OPENAI_API_KEY:
            return self._stub_reply(message)

        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            for h in history[-10:]:
                role = "user" if h["role"] == "user" else "assistant"
                messages.append({"role": role, "content": h["content"]})
            messages.append({"role": "user", "content": message})

            response = await client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=messages,
                max_tokens=600,
                temperature=0.7,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"I'm sorry, I encountered an error: {str(e)}. Please try again."

    async def parse_prescription(self, raw_text: str, language: str = "en") -> dict:
        """Use LLM to parse OCR text into structured prescription data."""
        if not settings.OPENAI_API_KEY:
            return {"title": None, "doctor": None, "medicines": [], "instructions": None}

        from openai import AsyncOpenAI
        import json

        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        prompt = f"""Extract structured information from this prescription text.
Return a JSON object with keys: title, doctor, medicines (list of {{name, dosage, frequency, duration, instructions}}), instructions.

Prescription text:
{raw_text}

Return only valid JSON, no markdown."""

        try:
            response = await client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.1,
            )
            content = response.choices[0].message.content.strip()
            return json.loads(content)
        except Exception:
            return {"title": None, "doctor": None, "medicines": [], "instructions": raw_text}

    async def generate_assessment(self, symptoms: List[str], severity: int, duration: int, language: str = "en") -> dict:
        """Generate a health assessment from symptoms."""
        if not settings.OPENAI_API_KEY:
            return self._stub_assessment(symptoms, severity)

        from openai import AsyncOpenAI
        import json

        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        severity_map = {1: "mild", 2: "moderate", 3: "severe"}
        prompt = f"""You are a medical AI. Based on these symptoms, provide a structured health assessment.

Symptoms: {', '.join(symptoms)}
Severity: {severity_map.get(severity, 'moderate')}
Duration: {duration} days

Return JSON with keys:
- urgency: "low" | "medium" | "high"
- summary: 2-3 sentence plain-language assessment
- possibleConditions: list of up to 3 possible conditions (educational only)
- recommendations: list of 3-5 practical recommendations

Return only valid JSON."""

        try:
            response = await client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=600,
                temperature=0.3,
            )
            return json.loads(response.choices[0].message.content.strip())
        except Exception:
            return self._stub_assessment(symptoms, severity)

    def _stub_reply(self, message: str) -> str:
        return (
            "Thank you for your question. I'm here to help you understand your medications "
            "and health concerns. For a full response, please ensure the AI service is configured. "
            "Always consult your doctor for medical advice."
        )

    def _stub_assessment(self, symptoms: list, severity: int) -> dict:
        urgency = "low" if severity == 1 else "medium" if severity == 2 else "high"
        return {
            "urgency": urgency,
            "summary": "Based on your symptoms, it is recommended to monitor your condition. This is an informational assessment only.",
            "possibleConditions": ["Common cold", "Viral infection"],
            "recommendations": [
                "Stay hydrated and get adequate rest.",
                "Monitor your temperature regularly.",
                "Consult a doctor if symptoms worsen or persist beyond 3 days.",
            ],
        }
