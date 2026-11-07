from sqlalchemy.ext.asyncio import AsyncSession
from app.services.llm_service import LLMService


class MedicineService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.llm = LLMService()

    async def parse_prescription_text(self, raw_text: str, language: str = "en") -> dict:
        """Parse raw OCR text into structured prescription data using LLM."""
        return await self.llm.parse_prescription(raw_text, language)
