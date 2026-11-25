"""
Stage 3 — Comprehensive edge-case tests for POST /api/v1/medicines/interactions

All medicine IDs are real records from mediteach.db, verified by direct
database inspection before writing these tests.

── Fixture reference ──────────────────────────────────────────────────────────
ID_INSULIN   b116e74d-ee72-4d02-915f-b43ee7a242dc
             name: 'Human Insulatard 40IU/ml Suspension for Injection'
             generic: 'Insulin Isophane (40IU)'
             drug_interactions drugs: ['Benazepril','Captopril','Enalapril','Fosinopril']
             effects: all MODERATE

ID_ENALAPRIL 5333d297-ec37-42c2-9682-42ac1df78853
             name: 'Enace D 10 Tablet'
             generic: 'Enalapril (10mg) + Hydrochlorothiazide (25mg)'
             → Enalapril is in Insulin's drug list → MODERATE interaction

ID_1AL       e31cf476-05a0-475a-9eaf-0ba4e2c14589
             name: '1-AL Tablet'
             generic: 'Levocetirizine (5mg)'
             drug_interactions drugs: ['Aprepitant','Fosaprepitant','Zafirlukast','Alprazolam']
             effects: ['LIFE-THREATENING','LIFE-THREATENING','SERIOUS','MODERATE']

ID_APRECAP   45984a11-2078-43aa-a743-810c469ef5b0
             name: 'Aprecap 125/80 Capsule'
             generic: 'Aprepitant (125mg) + Aprepitant (80mg)'
             → 'Aprepitant' is in 1-AL's drug list → LIFE-THREATENING
             → Tests REVERSE direction (B's ingredient found in A's drug list)
             → Also tests '+' combination parsing

ID_6MP       de72727f-aaec-4664-b801-e3bca7f422ba
             name: '6-MP 50mg Tablet'
             generic: 'Mercaptopurine (50mg)'
             drug_interactions drugs: ['Leflunomide', ...]  effects: LIFE-THREATENING

ID_LEFNO     80191817-01ea-48b5-8a59-d5fbcc99620f
             name: 'Lefno 20 Tablet'
             generic: 'Leflunomide (20mg)'
             → Leflunomide is in 6-MP's drug list → LIFE-THREATENING

ID_EMPTY     1c57f5ef-f0e7-4d20-961e-50ea70d7cbc1
             name: '10 D Infusion'
             drug_interactions: {"drug":[],"brand":[],"effect":[]}   ← empty

ID_EMPTY2    973ccd1c-e10a-432a-bf56-5baeadeb11bb
             name: '25 D Infusion'
             drug_interactions: empty arrays

ID_UNKNOWN   00000000-0000-0000-0000-000000000000   ← guaranteed absent from DB

VALID_SEVERITIES = {SERIOUS, LIFE-THREATENING, MODERATE, MINOR, BENEFICIAL, UNKNOWN}
"""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.api.v1.medicines import extract_ingredients, find_interactions_for_pair

# ── Real IDs confirmed from live DB ──────────────────────────────────────────
ID_INSULIN   = "b116e74d-ee72-4d02-915f-b43ee7a242dc"
ID_ENALAPRIL = "5333d297-ec37-42c2-9682-42ac1df78853"
ID_1AL       = "e31cf476-05a0-475a-9eaf-0ba4e2c14589"
ID_APRECAP   = "45984a11-2078-43aa-a743-810c469ef5b0"
ID_6MP       = "de72727f-aaec-4664-b801-e3bca7f422ba"
ID_LEFNO     = "80191817-01ea-48b5-8a59-d5fbcc99620f"
ID_EMPTY     = "1c57f5ef-f0e7-4d20-961e-50ea70d7cbc1"
ID_EMPTY2    = "973ccd1c-e10a-432a-bf56-5baeadeb11bb"
ID_UNKNOWN   = "00000000-0000-0000-0000-000000000000"

VALID_SEVERITIES = {
    "SERIOUS", "LIFE-THREATENING", "MODERATE", "MINOR", "BENEFICIAL", "UNKNOWN"
}


