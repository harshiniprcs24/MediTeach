from pydantic import BaseModel, field_validator
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

    @field_validator("medicine_ids")
    @classmethod
    def require_at_least_two_distinct(cls, v: List[str]) -> List[str]:
        unique = list(dict.fromkeys(id_.strip() for id_ in v if id_.strip()))
        if len(unique) < 2:
            raise ValueError(
                "At least two distinct medicine IDs are required to check interactions."
            )
        return unique


# ── Interaction response schemas ──────────────────────────────────────────────

class CheckedMedicine(BaseModel):
    """Summary of one medicine that was included in the interaction check."""
    id: str
    name: str
    data_status: str
    # "data_available"      — drug_interactions has at least one drug entry
    # "no_interactions_recorded" — drug_interactions present but drug[] is empty
    # "medicine_not_found"  — ID was not found in the database


class InteractionFound(BaseModel):
    """One confirmed interaction between two medicines."""
    medicine_a_id:           str
    medicine_a_name:         str
    medicine_b_id:           str
    medicine_b_name:         str
    interacting_ingredient:  str   # the generic drug name that matched
    severity:                str   # exactly as stored: SERIOUS / LIFE-THREATENING / etc.
    direction:               str   # "A_affects_B" or "B_affects_A"


class InteractionResponse(BaseModel):
    """
    Full response for POST /medicines/interactions.

    data_coverage values:
      "full"        — all submitted medicines had drug_interactions data
      "partial"     — some had data, some had empty arrays
      "unavailable" — none of the medicines had usable interaction data

    IMPORTANT: an empty interactions list does NOT mean the combination is safe.
    Check data_coverage and read the disclaimer before drawing any conclusion.
    """
    checked_medicines:      List[CheckedMedicine]
    interactions:           List[InteractionFound]
    unknown_medicine_ids:   List[str]
    data_coverage:          str
    disclaimer:             str


# Kept for backward compatibility — not used by the new endpoint
class InteractionResult(BaseModel):
    medicine_a: str
    medicine_b: str
    severity: str
    description: str
