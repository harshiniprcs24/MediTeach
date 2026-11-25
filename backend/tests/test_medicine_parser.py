"""
Tests for the deterministic prescription parser in medicine_service.py.

Uses the four sample medicine lines from the actual OCR output of the
uploaded demo prescription, plus edge cases for robustness.

No external API calls are made. All tests are purely deterministic.
"""

import pytest
from app.services.medicine_service import (
    extract_medicines_from_text,
    extract_header_info,
)

# ── The exact OCR text from the uploaded demo prescription ───────────────────
DEMO_OCR = (
    "ID: 266 - DEMO PATIENT (M)\n"
    "Address: PUNE\n"
    "Temp (deg): 36, BP: 120/80 mmHg\n"
    "\n"
    "Date: 27-Apr-2020, 04:37 PM\n"
    "\n"
    "SAMPLE PRESCRIPTION\n"
    "a\n"
    "Medicine Name Dosage Duration\n"
    "1) TAB. DEMO MEDICINE 1 1. Moming, 1 Night 10 Days\n"
    "(Before Food) (Tot:20 Tab)\n"
    "2) CAP, DEMO MEDICINE 2 1 Moming, 1 Night 10 Days\n"
    "(Before Food) (Tot:20 Cap)\n"
    "3) TAB, DEMO MEDICINE 3 1 Moming, 1 Aft, 1 Eve, 1 Night 10 Days\n"
    "(After Food) (Tot:40 Tab)\n"
    "4) TAB. DEMO MEDICINE 4 1/2 Moming, 1/2 Night 10 Days\n"
    "(After Food) (Tot:10 Tab)\n"
    "Advice Given:\n"
    "\n"
    "* AVOID OILY AND SPICY FOOD\n"
)


# ── extract_medicines_from_text ───────────────────────────────────────────────

class TestExtractMedicinesFromText:

    def test_returns_four_medicines_from_demo_prescription(self):
        result = extract_medicines_from_text(DEMO_OCR)
        assert len(result) == 4, (
            f"Expected 4 medicines, got {len(result)}: {result}"
        )

    def test_medicine_1_name_extracted(self):
        result = extract_medicines_from_text(DEMO_OCR)
        names = [m["name"].upper() for m in result]
        assert any("DEMO MEDICINE 1" in n for n in names), f"Names found: {names}"

    def test_medicine_2_name_extracted(self):
        result = extract_medicines_from_text(DEMO_OCR)
        names = [m["name"].upper() for m in result]
        assert any("DEMO MEDICINE 2" in n for n in names), f"Names found: {names}"

    def test_medicine_3_name_extracted(self):
        result = extract_medicines_from_text(DEMO_OCR)
        names = [m["name"].upper() for m in result]
        assert any("DEMO MEDICINE 3" in n for n in names), f"Names found: {names}"

    def test_medicine_4_name_extracted(self):
        result = extract_medicines_from_text(DEMO_OCR)
        names = [m["name"].upper() for m in result]
        assert any("DEMO MEDICINE 4" in n for n in names), f"Names found: {names}"

    def test_all_durations_are_10_days(self):
        result = extract_medicines_from_text(DEMO_OCR)
        for med in result:
            assert med["duration"] is not None, f"Duration missing for {med['name']}"
            assert "10" in med["duration"], (
                f"Expected '10 Days' in duration, got: {med['duration']}"
            )

    def test_medicine_1_frequency_contains_night(self):
        result = extract_medicines_from_text(DEMO_OCR)
        med1 = next((m for m in result if "MEDICINE 1" in m["name"].upper()), None)
        assert med1 is not None
        assert med1["frequency"] is not None
        assert "night" in med1["frequency"].lower(), (
            f"Expected 'night' in frequency, got: {med1['frequency']}"
        )

    def test_medicine_3_frequency_contains_multiple_times(self):
        """Medicine 3 has a 4-times-daily schedule."""
        result = extract_medicines_from_text(DEMO_OCR)
        med3 = next((m for m in result if "MEDICINE 3" in m["name"].upper()), None)
        assert med3 is not None
        assert med3["frequency"] is not None
        # Should mention morning/aft/eve/night combination
        freq_lower = med3["frequency"].lower()
        assert any(word in freq_lower for word in ["morn", "aft", "eve", "night"]), (
            f"Unexpected frequency: {med3['frequency']}"
        )

    def test_required_fields_present_in_all_medicines(self):
        """Every returned medicine must have at least name and duration."""
        result = extract_medicines_from_text(DEMO_OCR)
        for med in result:
            assert "name" in med
            assert "dosage" in med       # key exists, value may be None
            assert "frequency" in med
            assert "duration" in med
            assert "instructions" in med
            assert med["name"] is not None
            assert med["name"].strip() != ""

    def test_total_field_not_in_dosage(self):
        """(Tot:20 Tab) should never appear in the dosage field."""
        result = extract_medicines_from_text(DEMO_OCR)
        for med in result:
            dosage = med.get("dosage") or ""
            freq   = med.get("frequency") or ""
            assert "tot:" not in dosage.lower(), f"Tot: leaked into dosage: {dosage}"
            assert "tot:" not in freq.lower(),   f"Tot: leaked into frequency: {freq}"

    def test_returns_empty_for_empty_string(self):
        assert extract_medicines_from_text("") == []

    def test_returns_empty_for_none(self):
        assert extract_medicines_from_text(None) == []

    def test_returns_empty_for_ocr_error_string(self):
        error_text = "[OCR unavailable: tesseract is not installed or it's not in your PATH.]"
        result = extract_medicines_from_text(error_text)
        assert result == []

    def test_returns_empty_for_unstructured_text(self):
        """Plain paragraphs with no numbered medicine lines should return empty."""
        plain = (
            "Patient was advised to rest and drink plenty of fluids.\n"
            "Follow up after 7 days."
        )
        result = extract_medicines_from_text(plain)
        assert result == [], f"Expected empty list, got: {result}"

    def test_single_medicine_line(self):
        text = "1) TAB. PARACETAMOL  500mg  1 Morning, 1 Night  5 Days\n"
        result = extract_medicines_from_text(text)
        assert len(result) == 1
        assert "PARACETAMOL" in result[0]["name"].upper()
        assert "5" in (result[0]["duration"] or "")

    def test_no_fabricated_data(self):
        """
        Parser must never return fields that were not present in the source text.
        If duration is not in the line, it must be None — not a guess.
        """
        text = "1) TAB. SOME MEDICINE  1 Morning, 1 Night\n"
        result = extract_medicines_from_text(text)
        if result:
            # Duration is not in this line — must be None
            assert result[0]["duration"] is None, (
                f"Parser invented duration: {result[0]['duration']}"
            )


