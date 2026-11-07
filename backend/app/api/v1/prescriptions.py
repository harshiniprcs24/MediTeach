from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.core.security import get_current_user_id
from app.schemas.prescription import PrescriptionOut, PrescriptionListResponse
from app.services.medicine_service import MedicineService
from app.utils.file_handler import save_upload_file, validate_image_file
from app.services.ocr_service import OCRService
from app.models.prescription import Prescription

router = APIRouter()


@router.post("/upload", response_model=PrescriptionOut, status_code=status.HTTP_201_CREATED)
async def upload_prescription(
    file: UploadFile = File(...),
    language: str = Query("en"),
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Upload and OCR-process a prescription image."""
    validate_image_file(file)
    file_path = await save_upload_file(file, subfolder=user_id)

    ocr_service = OCRService()
    raw_text = await ocr_service.extract_text(file_path)

    medicine_service = MedicineService(db)
    parsed = await medicine_service.parse_prescription_text(raw_text, language)

    prescription = Prescription(
        user_id=user_id,
        title=parsed.get("title"),
        doctor=parsed.get("doctor"),
        file_path=file_path,
        raw_text=raw_text,
        medicines=parsed.get("medicines", []),
        instructions=parsed.get("instructions"),
        language=language,
    )
    db.add(prescription)
    await db.flush()
    await db.refresh(prescription)
    return prescription


@router.get("", response_model=PrescriptionListResponse)
async def list_prescriptions(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    sort: str = Query("created_at:desc"),
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """List paginated prescriptions for the current user."""
    from sqlalchemy import select, func, desc, asc
    from app.models.prescription import Prescription as PrescriptionModel

    sort_field, sort_dir = sort.split(":") if ":" in sort else (sort, "desc")
    order = desc if sort_dir == "desc" else asc

    total_q = await db.execute(
        select(func.count()).where(PrescriptionModel.user_id == user_id)
    )
    total = total_q.scalar()

    result = await db.execute(
        select(PrescriptionModel)
        .where(PrescriptionModel.user_id == user_id)
        .order_by(order(getattr(PrescriptionModel, sort_field, PrescriptionModel.created_at)))
        .offset((page - 1) * limit)
        .limit(limit)
    )
    items = result.scalars().all()
    return {"items": items, "total": total, "page": page, "limit": limit}


@router.get("/{prescription_id}", response_model=PrescriptionOut)
async def get_prescription(
    prescription_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    from sqlalchemy import select
    result = await db.execute(
        select(Prescription).where(
            Prescription.id == prescription_id,
            Prescription.user_id == user_id,
        )
    )
    prescription = result.scalar_one_or_none()
    if not prescription:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prescription not found")
    return prescription


@router.delete("/{prescription_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_prescription(
    prescription_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    from sqlalchemy import select
    result = await db.execute(
        select(Prescription).where(
            Prescription.id == prescription_id,
            Prescription.user_id == user_id,
        )
    )
    prescription = result.scalar_one_or_none()
    if not prescription:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prescription not found")
    await db.delete(prescription)
