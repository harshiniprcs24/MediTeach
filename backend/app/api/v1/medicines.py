from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, case
import re
import itertools

from app.database.connection import get_db
from app.core.security import get_current_user_id
from app.models.medicine import Medicine
from app.schemas.medicine import (
    MedicineOut,
    MedicineSearchResponse,
    InteractionRequest,
    InteractionResponse,
    CheckedMedicine,
    InteractionFound,
)

router = APIRouter()

# ── Safety disclaimer — never omit or shorten ─────────────────────────────────
_DISCLAIMER = (
    "This check is based on a limited dataset and is provided for educational "
    "purposes only. It does not cover all known drug interactions. "
    "An empty interaction list does NOT establish that this combination is safe. "
    "Always consult a qualified doctor or pharmacist before taking any "
    "combination of medicines."
)

_UNAVAILABLE_DISCLAIMER = (
    "Interaction data is not available for one or more of the submitted "
    "medicines in our dataset. This check cannot be used to assess the safety "
    "of this combination. Always consult a qualified healthcare professional."
)


# ── Ingredient extraction ─────────────────────────────────────────────────────

def extract_ingredients(generic_name: str | None) -> list[str]:
    """
    Parse a generic_name string into a list of normalised ingredient names.

    Examples:
      "Paracetamol (500mg)"                        → ["paracetamol"]
      "Enalapril (10mg) + Hydrochlorothiazide (25mg)" → ["enalapril", "hydrochlorothiazide"]
      "Paracetamol/Acetaminophen (325mg)"          → ["paracetamol", "acetaminophen"]
      "Insulin Isophane (40IU)"                    → ["insulin isophane"]

    Strategy:
      1. Split on '+' and '/' to separate combination ingredients.
      2. Strip dosage information inside parentheses.
      3. Normalise to lowercase and strip whitespace.
      4. Discard tokens shorter than 3 characters (avoid false matches).

    We use EXACT equality (after normalisation) when comparing against the
    drug array entries — never substring matching — to prevent false positives.
    For example, "Insulin" must not match "Insulin Isophane" unless the full
    normalised string equals the drug array entry.
    """
    if not generic_name:
        return []

    # Split on '+' and '/'
    parts = re.split(r'[+/]', generic_name)
    ingredients = []
    for part in parts:
        # Remove dosage: anything inside (...)
        clean = re.sub(r'\(.*?\)', '', part)
        # Remove trailing comma, periods
        clean = clean.strip().strip(',').strip('.')
        normalised = clean.lower().strip()
        if len(normalised) >= 3:
            ingredients.append(normalised)

    return ingredients


def normalise_drug_name(drug: str) -> str:
    """Normalise a drug name from the interactions array for comparison."""
    return drug.strip().lower()


# ── Core interaction logic ────────────────────────────────────────────────────

