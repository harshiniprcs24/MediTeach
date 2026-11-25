"""
MediTeach — Medicine Service
============================
Parses raw OCR prescription text into structured medicine data.

Two-stage pipeline
------------------
Stage 1 — LLM (OpenAI GPT-4o-mini)
    Used when OPENAI_API_KEY is configured.
    Handles unstructured, handwritten and complex formats.

Stage 2 — Deterministic regex fallback
    Used when no API key is set OR when the LLM returns an empty list.
    Handles structured printed prescriptions that follow the pattern:

        N) FORM. MEDICINE NAME  dosage-schedule  duration
        (Before/After Food)  (Tot:N Tab)

    Key insight from debugging the actual OCR output:
    - Name and dosage are separated by a SINGLE space (not multiple).
    - The boundary between name and dosage is identified by:
        a digit (possibly fractional like "1/2" or "1.") immediately
        followed by a dosage-schedule keyword (Morning/Moming/Night/
        Aft/Eve/Evening/Tab/Cap/ml/mg …).
    - Duration is matched anywhere in the dosage field ("10 Days", etc.).

    If the text does not match expected structure, an empty medicines list
    is returned — the raw OCR text is always preserved on the model for
    manual review.

Safety guarantees
-----------------
- Neither stage invents medicine names, dosages, or durations.
- Missing fields are returned as None, never as placeholder strings.
- OCR error strings are detected and bypassed without crashing.
"""

import re
import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.llm_service import LLMService
from app.core.config import settings

logger = logging.getLogger(__name__)


# ── Regex patterns ────────────────────────────────────────────────────────────

# Main line pattern.
# Matches: "N)  [FORM.]  MEDICINE NAME  <dosage anchored by digit+keyword>"
#
# The dosage anchor matches a digit/fraction immediately followed by a
# schedule keyword (Moming is a common Tesseract misread of Morning).
_DOSAGE_KW = (
    r"Moming|Morning|Night|Aft(?:ernoon)?|Eve(?:ning)?|"
    r"Tab(?:let)?|Cap(?:sule)?|ml|mg|mcg|IU|units?"
)

_LINE_RE = re.compile(
    r"^\s*(?P<num>\d+)[).]\s+"                       # "1) "
    r"(?P<form>(?:TAB|CAP|SYP|INJ|DROP|SUSP|OINT)[.,]?\s+)?"  # "TAB. " (optional)
    r"(?P<name>.+?)\s+"                              # medicine name (lazy)
    r"(?P<dosage>\d[\d./]*\s*(?:" + _DOSAGE_KW + r").+)"  # dosage starts with digit+keyword
    r"$",
    re.IGNORECASE,
)

# Duration: "10 Days", "5 Day", "2 Weeks", "1 Month"
_DURATION_RE = re.compile(
    r"\b(\d+(?:\.\d+)?)\s*(days?|weeks?|months?)\b",
    re.IGNORECASE,
)

# Strip "(Tot:20 Tab)" from dosage
_TOTAL_RE = re.compile(r"\s*\(Tot:\d+\s*\w+\)", re.IGNORECASE)

# Food/stomach instructions in parentheses: "(Before Food)", "(After Food)"
_INSTR_RE = re.compile(
    r"\(([^)]{3,60}(?:food|stomach|meal|meals|water|sleep|bed)[^)]*)\)",
    re.IGNORECASE,
)

# Advice section marker
_ADVICE_RE = re.compile(r"^advice\s*(?:given)?\s*[:\-]?\s*$", re.IGNORECASE)


# ── Line parser ───────────────────────────────────────────────────────────────

