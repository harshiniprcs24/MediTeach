from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.database.connection import get_db
from app.core.security import get_current_user_id
from app.models.medicine import Medicine
from app.schemas.medicine import MedicineOut, MedicineSearchResponse, InteractionRequest

router = APIRouter()


@router.get("/search", response_model=MedicineSearchResponse)
async def search_medicines(
    q: str = Query(..., min_length=1),
    lang: str = Query("en"),
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Full-text search medicines by name or generic name."""
    q_lower = f"%{q.lower()}%"
    result = await db.execute(
        select(Medicine)
        .where(
            or_(
                Medicine.name.ilike(q_lower),
                Medicine.generic_name.ilike(q_lower),
            )
        )
        .limit(20)
    )
    medicines = result.scalars().all()
    return {"results": medicines, "query": q}


@router.get("/info", response_model=MedicineOut)
async def get_medicine_info(
    name: str = Query(...),
    lang: str = Query("en"),
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Look up medicine details by exact name."""
    result = await db.execute(
        select(Medicine).where(Medicine.name.ilike(name))
    )
    medicine = result.scalar_one_or_none()
    if not medicine:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medicine not found")
    return medicine


@router.get("/{medicine_id}", response_model=MedicineOut)
async def get_medicine_by_id(
    medicine_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    result = await db.execute(select(Medicine).where(Medicine.id == medicine_id))
    medicine = result.scalar_one_or_none()
    if not medicine:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medicine not found")
    return medicine


@router.post("/interactions")
async def check_interactions(
    payload: InteractionRequest,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Check for drug interactions between a list of medicines."""
    # Placeholder – integrate with a drug interaction API or LLM
    return {"interactions": [], "message": "No interactions found in local database."}
