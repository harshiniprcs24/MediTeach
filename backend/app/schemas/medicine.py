from pydantic import BaseModel
from typing import Optional, List


class MedicineOut(BaseModel):
    id: str
    name: str
    generic_name: Optional[str]
    category: Optional[str]
    description: Optional[str]
    side_effects: Optional[str]
    dosage_info: Optional[str]
    contraindications: Optional[str]

    model_config = {"from_attributes": True}


class MedicineSearchResponse(BaseModel):
    results: List[MedicineOut]
    query: str


class InteractionRequest(BaseModel):
    medicine_ids: List[str]


class InteractionResult(BaseModel):
    medicine_a: str
    medicine_b: str
    severity: str        # none | mild | moderate | severe
    description: str
