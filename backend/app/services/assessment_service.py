from sqlalchemy.ext.asyncio import AsyncSession

from app.models.assessment import Assessment
from app.schemas.assessment import AssessmentRequest, AssessmentOut
from app.services.llm_service import LLMService


class AssessmentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.llm = LLMService()

    async def create_assessment(
        self, user_id: str, payload: AssessmentRequest, language: str = "en"
    ) -> AssessmentOut:
        # Generate AI assessment
        result = await self.llm.generate_assessment(
            payload.symptoms, payload.severity, payload.duration, language
        )

        assessment = Assessment(
            user_id=user_id,
            symptoms=payload.symptoms,
            severity=payload.severity,
            duration_days=payload.duration,
            urgency=result.get("urgency", "low"),
            summary=result.get("summary"),
            possible_conditions=result.get("possibleConditions", []),
            recommendations=result.get("recommendations", []),
            language=language,
        )
        self.db.add(assessment)
        await self.db.flush()
        await self.db.refresh(assessment)
        return assessment