def _parse_line(line: str, next_line: str) -> Optional[dict]:
    """
    Parse one numbered medicine line.
    Returns a dict or None if the line does not match.
    """
    m = _LINE_RE.match(line.strip())
    if not m:
        return None

    form       = (m.group("form") or "").strip().rstrip(".,").strip()
    raw_name   = m.group("name").strip()
    dosage_raw = m.group("dosage").strip()

    # Full name includes the dosage form prefix
    name = f"{form} {raw_name}".strip() if form else raw_name

    # Discard very short or obviously wrong names (OCR noise)
    if len(name.replace(" ", "")) < 3:
        return None

    # Extract duration from dosage field
    dur_m    = _DURATION_RE.search(dosage_raw)
    duration = (
        f"{dur_m.group(1)} {dur_m.group(2).capitalize()}" if dur_m else None
    )

    # Remove duration and total from dosage field → frequency/schedule remains
    freq_raw = _DURATION_RE.sub("", dosage_raw)
    freq_raw = _TOTAL_RE.sub("", freq_raw).strip().strip(",").strip()

    # If the dosage field starts with a plain dose amount (e.g. "1", "1/2",
    # "500mg"), split it off as dosage; remainder is frequency.
    dosage    = None
    frequency = freq_raw or None
    dose_split = re.match(
        r"^(\d[\d./]*\s*(?:mg|ml|mcg|g|IU|units?)?)\s+(.+)$",
        freq_raw,
        re.IGNORECASE,
    )
    if dose_split:
        dosage    = dose_split.group(1).strip()
        frequency = dose_split.group(2).strip() or None

    # Instruction from this line or the next continuation line
    instr_m      = _INSTR_RE.search(line) or (_INSTR_RE.search(next_line) if next_line else None)
    instructions = instr_m.group(1).strip().title() if instr_m else None

    return {
        "name":         name,
        "dosage":       dosage,
        "frequency":    frequency,
        "duration":     duration,
        "instructions": instructions,
    }


# ── Public extraction functions ───────────────────────────────────────────────

def extract_medicines_from_text(raw_text: str) -> list:
    """
    Scan every line for numbered medicine entries and return a list of dicts.
    Returns [] if no structured lines are found or input is empty/None.
    Never invents data.
    """
    if not raw_text or not raw_text.strip():
        return []

    # Bail out on OCR error strings
    if raw_text.strip().startswith("[OCR unavailable"):
        return []

    lines    = raw_text.splitlines()
    medicines = []
    for i, line in enumerate(lines):
        next_line = lines[i + 1] if i + 1 < len(lines) else ""
        result = _parse_line(line, next_line)
        if result:
            medicines.append(result)

    return medicines


def extract_header_info(raw_text: str) -> dict:
    """
    Extract optional header fields from the OCR text.
    Returns {"title": None, "doctor": None, "instructions": None}
    with values filled where determinable.
    """
    title        = None
    doctor       = None
    instructions = None

    if not raw_text:
        return {"title": title, "doctor": doctor, "instructions": instructions}

    lines        = [l.strip() for l in raw_text.splitlines() if l.strip()]
    advice_lines = []
    in_advice    = False

    for line in lines:
        if _ADVICE_RE.match(line):
            in_advice = True
            continue
        if in_advice:
            # Collect bullet-point advice lines
            if re.match(r"^[*\-•]", line):
                advice_lines.append(line.lstrip("*-• ").strip())
            elif re.match(r"^\d+[).]", line):
                break  # reached next medicine entry

    if advice_lines:
        instructions = ". ".join(advice_lines)

    return {"title": title, "doctor": doctor, "instructions": instructions}


# ── Service class ─────────────────────────────────────────────────────────────

class MedicineService:
    def __init__(self, db: AsyncSession):
        self.db  = db
        self.llm = LLMService()

    async def parse_prescription_text(self, raw_text: str, language: str = "en") -> dict:
        """
        Parse raw OCR text into structured prescription data.

        Stage 1: LLM (when OPENAI_API_KEY is set).
        Stage 2: Deterministic regex fallback (always available).

        raw_text is never modified — callers store it on the model unchanged.
        """
        # Skip parsing when OCR itself reported a failure
        if not raw_text or raw_text.strip().startswith("[OCR unavailable"):
            logger.warning("Skipping extraction — OCR text unavailable.")
            return {
                "title": None, "doctor": None,
                "medicines": [], "instructions": None,
            }

        # ── Stage 1: LLM ──────────────────────────────────────────────────────
        if settings.OPENAI_API_KEY:
            logger.info("Parsing prescription with LLM.")
            result = await self.llm.parse_prescription(raw_text, language)
            if result.get("medicines"):
                return result
            logger.warning(
                "LLM returned empty medicines — falling back to regex parser."
            )

        # ── Stage 2: Regex fallback ───────────────────────────────────────────
        logger.info("Parsing prescription with deterministic regex fallback.")
        medicines = extract_medicines_from_text(raw_text)
        header    = extract_header_info(raw_text)

        if not medicines:
            logger.info(
                "Regex parser found no structured medicine lines. "
                "Raw OCR text will be shown to the user for manual review."
            )

        return {
            "title":        header["title"],
            "doctor":       header["doctor"],
            "medicines":    medicines,
            "instructions": header["instructions"],
        }