def find_interactions_for_pair(
    med_a: Medicine,
    med_b: Medicine,
) -> list[InteractionFound]:
    """
    Check whether medicine A and medicine B interact, in both directions.

    Direction A→B: does med_A's drug_interactions list any ingredient of med_B?
    Direction B→A: does med_B's drug_interactions list any ingredient of med_A?

    Matching uses exact equality after normalisation (lowercase + strip).
    This avoids the false-positive risk of substring matching.

    Returns a list of InteractionFound objects (may be empty).
    Deduplicates: if both directions report the same ingredient pair, only
    the first direction found is included.
    """
    results: list[InteractionFound] = []
    seen_pairs: set[tuple[str, str, str]] = set()  # (a_id, b_id, ingredient)

    def _check(source: Medicine, target: Medicine, direction: str) -> None:
        di = source.drug_interactions
        if not di or not isinstance(di, dict):
            return
        drug_list   = di.get("drug", [])
        effect_list = di.get("effect", [])
        if not drug_list:
            return

        # Normalise the entire drug array once
        normalised_drugs = [normalise_drug_name(d) for d in drug_list]

        target_ingredients = extract_ingredients(target.generic_name)
        for ingredient in target_ingredients:
            try:
                idx = normalised_drugs.index(ingredient)
            except ValueError:
                continue  # not found — exact match only

            severity = (
                effect_list[idx].strip()
                if idx < len(effect_list)
                else "UNKNOWN"
            )
            dedup_key = (source.id, target.id, ingredient)
            if dedup_key in seen_pairs:
                continue
            seen_pairs.add(dedup_key)

            results.append(InteractionFound(
                medicine_a_id=source.id,
                medicine_a_name=source.name,
                medicine_b_id=target.id,
                medicine_b_name=target.name,
                interacting_ingredient=ingredient,
                severity=severity,
                direction=direction,
            ))

    _check(med_a, med_b, "A_affects_B")
    _check(med_b, med_a, "B_affects_A")
    return results


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
    """
    Look up a single medicine by name.

    Match priority (highest to lowest):
      1. Exact match on name          (case-insensitive)
      2. Exact match on generic_name  (case-insensitive)
      3. Partial match on name        (name contains the query)
      4. Partial match on generic_name

    Returns the single best match. If multiple records share the same
    priority level, the one whose name sorts first alphabetically is
    returned — no records are silently merged or combined.
    """
    name_exact   = name.strip()
    name_partial = f"%{name_exact}%"

    # Priority column: lower value = better match
    #   1 → exact name match
    #   2 → exact generic_name match
    #   3 → partial name match
    #   4 → partial generic_name match
    priority = case(
        (Medicine.name.ilike(name_exact),          1),
        (Medicine.generic_name.ilike(name_exact),  2),
        (Medicine.name.ilike(name_partial),        3),
        (Medicine.generic_name.ilike(name_partial), 4),
        else_=99,
    )

    result = await db.execute(
        select(Medicine)
        .where(
            or_(
                Medicine.name.ilike(name_exact),
                Medicine.generic_name.ilike(name_exact),
                Medicine.name.ilike(name_partial),
                Medicine.generic_name.ilike(name_partial),
            )
        )
        .order_by(priority, Medicine.name)
        .limit(1)
    )
    medicine = result.scalar_one_or_none()
    if not medicine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No medicine found matching '{name}'.",
        )
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


@router.post("/interactions", response_model=InteractionResponse)
async def check_interactions(
    payload: InteractionRequest,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    Check drug interactions between two or more medicines.

    Requires at least two distinct medicine IDs. Checks both directions
    for every unique pair. Reports interactions found, data availability
    per medicine, and a mandatory safety disclaimer.

    SAFETY: An empty interactions list does NOT mean the combination is safe.
    The dataset covers only a subset of known drug interactions.
    """
    # ── Fetch requested medicines ─────────────────────────────────────────────
    result = await db.execute(
        select(Medicine).where(Medicine.id.in_(payload.medicine_ids))
    )
    found_medicines: list[Medicine] = list(result.scalars().all())
    found_ids = {m.id for m in found_medicines}

    unknown_ids = [id_ for id_ in payload.medicine_ids if id_ not in found_ids]

    # ── Classify each medicine by data availability ───────────────────────────
    checked: list[CheckedMedicine] = []
    for med in found_medicines:
        di = med.drug_interactions
        if di is None:
            ds = "no_interactions_recorded"
        elif isinstance(di, dict) and di.get("drug"):
            ds = "data_available"
        else:
            ds = "no_interactions_recorded"
        checked.append(CheckedMedicine(id=med.id, name=med.name, data_status=ds))

    for uid in unknown_ids:
        checked.append(CheckedMedicine(
            id=uid,
            name="Unknown",
            data_status="medicine_not_found",
        ))

    # ── Check every unique pair ───────────────────────────────────────────────
    interactions: list[InteractionFound] = []
    for med_a, med_b in itertools.combinations(found_medicines, 2):
        interactions.extend(find_interactions_for_pair(med_a, med_b))

    # ── Compute data_coverage ─────────────────────────────────────────────────
    statuses = {c.data_status for c in checked if c.data_status != "medicine_not_found"}
    has_available  = "data_available" in statuses
    has_no_record  = "no_interactions_recorded" in statuses

    if has_available and not has_no_record:
        data_coverage = "full"
    elif has_available and has_no_record:
        data_coverage = "partial"
    else:
        data_coverage = "unavailable"

    disclaimer = (
        _UNAVAILABLE_DISCLAIMER if data_coverage == "unavailable"
        else _DISCLAIMER
    )

    return InteractionResponse(
        checked_medicines=checked,
        interactions=interactions,
        unknown_medicine_ids=unknown_ids,
        data_coverage=data_coverage,
        disclaimer=disclaimer,
    )
