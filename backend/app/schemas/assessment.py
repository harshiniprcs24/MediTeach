from pydantic import BaseModel, field_validator
from typing import List, Optional
from datetime import datetime


class AssessmentRequest(BaseModel):
    symptoms: List[str]
    severity: int           # 1, 2, or 3
    duration: int           # days

    @field_validator("severity")
    @classmethod
    def validate_severity(cls, v):
        if v not in (1, 2, 3):
            raise ValueError("Severity must be 1 (mild), 2 (moderate), or 3 (severe)")
        return v

    @field_validator("symptoms")
    @classmethod
    def validate_symptoms(cls, v):
        if not v:
            raise ValueError("At least one symptom is required")
        return v


class AssessmentOut(BaseModel):
    id: str
    symptoms: List[str]
    severity: int
    duration_days: int
    urgency: Optional[str]
    summary: Optional[str]
    possible_conditions: Optional[List[str]]
    recommendations: Optional[List[str]]
    created_at: datetime

    model_config = {"from_attributes": True}


class AssessmentListItem(BaseModel):
    id: str
    urgency: Optional[str]
    symptoms: List[str]
    created_at: datetime

    model_config = {"from_attributes": True}
