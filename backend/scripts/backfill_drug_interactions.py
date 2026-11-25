"""
MediTeach — Drug Interactions Backfill Script
==============================================
Stage 1 of drug interaction feature implementation.

What this script does:
  1. Creates a timestamped backup of mediteach.db before any changes.
  2. Adds the drug_interactions JSON column to the medicines table
     using ALTER TABLE (safe — does not drop or recreate the table).
  3. Reads drug_interactions data from medicine_data.csv.
  4. Matches each CSV row to a DB medicine by normalized product name.
  5. UPDATEs each matched row with its parsed drug_interactions value.

Design decisions:
  - NULL   means the CSV had no entry for this product (unmatched).
  - {}     is stored as-is when the JSON parses to an empty-ish dict.
  - {"drug": [], "brand": [], "effect": []} is stored as-is —
    explicitly means "source recorded no interactions" (distinct from NULL).
  - Brand names are stripped of leading/trailing whitespace.
  - Safe to re-run: if the column already exists, ALTER TABLE is skipped.
    UPDATE is idempotent — running again overwrites with the same values.

Usage (from the backend/ directory):
    venv\\Scripts\\python.exe scripts/backfill_drug_interactions.py

Optional flags:
    --dry-run    Show what would happen without writing to the DB or backing up.
    --limit N    Only process the first N unique CSV names (for quick testing).
"""

import argparse
import csv
import json
import shutil
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────
BACKEND_ROOT = Path(__file__).resolve().parent.parent
CSV_PATH     = BACKEND_ROOT / "data" / "medicine_data.csv"
ENV_PATH     = BACKEND_ROOT / ".env"