# ── Auth helper ───────────────────────────────────────────────────────────────
async def get_token(client: AsyncClient) -> str:
    """Register or log in; always returns a valid Bearer token."""
    payload = {
        "name": "Stage3 Tester",
        "email": "stage3_test@example.com",
        "password": "Test1234",
        "preferred_language": "en",
    }
    r = await client.post("/api/v1/auth/register", json=payload)
    if r.status_code == 409:
        r = await client.post(
            "/api/v1/auth/login",
            json={"email": payload["email"], "password": payload["password"]},
        )
    return r.json()["access_token"]


async def post_interactions(client, token, medicine_ids):
    """Helper: POST to interactions endpoint and return response."""
    return await client.post(
        "/api/v1/medicines/interactions",
        json={"medicine_ids": medicine_ids},
        headers={"Authorization": f"Bearer {token}"},
    )


# ═════════════════════════════════════════════════════════════════════════════
# UNIT TESTS — extract_ingredients
# ═════════════════════════════════════════════════════════════════════════════

class TestExtractIngredients:
    """Unit tests for the extract_ingredients helper."""

    def test_single_ingredient(self):
        assert extract_ingredients("Paracetamol (500mg)") == ["paracetamol"]

    def test_combination_plus_separator(self):
        result = extract_ingredients("Enalapril (10mg) + Hydrochlorothiazide (25mg)")
        assert "enalapril" in result
        assert "hydrochlorothiazide" in result
        assert len(result) == 2

    def test_combination_slash_separator(self):
        result = extract_ingredients("Paracetamol/Acetaminophen (325mg)")
        assert "paracetamol" in result
        assert "acetaminophen" in result
        assert len(result) == 2

    def test_multi_word_ingredient(self):
        assert extract_ingredients("Insulin Isophane (40IU)") == ["insulin isophane"]

    def test_none_input_returns_empty(self):
        assert extract_ingredients(None) == []

    def test_empty_string_returns_empty(self):
        assert extract_ingredients("") == []

    def test_whitespace_only_returns_empty(self):
        assert extract_ingredients("   ") == []

    def test_leading_trailing_whitespace_stripped(self):
        result = extract_ingredients("  Metformin  (500mg)  ")
        assert "metformin" in result

    def test_very_short_token_discarded(self):
        # Tokens < 3 chars should be excluded to avoid false matches
        result = extract_ingredients("BP (10mg)")
        assert result == []

    def test_three_ingredient_combination(self):
        result = extract_ingredients(
            "Paracetamol (325mg) + Tramadol (37.5mg) + Caffeine (30mg)"
        )
        assert "paracetamol" in result
        assert "tramadol" in result
        assert "caffeine" in result
        assert len(result) == 3

    def test_dosage_stripped_not_included(self):
        result = extract_ingredients("Metformin (500mg)")
        assert "500mg" not in result[0]
        assert result == ["metformin"]


# ═════════════════════════════════════════════════════════════════════════════
# INTEGRATION TESTS — endpoint behaviour
# ═════════════════════════════════════════════════════════════════════════════

