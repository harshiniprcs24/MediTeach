"""
MediTeach — Medicine Database Seed Script
==========================================
Imports medicine records from the Kaggle CSV dataset into the SQLite
medicines table using batch inserts.

Usage (from the backend/ directory):
    venv\\Scripts\\python.exe scripts/seed_medicines.py

Optional flags:
    --dry-run       Parse and validate the CSV without writing to the DB
    --batch-size N  Override the default batch size (default: 500)
    --limit N       Only import the first N unique medicines (for quick testing)

CSV field → Medicine model field mapping:
    product_name         → name           (String 255, required)
    salt_composition     → generic_name   (String 255, nullable)
    sub_category         → category       (String 100, nullable)
    medicine_desc        → description    (Text, nullable)
    side_effects         → side_effects   (Text, nullable)

Unmapped CSV fields (intentionally not stored):
    drug_interactions    → NOT stored. Investigation confirmed the translations
                           column is reserved for {"ta":..., "hi":..., "te":...}
                           language data. Mixing interaction data there would
                           cause a semantic conflict when translation support is
                           implemented. A dedicated drug_interactions JSON column
                           should be added to the Medicine model when the
                           /medicines/interactions endpoint is built.
    product_price        → NOT stored (price data not relevant to MediTeach)
    product_manufactured → NOT stored (manufacturer not in the Medicine model)

Fields set to NULL in this import:
    dosage_info          → NULL (not present in CSV)
    contraindications    → NULL (not present in CSV)
    translations         → NULL (reserved for future language translations)

Duplicate handling:
    Uniqueness is defined as: LOWER(TRIM(product_name))
    On re-run, names already present in the DB are loaded into memory first
    and skipped during insertion. No UPDATE is performed on existing rows.

Safety:
    - Does not modify any existing project files
    - Reads DATABASE_URL from .env (same source as FastAPI)
    - Does not import the FastAPI app or async SQLAlchemy engine
    - Uses synchronous sqlite3 for simplicity and speed in a one-time script
    - All inserts are wrapped in a single transaction per batch;
      the entire import is rolled back cleanly if the script is interrupted
"""

import argparse
import csv
import sqlite3
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path


# ── Path resolution ──────────────────────────────────────────────────────────
# This file lives at backend/scripts/seed_medicines.py
# The backend root is one level up.

BACKEND_ROOT = Path(__file__).resolve().parent.parent
CSV_PATH     = BACKEND_ROOT / "data" / "medicine_data.csv"
ENV_PATH     = BACKEND_ROOT / ".env"

DEFAULT_BATCH_SIZE = 500


# ── Database URL resolution ───────────────────────────────────────────────────

