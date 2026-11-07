from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List

from app.database.connection import get_db
from app.core.security import get_current_user_id
from app.schemas.assessment import AssessmentRequest, AssessmentOut, AssessmentListItem
from app.services.assessment_service import AssessmentService
from app.models.assessment import Assessment

router = APIRouter()


@router.post("/submit", response_model=AssessmentOut, status_code=status.HTTP_201_CREATED)
async def submit_assessment(
    payload: AssessmentRequest,
    language: str = Query("en"),
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Submit symptoms and receive an AI-powered health assessment."""
    service = AssessmentService(db)
    return await service.create_assessment(user_id, payload, language)


@router.get("/history", response_model=List[AssessmentListItem])
async def get_history(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Get past assessments for the current user."""
    result = await db.execute(
        select(Assessment)
        .where(Assessment.user_id == user_id)
        .order_by(desc(Assessment.created_at))
        .limit(limit)
    )
    return result.scalars().all()


@router.get("/{assessment_id}", response_model=AssessmentOut)
async def get_assessment(
    assessment_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Get a specific assessment result."""
    result = await db.execute(
        select(Assessment).where(
            Assessment.id == assessment_id,
            Assessment.user_id == user_id,
        )
    )
    assessment = result.scalar_one_or_none()
    if not assessment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")
    return assessment