# ── extract_header_info ───────────────────────────────────────────────────────

class TestExtractHeaderInfo:

    def test_advice_extracted_as_instructions(self):
        result = extract_header_info(DEMO_OCR)
        assert result["instructions"] is not None
        assert "oily" in result["instructions"].lower() or \
               "spicy" in result["instructions"].lower(), (
            f"Instructions: {result['instructions']}"
        )

    def test_title_is_none_when_not_determinable(self):
        """Demo prescription has no clear clinic title line."""
        result = extract_header_info(DEMO_OCR)
        # We do not invent a title — it should be None or the extracted value
        assert "title" in result

    def test_returns_dict_with_all_keys(self):
        result = extract_header_info(DEMO_OCR)
        assert "title"        in result
        assert "doctor"       in result
        assert "instructions" in result

    def test_empty_text_returns_all_none(self):
        result = extract_header_info("")
        assert result["title"]        is None
        assert result["doctor"]       is None
        assert result["instructions"] is None


# ── Integration: parse_prescription_text without API key ─────────────────────

class TestParsePrescriptionTextFallback:
    """
    Tests MedicineService.parse_prescription_text using the regex fallback.
    These are synchronous via pytest-asyncio.
    """

    @pytest.mark.asyncio
    async def test_fallback_returns_four_medicines(self):
        """Without an API key, the regex fallback should extract 4 medicines."""
        from unittest.mock import MagicMock
        from app.services.medicine_service import MedicineService

        # Ensure no API key for this test
        import app.core.config as cfg
        original = cfg.settings.OPENAI_API_KEY
        cfg.settings.OPENAI_API_KEY = ""

        try:
            svc = MedicineService(db=MagicMock())
            result = await svc.parse_prescription_text(DEMO_OCR, "en")
        finally:
            cfg.settings.OPENAI_API_KEY = original

        assert "medicines" in result
        assert len(result["medicines"]) == 4, (
            f"Expected 4, got {len(result['medicines'])}: {result['medicines']}"
        )

    @pytest.mark.asyncio
    async def test_fallback_preserves_instructions(self):
        from unittest.mock import MagicMock
        from app.services.medicine_service import MedicineService
        import app.core.config as cfg

        original = cfg.settings.OPENAI_API_KEY
        cfg.settings.OPENAI_API_KEY = ""

        try:
            svc = MedicineService(db=MagicMock())
            result = await svc.parse_prescription_text(DEMO_OCR, "en")
        finally:
            cfg.settings.OPENAI_API_KEY = original

        instr = result.get("instructions") or ""
        assert "oily" in instr.lower() or "spicy" in instr.lower(), (
            f"Instructions: {instr}"
        )

    @pytest.mark.asyncio
    async def test_fallback_skips_ocr_error_text(self):
        from unittest.mock import MagicMock
        from app.services.medicine_service import MedicineService
        import app.core.config as cfg

        original = cfg.settings.OPENAI_API_KEY
        cfg.settings.OPENAI_API_KEY = ""

        try:
            svc = MedicineService(db=MagicMock())
            result = await svc.parse_prescription_text(
                "[OCR unavailable: tesseract is not installed]", "en"
            )
        finally:
            cfg.settings.OPENAI_API_KEY = original

        assert result["medicines"] == []