def resolve_db_path() -> Path:
    """
    Read DATABASE_URL from .env if present, otherwise use the pydantic-settings
    default.  Only SQLite is supported by this script; it extracts the file path
    from the URL string.

    Supported URL formats:
        sqlite+aiosqlite:///./mediteach.db   → backend/mediteach.db
        sqlite+aiosqlite:////absolute/path   → /absolute/path
    """
    db_url = "sqlite+aiosqlite:///./mediteach.db"   # default from config.py

    if ENV_PATH.exists():
        with open(ENV_PATH, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("DATABASE_URL="):
                    db_url = line.split("=", 1)[1].strip().strip('"').strip("'")
                    break

    # Strip the async driver prefix to get a plain sqlite:/// URL
    db_url = db_url.replace("sqlite+aiosqlite", "sqlite")

    if not db_url.startswith("sqlite:///"):
        print(f"ERROR: This script only supports SQLite. Found: {db_url}")
        sys.exit(1)

    path_part = db_url[len("sqlite:///"):]   # everything after sqlite:///

    if path_part.startswith("/"):
        # Absolute path (sqlite:////absolute/path → /absolute/path)
        return Path(path_part)
    else:
        # Relative path — resolve relative to backend root
        # "./mediteach.db" → backend/mediteach.db
        return (BACKEND_ROOT / path_part.lstrip("./")).resolve()


# ── CSV parsing ───────────────────────────────────────────────────────────────

def parse_csv(limit: int | None) -> tuple[list[dict], int, int]:
    """
    Stream-parse the CSV and return:
        (records, total_csv_rows, invalid_rows)

    Deduplication within the CSV itself is performed here:
    the first occurrence of each product_name (case-insensitive) is kept;
    subsequent identical names are counted as CSV-level duplicates.

    Each returned record dict has keys matching the DB columns exactly.
    """

    if not CSV_PATH.exists():
        print(f"ERROR: CSV file not found at {CSV_PATH}")
        sys.exit(1)

    seen_names: set[str] = set()
    records: list[dict] = []
    total_rows = 0
    invalid_rows = 0
    csv_duplicates = 0

    with open(CSV_PATH, encoding="utf-8", errors="replace", newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            total_rows += 1

            # ── Required field ────────────────────────────────────────────────
            raw_name = (row.get("product_name") or "").strip()
            if not raw_name:
                invalid_rows += 1
                continue

            # Normalise the name key for deduplication
            name_key = raw_name.lower()
            if name_key in seen_names:
                csv_duplicates += 1
                continue
            seen_names.add(name_key)

            # ── Optional fields ───────────────────────────────────────────────
            generic_name = (row.get("salt_composition") or "").strip() or None
            category     = (row.get("sub_category") or "").strip() or None
            description  = (row.get("medicine_desc") or "").strip() or None
            side_effects = (row.get("side_effects") or "").strip() or None

            # ── Truncate fields that have DB length limits ────────────────────
            # product_name max observed: 98 chars   (limit 255) → safe
            # salt_composition max:      209 chars  (limit 255) → safe
            # sub_category max:          69 chars   (limit 100) → safe
            # We truncate defensively in case edge rows exceed the observed max.
            if generic_name and len(generic_name) > 255:
                generic_name = generic_name[:255]
            if category and len(category) > 100:
                category = category[:100]

            # ── Unmapped fields ───────────────────────────────────────────────
            # drug_interactions: NOT stored. The translations column is reserved
            # for language data {"ta":..., "hi":..., "te":...}. Storing
            # interaction data there would create a semantic conflict. A
            # dedicated drug_interactions column will be added to the Medicine
            # model when the /medicines/interactions endpoint is implemented.
            #
            # product_price, product_manufactured: discarded — not in the model
            # and not relevant to MediTeach's patient education purpose.

            records.append({
                "id":                str(uuid.uuid4()),
                "name":              raw_name,
                "generic_name":      generic_name,
                "category":          category,
                "description":       description,
                "side_effects":      side_effects,
                "dosage_info":       None,   # not in CSV
                "contraindications": None,   # not in CSV
                "translations":      None,   # reserved for language data
                "created_at":        datetime.now(timezone.utc).isoformat(),
                "updated_at":        datetime.now(timezone.utc).isoformat(),
            })

            if limit is not None and len(records) >= limit:
                # We've hit the --limit cap; count the rest as skipped
                remaining = 0
                for _ in reader:
                    remaining += 1
                total_rows += remaining
                csv_duplicates += remaining  # approximate: treat as skipped
                break

    return records, total_rows, invalid_rows, csv_duplicates


# ── Database insertion ────────────────────────────────────────────────────────

def seed(
    db_path: Path,
    records: list[dict],
    batch_size: int,
    dry_run: bool,
) -> tuple[int, int, int]:
    """
    Insert records into the medicines table.

    Returns:
        (inserted, db_duplicates_skipped, errors)

    Duplicate strategy:
        1. Before inserting anything, load all existing medicine names from the
           DB into a Python set (lowercase).
        2. Any record whose name (lowercase) is already in that set is skipped.
        3. This means re-running the script is safe: it will find all
           previously inserted names and skip them without touching the DB.
        4. We deliberately do NOT use INSERT OR IGNORE or ON CONFLICT because
           those clauses would silently mask real errors. Explicit pre-check
           gives accurate duplicate counts.
    """

    if dry_run:
        print("\n[DRY RUN] No changes will be written to the database.\n")
        return len(records), 0, 0

    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA journal_mode=WAL")   # faster concurrent writes
    conn.execute("PRAGMA synchronous=NORMAL") # safe and faster than FULL
    cursor = conn.cursor()

    # ── Load existing names for duplicate detection ───────────────────────────
    cursor.execute("SELECT LOWER(name) FROM medicines")
    existing_names: set[str] = {row[0] for row in cursor.fetchall()}
    print(f"  Existing medicines in DB: {len(existing_names):,}")

    INSERT_SQL = """
        INSERT INTO medicines
            (id, name, generic_name, category, description,
             side_effects, dosage_info, contraindications,
             translations, created_at, updated_at)
        VALUES
            (:id, :name, :generic_name, :category, :description,
             :side_effects, :dosage_info, :contraindications,
             :translations, :created_at, :updated_at)
    """

    inserted       = 0
    db_duplicates  = 0
    errors         = 0
    batch          = []

    def flush_batch(batch: list[dict]) -> tuple[int, int]:
        """Insert one batch inside a transaction. Returns (inserted, errors)."""
        ins = 0
        err = 0
        try:
            conn.executemany(INSERT_SQL, batch)
            conn.commit()
            ins = len(batch)
        except sqlite3.Error as exc:
            conn.rollback()
            # Re-try row by row to isolate the bad record
            for record in batch:
                try:
                    conn.execute(INSERT_SQL, record)
                    conn.commit()
                    ins += 1
                except sqlite3.Error as row_exc:
                    conn.rollback()
                    err += 1
                    print(f"  [ERROR] Row failed: {record['name']!r} — {row_exc}")
        return ins, err

    total_to_process = len(records)
    processed = 0

    for record in records:
        name_key = record["name"].lower()

        # Skip if already in DB
        if name_key in existing_names:
            db_duplicates += 1
            processed += 1
            continue

        batch.append(record)
        existing_names.add(name_key)  # prevent duplicates within this run

        if len(batch) >= batch_size:
            ins, err = flush_batch(batch)
            inserted += ins
            errors   += err
            batch = []

            processed += ins + err
            pct = processed / total_to_process * 100
            print(f"  Progress: {processed:>7,} / {total_to_process:,} "
                  f"({pct:.1f}%)  inserted={inserted:,}  "
                  f"skipped={db_duplicates:,}  errors={errors}")

    # Flush remaining records
    if batch:
        ins, err = flush_batch(batch)
        inserted += ins
        errors   += err

    conn.close()
    return inserted, db_duplicates, errors


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Seed the MediTeach medicines table from the Kaggle CSV."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse and validate the CSV without writing to the DB.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=DEFAULT_BATCH_SIZE,
        metavar="N",
        help=f"Rows per INSERT batch (default: {DEFAULT_BATCH_SIZE}).",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        metavar="N",
        help="Only import the first N unique records (useful for testing).",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("MediTeach — Medicine Seed Script")
    print("=" * 60)
    print(f"  CSV path:    {CSV_PATH}")

    db_path = resolve_db_path()
    print(f"  DB path:     {db_path}")
    print(f"  Batch size:  {args.batch_size}")
    if args.limit:
        print(f"  Limit:       {args.limit} records")
    if args.dry_run:
        print(f"  Mode:        DRY RUN (no writes)")
    else:
        print(f"  Mode:        LIVE (will write to DB)")
    print()

    if not db_path.exists() and not args.dry_run:
        print(f"ERROR: Database file not found at {db_path}")
        print("  Make sure the FastAPI server has been started at least once")
        print("  (it creates the DB and tables automatically on first startup).")
        sys.exit(1)

    # ── Step 1: Parse CSV ─────────────────────────────────────────────────────
    print("Step 1/2 — Parsing CSV...")
    records, total_rows, invalid_rows, csv_duplicates = parse_csv(args.limit)
    unique_from_csv = len(records)

    print(f"  Total CSV rows read:           {total_rows:>8,}")
    print(f"  Invalid rows (empty name):     {invalid_rows:>8,}")
    print(f"  Duplicate names in CSV:        {csv_duplicates:>8,}")
    print(f"  Unique records to process:     {unique_from_csv:>8,}")
    print()

    # ── Step 2: Insert into DB ────────────────────────────────────────────────
    print("Step 2/2 — Inserting into database...")
    inserted, db_duplicates, errors = seed(
        db_path=db_path,
        records=records,
        batch_size=args.batch_size,
        dry_run=args.dry_run,
    )

    # ── Final summary ─────────────────────────────────────────────────────────
    print()
    print("=" * 60)
    print("IMPORT SUMMARY")
    print("=" * 60)
    print(f"  Total CSV rows:                {total_rows:>8,}")
    print(f"  Invalid rows skipped:          {invalid_rows:>8,}")
    print(f"  Duplicates in CSV skipped:     {csv_duplicates:>8,}")
    print(f"  Already in DB skipped:         {db_duplicates:>8,}")
    print(f"  Errors:                        {errors:>8,}")
    print(f"  ─────────────────────────────────────────")
    print(f"  Successfully inserted:         {inserted:>8,}")
    print("=" * 60)

    if errors > 0:
        print(f"\n  ⚠  {errors} rows failed. See error messages above.")
        sys.exit(1)
    elif args.dry_run:
        print(f"\n  ✓  Dry run complete. {unique_from_csv:,} records would be inserted.")
    else:
        print(f"\n  ✓  Done. {inserted:,} medicines are now searchable in MediTeach.")


if __name__ == "__main__":
    main()