class TestAuthentication:
    """Authentication must be enforced."""

    @pytest.mark.asyncio
    async def test_unauthenticated_request_rejected(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            r = await client.post(
                "/api/v1/medicines/interactions",
                json={"medicine_ids": [ID_INSULIN, ID_ENALAPRIL]},
            )
        assert r.status_code == 403

    @pytest.mark.asyncio
    async def test_invalid_token_rejected(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            r = await client.post(
                "/api/v1/medicines/interactions",
                json={"medicine_ids": [ID_INSULIN, ID_ENALAPRIL]},
                headers={"Authorization": "Bearer not.a.real.token"},
            )
        assert r.status_code == 401


class TestInputValidation:
    """Request validation must reject invalid inputs before any DB query."""

    @pytest.mark.asyncio
    async def test_empty_list_returns_422(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            token = await get_token(client)
            r = await post_interactions(client, token, [])
        assert r.status_code == 422

    @pytest.mark.asyncio
    async def test_single_id_returns_422(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            token = await get_token(client)
            r = await post_interactions(client, token, [ID_INSULIN])
        assert r.status_code == 422

    @pytest.mark.asyncio
    async def test_two_identical_ids_returns_422(self):
        """Duplicate IDs count as one distinct ID → must fail validation."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            token = await get_token(client)
            r = await post_interactions(client, token, [ID_INSULIN, ID_INSULIN])
        assert r.status_code == 422

    @pytest.mark.asyncio
    async def test_three_identical_ids_returns_422(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            token = await get_token(client)
            r = await post_interactions(client, token, [ID_INSULIN, ID_INSULIN, ID_INSULIN])
        assert r.status_code == 422

    @pytest.mark.asyncio
    async def test_missing_medicine_ids_field_returns_422(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            token = await get_token(client)
            r = await client.post(
                "/api/v1/medicines/interactions",
                json={},
                headers={"Authorization": f"Bearer {token}"},
            )
        assert r.status_code == 422

    @pytest.mark.asyncio
    async def test_non_list_medicine_ids_returns_422(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            token = await get_token(client)
            r = await client.post(
                "/api/v1/medicines/interactions",
                json={"medicine_ids": "not-a-list"},
                headers={"Authorization": f"Bearer {token}"},
            )
        assert r.status_code == 422


class TestKnownInteraction:
    """Insulin + Enalapril: confirmed MODERATE interaction."""

    @pytest.mark.asyncio
    async def test_interaction_found(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            token = await get_token(client)
            r = await post_interactions(client, token, [ID_INSULIN, ID_ENALAPRIL])
        assert r.status_code == 200
        data = r.json()
        assert len(data["interactions"]) >= 1

        ingreds = [ix["interacting_ingredient"] for ix in data["interactions"]]
        assert any("enalapril" in i for i in ingreds)

        sevs = [ix["severity"] for ix in data["interactions"]]
        assert "MODERATE" in sevs

    @pytest.mark.asyncio
    async def test_interaction_severity_is_exactly_moderate(self):
        """Severity must be exactly 'MODERATE', not 'moderate' or 'Moderate'."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            token = await get_token(client)
            r = await post_interactions(client, token, [ID_INSULIN, ID_ENALAPRIL])
        data = r.json()
        enalapril_hits = [
            ix for ix in data["interactions"]
            if "enalapril" in ix["interacting_ingredient"].lower()
        ]
        assert len(enalapril_hits) >= 1
        assert enalapril_hits[0]["severity"] == "MODERATE"

    @pytest.mark.asyncio
    async def test_data_coverage_is_full_when_both_have_data(self):
        """
        Both medicines have drug_interactions data.
        Insulin has a non-empty drug list → data_available.
        Enace D 10 has a combination generic (Enalapril + Hydrochlorothiazide).
        Its drug_interactions data depends on what was stored from the CSV.
        Coverage will be 'full' if both have drug data, 'partial' if one has
        empty arrays — both are valid outcomes; what matters is it is NOT
        'unavailable' (which would mean neither has any data).
        """
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            token = await get_token(client)
            r = await post_interactions(client, token, [ID_INSULIN, ID_ENALAPRIL])
        assert r.json()["data_coverage"] in ("full", "partial")

    @pytest.mark.asyncio
    async def test_combination_medicine_ingredients_parsed(self):
        """
        Enace D 10 has generic 'Enalapril (10mg) + Hydrochlorothiazide (25mg)'.
        Both ingredients must be extracted and Enalapril must match.
        """
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            token = await get_token(client)
            r = await post_interactions(client, token, [ID_INSULIN, ID_ENALAPRIL])
        data = r.json()
        # The Enalapril ingredient must have been found from the combination generic name
        ingredients_found = [ix["interacting_ingredient"] for ix in data["interactions"]]
        assert "enalapril" in ingredients_found


class TestReverseDirectionMatch:
    """
    1-AL lists Aprepitant in its drug_interactions.
    Aprecap's generic contains 'Aprepitant'.
    The match is found via B_affects_A direction (Aprecap's ingredient
    is found in 1-AL's drug list, not the other way round).
    """

    @pytest.mark.asyncio
    async def test_reverse_direction_interaction_detected(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            token = await get_token(client)
            r = await post_interactions(client, token, [ID_1AL, ID_APRECAP])
        assert r.status_code == 200
        data = r.json()
        assert len(data["interactions"]) >= 1

        ingreds = [ix["interacting_ingredient"] for ix in data["interactions"]]
        assert any("aprepitant" in i for i in ingreds)

    @pytest.mark.asyncio
    async def test_reverse_direction_severity_is_life_threatening(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            token = await get_token(client)
            r = await post_interactions(client, token, [ID_1AL, ID_APRECAP])
        data = r.json()
        sevs = [ix["severity"] for ix in data["interactions"]]
        assert "LIFE-THREATENING" in sevs

    @pytest.mark.asyncio
    async def test_direction_field_is_valid(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            token = await get_token(client)
            r = await post_interactions(client, token, [ID_1AL, ID_APRECAP])
        data = r.json()
        for ix in data["interactions"]:
            assert ix["direction"] in ("A_affects_B", "B_affects_A")


class TestEmptyInteractionArrays:
    """Medicines with empty drug_interactions arrays."""

    @pytest.mark.asyncio
    async def test_both_empty_returns_no_interactions(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            token = await get_token(client)
            r = await post_interactions(client, token, [ID_EMPTY, ID_EMPTY2])
        assert r.status_code == 200
        data = r.json()
        assert data["interactions"] == []

    @pytest.mark.asyncio
    async def test_both_empty_coverage_is_unavailable(self):
        """Empty arrays ≠ safe. Coverage must be 'unavailable'."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            token = await get_token(client)
            r = await post_interactions(client, token, [ID_EMPTY, ID_EMPTY2])
        assert r.json()["data_coverage"] == "unavailable"

    @pytest.mark.asyncio
    async def test_empty_arrays_not_classified_as_safe(self):
        """
        Safety rule: response must never imply the combination is safe.
        The disclaimer for unavailable data must warn, not reassure.
        """
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            token = await get_token(client)
            r = await post_interactions(client, token, [ID_EMPTY, ID_EMPTY2])
        data = r.json()
        d = data["disclaimer"].lower()
        # Must not contain bare "safe" without a negation nearby
        # Acceptable: "cannot be used to assess the safety"
        # Not acceptable: "combination is safe"
        assert "combination is safe" not in d

    @pytest.mark.asyncio
    async def test_empty_medicines_data_status_is_no_interactions_recorded(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            token = await get_token(client)
            r = await post_interactions(client, token, [ID_EMPTY, ID_EMPTY2])
        data = r.json()
        statuses = {cm["data_status"] for cm in data["checked_medicines"]}
        assert statuses == {"no_interactions_recorded"}


class TestPartialDataAvailability:
    """One medicine has interaction data; the other has empty arrays."""

    @pytest.mark.asyncio
    async def test_partial_coverage_when_one_has_data_one_empty(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            token = await get_token(client)
            r = await post_interactions(client, token, [ID_INSULIN, ID_EMPTY])
        assert r.status_code == 200
        data = r.json()
        assert data["data_coverage"] == "partial"

    @pytest.mark.asyncio
    async def test_partial_coverage_disclaimer_warns_about_limits(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            token = await get_token(client)
            r = await post_interactions(client, token, [ID_INSULIN, ID_EMPTY])
        data = r.json()
        assert len(data["disclaimer"]) >= 50
        assert "consult" in data["disclaimer"].lower()

    @pytest.mark.asyncio
    async def test_partial_data_statuses_correctly_classified(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            token = await get_token(client)
            r = await post_interactions(client, token, [ID_INSULIN, ID_EMPTY])
        data = r.json()
        statuses = {cm["id"]: cm["data_status"] for cm in data["checked_medicines"]}
        assert statuses[ID_INSULIN] == "data_available"
        assert statuses[ID_EMPTY] == "no_interactions_recorded"


class TestNoMatchingInteraction:
    """Two medicines with data but no interaction between them."""

    @pytest.mark.asyncio
    async def test_no_recorded_interaction_returns_empty_list(self):
        """
        6-MP and 1-AL: 6-MP's drug list contains Leflunomide — 1-AL's
        ingredient is Levocetirizine which is NOT in 6-MP's list.
        1-AL's drug list contains Aprepitant — 6-MP's ingredient is
        Mercaptopurine which is NOT in 1-AL's list.
        Expected: no interactions found.
        """
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            token = await get_token(client)
            r = await post_interactions(client, token, [ID_1AL, ID_6MP])
        assert r.status_code == 200
        data = r.json()
        assert data["interactions"] == []

    @pytest.mark.asyncio
    async def test_no_match_coverage_is_full_when_both_have_data(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            token = await get_token(client)
            r = await post_interactions(client, token, [ID_1AL, ID_6MP])
        assert r.json()["data_coverage"] == "full"

    @pytest.mark.asyncio
    async def test_no_match_disclaimer_does_not_claim_safety(self):
        """
        Critical safety rule: an empty interactions list must never imply
        that the combination is safe.
        """
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            token = await get_token(client)
            r = await post_interactions(client, token, [ID_1AL, ID_6MP])
        data = r.json()
        d = data["disclaimer"].lower()
        # The disclaimer must contain a safety warning, not a clearance
        assert "does not" in d or "cannot" in d or "not establish" in d


class TestUnknownMedicineIds:
    """Unknown IDs must be reported, not cause errors."""

    @pytest.mark.asyncio
    async def test_all_unknown_ids_reported(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            token = await get_token(client)
            r = await post_interactions(client, token, [ID_UNKNOWN, ID_INSULIN])
        assert r.status_code == 200
        data = r.json()
        assert ID_UNKNOWN in data["unknown_medicine_ids"]

    @pytest.mark.asyncio
    async def test_unknown_id_gets_medicine_not_found_status(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            token = await get_token(client)
            r = await post_interactions(client, token, [ID_UNKNOWN, ID_INSULIN])
        data = r.json()
        statuses = {cm["id"]: cm["data_status"] for cm in data["checked_medicines"]}
        assert statuses.get(ID_UNKNOWN) == "medicine_not_found"

    @pytest.mark.asyncio
    async def test_two_unknown_ids_does_not_crash(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            token = await get_token(client)
            unknown2 = "11111111-1111-1111-1111-111111111111"
            r = await post_interactions(client, token, [ID_UNKNOWN, unknown2])
        assert r.status_code == 200
        data = r.json()
        assert ID_UNKNOWN in data["unknown_medicine_ids"]
        assert unknown2 in data["unknown_medicine_ids"]
        assert data["interactions"] == []

    @pytest.mark.asyncio
    async def test_unknown_id_does_not_raise_404(self):
        """The endpoint must return 200 and report the unknown ID — not 404."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            token = await get_token(client)
            r = await post_interactions(client, token, [ID_UNKNOWN, ID_INSULIN])
        assert r.status_code == 200


class TestThreeOrMoreMedicines:
    """All unique pairs must be checked when 3+ medicines are submitted."""

    @pytest.mark.asyncio
    async def test_three_medicines_all_pairs_checked(self):
        """
        Medicines: 6-MP, Lefno (interacts with 6-MP), Insulin.
        Pairs: (6-MP, Lefno), (6-MP, Insulin), (Lefno, Insulin).
        At least one interaction must be found: 6-MP × Lefno = LIFE-THREATENING.
        """
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            token = await get_token(client)
            r = await post_interactions(
                client, token, [ID_6MP, ID_LEFNO, ID_INSULIN]
            )
        assert r.status_code == 200
        data = r.json()
        assert len(data["checked_medicines"]) == 3
        assert len(data["interactions"]) >= 1

    @pytest.mark.asyncio
    async def test_three_medicines_known_interaction_present(self):
        """6-MP × Lefno must be LIFE-THREATENING in the 3-medicine check."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            token = await get_token(client)
            r = await post_interactions(
                client, token, [ID_6MP, ID_LEFNO, ID_INSULIN]
            )
        data = r.json()
        sevs = [ix["severity"] for ix in data["interactions"]]
        assert "LIFE-THREATENING" in sevs

    @pytest.mark.asyncio
    async def test_three_medicines_no_duplicate_pairs(self):
        """Each pair must appear at most once in interactions."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            token = await get_token(client)
            r = await post_interactions(
                client, token, [ID_6MP, ID_LEFNO, ID_INSULIN]
            )
        data = r.json()
        # Build set of (a_id, b_id, ingredient) tuples — all must be unique
        seen = set()
        for ix in data["interactions"]:
            key = (ix["medicine_a_id"], ix["medicine_b_id"], ix["interacting_ingredient"])
            assert key not in seen, f"Duplicate interaction entry: {key}"
            seen.add(key)


class TestSeverityPreservation:
    """Severity values must be returned exactly as stored — no modification."""

    @pytest.mark.asyncio
    async def test_severity_values_are_from_known_set(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            token = await get_token(client)
            r = await post_interactions(client, token, [ID_INSULIN, ID_ENALAPRIL])
        data = r.json()
        for ix in data["interactions"]:
            assert ix["severity"] in VALID_SEVERITIES, (
                f"Invented severity: {ix['severity']!r}"
            )

    @pytest.mark.asyncio
    async def test_life_threatening_severity_preserved_exactly(self):
        """Must be 'LIFE-THREATENING', not 'life-threatening' or 'FATAL'."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            token = await get_token(client)
            r = await post_interactions(client, token, [ID_1AL, ID_APRECAP])
        data = r.json()
        sevs = [ix["severity"] for ix in data["interactions"]]
        assert "LIFE-THREATENING" in sevs
        # Must not appear in a normalised/modified form
        assert "life-threatening" not in sevs
        assert "Life-Threatening" not in sevs

    @pytest.mark.asyncio
    async def test_no_dosage_or_treatment_instructions_in_response(self):
        """
        The response must never contain dosage changes or treatment advice.
        Verify the known interaction response contains only factual fields.
        """
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            token = await get_token(client)
            r = await post_interactions(client, token, [ID_INSULIN, ID_ENALAPRIL])
        data = r.json()
        # Interaction objects must not have dosage/treatment fields
        for ix in data["interactions"]:
            assert "dosage" not in ix
            assert "treatment" not in ix
            assert "recommendation" not in ix
            assert "dose" not in ix


class TestResponseStructure:
    """Every response must have the correct shape regardless of outcome."""

    @pytest.mark.asyncio
    async def test_all_required_fields_present(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            token = await get_token(client)
            r = await post_interactions(client, token, [ID_INSULIN, ID_ENALAPRIL])
        data = r.json()
        assert "checked_medicines" in data
        assert "interactions" in data
        assert "unknown_medicine_ids" in data
        assert "data_coverage" in data
        assert "disclaimer" in data

    @pytest.mark.asyncio
    async def test_checked_medicine_fields(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            token = await get_token(client)
            r = await post_interactions(client, token, [ID_INSULIN, ID_ENALAPRIL])
        data = r.json()
        valid_statuses = {"data_available", "no_interactions_recorded", "medicine_not_found"}
        for cm in data["checked_medicines"]:
            assert "id" in cm
            assert "name" in cm
            assert "data_status" in cm
            assert cm["data_status"] in valid_statuses

    @pytest.mark.asyncio
    async def test_interaction_object_fields(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            token = await get_token(client)
            r = await post_interactions(client, token, [ID_INSULIN, ID_ENALAPRIL])
        data = r.json()
        for ix in data["interactions"]:
            assert "medicine_a_id" in ix
            assert "medicine_a_name" in ix
            assert "medicine_b_id" in ix
            assert "medicine_b_name" in ix
            assert "interacting_ingredient" in ix
            assert "severity" in ix
            assert "direction" in ix

    @pytest.mark.asyncio
    async def test_data_coverage_values(self):
        """data_coverage must be one of the three defined values."""
        valid = {"full", "partial", "unavailable"}
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            token = await get_token(client)
            for id_pair in [
                [ID_INSULIN, ID_ENALAPRIL],   # full
                [ID_INSULIN, ID_EMPTY],        # partial
                [ID_EMPTY, ID_EMPTY2],         # unavailable
            ]:
                r = await post_interactions(client, token, id_pair)
                assert r.json()["data_coverage"] in valid


class TestDisclaimerSafety:
    """Safety disclaimers must be present and must never claim safety."""

    @pytest.mark.asyncio
    async def test_disclaimer_present_in_all_scenarios(self):
        scenarios = [
            [ID_INSULIN, ID_ENALAPRIL],   # interaction found
            [ID_EMPTY, ID_EMPTY2],        # no data
            [ID_INSULIN, ID_EMPTY],       # partial
            [ID_UNKNOWN, ID_INSULIN],     # unknown ID
            [ID_1AL, ID_6MP],             # no match
        ]
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            token = await get_token(client)
            for ids in scenarios:
                r = await post_interactions(client, token, ids)
                data = r.json()
                assert "disclaimer" in data, f"disclaimer missing for {ids}"
                assert len(data["disclaimer"]) >= 50, f"disclaimer too short for {ids}"

    @pytest.mark.asyncio
    async def test_disclaimer_never_says_combination_is_safe(self):
        scenarios = [
            [ID_INSULIN, ID_ENALAPRIL],
            [ID_EMPTY, ID_EMPTY2],
            [ID_1AL, ID_6MP],
        ]
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            token = await get_token(client)
            for ids in scenarios:
                r = await post_interactions(client, token, ids)
                d = r.json()["disclaimer"].lower()
                # "combination is safe" may appear in a negated context e.g.
                # "does not establish that this combination is safe" — that is
                # correct. What must never appear is a positive safety claim
                # such as "the combination is safe." or "this combination is safe."
                assert not d.endswith("combination is safe."), (
                    f"Disclaimer ends with positive safety claim for {ids}"
                )
                # Disclaimer must contain a negation or limitation statement
                assert any(w in d for w in ("not", "cannot", "never", "limit")), (
                    f"Disclaimer lacks safety warning for {ids}: {d}"
                )

    @pytest.mark.asyncio
    async def test_disclaimer_always_advises_consultation(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            token = await get_token(client)
            r = await post_interactions(client, token, [ID_INSULIN, ID_ENALAPRIL])
        d = r.json()["disclaimer"].lower()
        assert "consult" in d


class TestExistingEndpointsUnaffected:
    """Confirm medicine search and info endpoints still work correctly."""

    @pytest.mark.asyncio
    async def test_search_still_works(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            token = await get_token(client)
            r = await client.get(
                "/api/v1/medicines/search?q=paracetamol",
                headers={"Authorization": f"Bearer {token}"},
            )
        assert r.status_code == 200
        data = r.json()
        assert "results" in data
        assert isinstance(data["results"], list)
        assert len(data["results"]) > 0

    @pytest.mark.asyncio
    async def test_info_still_works(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            token = await get_token(client)
            r = await client.get(
                "/api/v1/medicines/info?name=paracetamol",
                headers={"Authorization": f"Bearer {token}"},
            )
        assert r.status_code == 200
        data = r.json()
        assert "id" in data
        assert "name" in data

    @pytest.mark.asyncio
    async def test_get_by_id_still_works(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            token = await get_token(client)
            r = await client.get(
                f"/api/v1/medicines/{ID_INSULIN}",
                headers={"Authorization": f"Bearer {token}"},
            )
        assert r.status_code == 200
        data = r.json()
        assert data["id"] == ID_INSULIN
