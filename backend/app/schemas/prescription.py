from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime


class MedicineItem(BaseModel):
    name: str
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    duration: Optional[str] = None
    instructions: Optional[str] = None


class PrescriptionOut(BaseModel):
    id: str
    title: Optional[str]
    doctor: Optional[str]
    raw_text: Optional[str]
    medicines: Optional[List[MedicineItem]]
    instructions: Optional[str]
    language: str
    created_at: datetime

    model_config = {"from_attributes": True}


class PrescriptionListItem(BaseModel):
    id: str
    title: Optional[str]
    doctor: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class PrescriptionListResponse(BaseModel):
    items: List[PrescriptionListItem]
    total: int
    page: int
    limit: int