# ── Database URL resolution (same logic as seed script) ───────────────────────
def resolve_db_path() -> Path:
    db_url = "sqlite+aiosqlite:///./mediteach.db"
    if ENV_PATH.exists():
        with open(ENV_PATH, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("DATABASE_URL="):
                    db_url = line.split("=", 1)[1].strip().strip('"').strip("'")
                    break
    db_url = db_url.replace("sqlite+aiosqlite", "sqlite")
    if not db_url.startswith("sqlite:///"):
        print(f"ERROR: Only SQLite is supported. Found: {db_url}")
        sys.exit(1)
    path_part = db_url[len("sqlite:///"):]
    if path_part.startswith("/"):
        return Path(path_part)
    return (BACKEND_ROOT / path_part.lstrip("./")).resolve()


# ── Backup ────────────────────────────────────────────────────────────────────
def backup_database(db_path: Path) -> Path:
    """Copy mediteach.db to mediteach_backup_<timestamp>.db in the same folder."""
    ts      = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup  = db_path.parent / f"mediteach_backup_{ts}.db"
    shutil.copy2(str(db_path), str(backup))
    return backup


# ── ALTER TABLE ───────────────────────────────────────────────────────────────
def add_column_if_missing(conn: sqlite3.Connection) -> bool:
    """
    Add drug_interactions JSON column to medicines table if not present.
    Returns True if the column was added, False if it already existed.
    """
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info('medicines')")
    existing_cols = {row[1] for row in cursor.fetchall()}
    if "drug_interactions" in existing_cols:
        return False
    cursor.execute("ALTER TABLE medicines ADD COLUMN drug_interactions JSON")
    conn.commit()
    return True


# ── CSV loading ───────────────────────────────────────────────────────────────
def load_csv_interactions(limit: int | None) -> dict[str, dict | None]:
    """
    Stream the CSV and return a dict:
        normalised_product_name → parsed interaction dict (or None on failure)

    Only the first occurrence of each product name is kept (CSV deduplication).
    Preserves empty arrays as {"drug": [], "brand": [], "effect": []} —
    explicitly distinct from None / NULL.
    Brand name strings are stripped of leading/trailing whitespace.
    """
    if not CSV_PATH.exists():
        print(f"ERROR: CSV not found at {CSV_PATH}")
        sys.exit(1)

    data: dict[str, dict | None] = {}
    parse_errors = 0

    with open(CSV_PATH, encoding="utf-8", errors="replace", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = (row.get("product_name") or "").strip()
            if not name:
                continue
            key = name.lower()
            if key in data:
                continue   # keep first occurrence only

            raw = (row.get("drug_interactions") or "").strip()
            if not raw:
                data[key] = None
                continue

            try:
                parsed = json.loads(raw)
            except (json.JSONDecodeError, ValueError):
                parse_errors += 1
                data[key] = None
                continue

            # Strip whitespace from brand name strings
            if isinstance(parsed.get("brand"), list):
                parsed["brand"] = [b.strip() for b in parsed["brand"]]

            data[key] = parsed

            if limit is not None and len(data) >= limit:
                break

    if parse_errors:
        print(f"  ⚠  {parse_errors} CSV rows had unparseable drug_interactions JSON")

    return data


# ── Backfill ──────────────────────────────────────────────────────────────────
def backfill(
    conn: sqlite3.Connection,
    csv_data: dict[str, dict | None],
    dry_run: bool,
) -> dict:
    """
    UPDATE each medicine row with its drug_interactions value from CSV.
    Returns a stats dict.
    """
    cursor = conn.cursor()

    # Load all medicines: normalised name → id
    cursor.execute("SELECT id, LOWER(name) FROM medicines")
    db_medicines: dict[str, str] = {row[1]: row[0] for row in cursor.fetchall()}

    stats = {
        "total_db_medicines":     len(db_medicines),
        "csv_names_loaded":       len(csv_data),
        "matched_and_updated":    0,
        "set_to_empty_array":     0,   # matched, drug[] == []
        "set_to_has_data":        0,   # matched, drug[] has entries
        "unmatched_db_rows":      0,   # in DB but not in CSV by name
        "dry_run":                dry_run,
    }

    update_pairs: list[tuple[str, str]] = []   # (json_str_or_null, medicine_id)

    for db_name, medicine_id in db_medicines.items():
        if db_name in csv_data:
            interaction = csv_data[db_name]
            if interaction is None:
                # CSV had no JSON for this product — keep NULL
                # (do not overwrite — NULL is the correct value)
                stats["unmatched_db_rows"] += 1
                continue

            json_str = json.dumps(interaction)
            update_pairs.append((json_str, medicine_id))
            stats["matched_and_updated"] += 1

            drugs = interaction.get("drug", [])
            if isinstance(drugs, list) and drugs:
                stats["set_to_has_data"] += 1
            else:
                stats["set_to_empty_array"] += 1
        else:
            stats["unmatched_db_rows"] += 1

    if dry_run:
        return stats

    # Execute in batches of 500
    BATCH = 500
    for i in range(0, len(update_pairs), BATCH):
        batch = update_pairs[i : i + BATCH]
        cursor.executemany(
            "UPDATE medicines SET drug_interactions = ? WHERE id = ?",
            batch,
        )
        conn.commit()

    return stats


# ── Verification ──────────────────────────────────────────────────────────────
def verify(conn: sqlite3.Connection) -> dict:
    """Read back counts from the DB to confirm the backfill result."""
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM medicines")
    total = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM medicines WHERE drug_interactions IS NULL")
    null_count = c.fetchone()[0]

    c.execute("""
        SELECT COUNT(*) FROM medicines
        WHERE drug_interactions IS NOT NULL
          AND json_extract(drug_interactions, '$.drug') = '[]'
    """)
    # SQLite json_extract returns a string representation for arrays
    # Use a more reliable approach: check if the JSON drug array is empty
    c.execute("""
        SELECT COUNT(*) FROM medicines
        WHERE drug_interactions IS NOT NULL
    """)
    non_null = c.fetchone()[0]

    # Count those with actual drug data (drug array non-empty)
    c.execute("""
        SELECT COUNT(*) FROM medicines
        WHERE drug_interactions IS NOT NULL
          AND drug_interactions != '{"drug": [], "brand": [], "effect": []}'
          AND drug_interactions NOT LIKE '%"drug": []%'
    """)
    # More reliable: load and check in Python for a sample
    # Use json_array_length if available (SQLite 3.38+), else Python fallback
    try:
        c.execute("""
            SELECT COUNT(*) FROM medicines
            WHERE json_array_length(json_extract(drug_interactions, '$.drug')) > 0
        """)
        has_data = c.fetchone()[0]
        c.execute("""
            SELECT COUNT(*) FROM medicines
            WHERE drug_interactions IS NOT NULL
              AND json_array_length(json_extract(drug_interactions, '$.drug')) = 0
        """)
        empty_arrays = c.fetchone()[0]
    except sqlite3.OperationalError:
        # json_array_length not available — fall back to Python counting
        c.execute("SELECT drug_interactions FROM medicines WHERE drug_interactions IS NOT NULL")
        rows = c.fetchall()
        has_data     = sum(1 for (r,) in rows if json.loads(r).get("drug"))
        empty_arrays = sum(1 for (r,) in rows if not json.loads(r).get("drug"))

    # Verify other tables are untouched
    other_tables = {}
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name != 'medicines'")
    for (t,) in c.fetchall():
        c.execute(f"SELECT COUNT(*) FROM '{t}'")
        other_tables[t] = c.fetchone()[0]

    return {
        "total_medicines":    total,
        "null_count":         null_count,
        "non_null_count":     non_null,
        "empty_array_count":  empty_arrays,
        "has_data_count":     has_data,
        "other_tables":       other_tables,
    }


# ── Entry point ───────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Backfill drug_interactions column from Kaggle CSV."
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="Simulate without writing to DB or creating backup.")
    parser.add_argument("--limit", type=int, default=None, metavar="N",
                        help="Only process first N unique CSV names (testing).")
    args = parser.parse_args()

    print("=" * 65)
    print("MediTeach — Drug Interactions Backfill")
    print("=" * 65)

    db_path = resolve_db_path()
    print(f"  DB  : {db_path}")
    print(f"  CSV : {CSV_PATH}")
    print(f"  Mode: {'DRY RUN — no writes' if args.dry_run else 'LIVE'}")
    if args.limit:
        print(f"  Limit: {args.limit} CSV names")
    print()

    if not db_path.exists():
        print("ERROR: Database not found. Start FastAPI once to create it.")
        sys.exit(1)

    # ── Step 1: Backup ────────────────────────────────────────────────────────
    if not args.dry_run:
        print("Step 1/4 — Backing up database...")
        backup_path = backup_database(db_path)
        print(f"  Backup created: {backup_path.name}")
    else:
        print("Step 1/4 — Backup skipped (dry run)")
    print()

    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")

    # ── Step 2: ALTER TABLE ───────────────────────────────────────────────────
    print("Step 2/4 — Adding drug_interactions column...")
    if args.dry_run:
        print("  [DRY RUN] Would run: ALTER TABLE medicines ADD COLUMN drug_interactions JSON")
    else:
        added = add_column_if_missing(conn)
        if added:
            print("  Column added successfully.")
        else:
            print("  Column already exists — skipping ALTER TABLE.")
    print()

    # ── Step 3: Load CSV ──────────────────────────────────────────────────────
    print("Step 3/4 — Loading CSV interaction data...")
    csv_data = load_csv_interactions(args.limit)
    print(f"  Unique product names loaded from CSV: {len(csv_data):,}")
    print()

    # ── Step 4: Backfill ──────────────────────────────────────────────────────
    print("Step 4/4 — Backfilling medicines table...")
    stats = backfill(conn, csv_data, dry_run=args.dry_run)

    print(f"  Total medicines in DB:       {stats['total_db_medicines']:>7,}")
    print(f"  CSV names available:         {stats['csv_names_loaded']:>7,}")
    print(f"  Matched and updated:         {stats['matched_and_updated']:>7,}")
    print(f"    → with actual drug data:   {stats['set_to_has_data']:>7,}")
    print(f"    → with empty arrays:       {stats['set_to_empty_array']:>7,}")
    print(f"  Unmatched (left as NULL):    {stats['unmatched_db_rows']:>7,}")
    print()

    # ── Verification ──────────────────────────────────────────────────────────
    if not args.dry_run:
        print("=" * 65)
        print("VERIFICATION — Reading back from database")
        print("=" * 65)
        v = verify(conn)
        print(f"  Total medicine records:      {v['total_medicines']:>7,}")
        print(f"  drug_interactions IS NULL:   {v['null_count']:>7,}")
        print(f"  drug_interactions non-NULL:  {v['non_null_count']:>7,}")
        print(f"    → empty arrays (no data):  {v['empty_array_count']:>7,}")
        print(f"    → has actual drug data:    {v['has_data_count']:>7,}")
        print()
        print("  Other tables (must be unchanged):")
        for table, count in v["other_tables"].items():
            print(f"    {table:<20} {count:>6,} rows")
        print()

        ok = v["total_medicines"] == 7466
        if ok:
            print("  ✓ All 7,466 medicine records intact.")
        else:
            print(f"  ✗ UNEXPECTED medicine count: {v['total_medicines']} (expected 7,466)")

        total_accounted = v["null_count"] + v["non_null_count"]
        if total_accounted == 7466:
            print("  ✓ NULL + non-NULL accounts for all 7,466 rows.")
        else:
            print(f"  ✗ NULL ({v['null_count']}) + non-NULL ({v['non_null_count']}) = "
                  f"{total_accounted} (expected 7,466)")
    else:
        print("[DRY RUN] Verification skipped — no changes were made.")

    conn.close()

    print()
    print("=" * 65)
    if args.dry_run:
        print("DRY RUN complete. Run without --dry-run to apply changes.")
    else:
        print("Backfill complete.")
    print("=" * 65)


if __name__ == "__main__":
    main()
