import csv
import sys
from datetime import datetime
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
REPOSITORY_DIR = BACKEND_DIR.parent
CSV_PATH = REPOSITORY_DIR / "database" / "campusfind_found_items.csv"
sys.path.insert(0, str(BACKEND_DIR))

from campusfind_mcp.database import database_connection  # noqa: E402


EXPECTED_COLUMNS = {
    "reference_code",
    "item_name",
    "category",
    "color",
    "found_location",
    "found_date",
    "description",
    "status",
}


def parse_date(raw_value: str, row_number: int):
    value = raw_value.strip()
    for date_format in ("%Y-%m-%d", "%m/%d/%Y"):
        try:
            return datetime.strptime(value, date_format).date()
        except ValueError:
            pass
    raise ValueError(f"Row {row_number}: invalid found_date {value!r}")


def clean_row(row: dict[str, str], row_number: int) -> dict[str, object]:
    cleaned = {key.strip().lstrip("\ufeff"): (value or "").strip() for key, value in row.items() if key}
    missing_columns = EXPECTED_COLUMNS - cleaned.keys()
    if missing_columns:
        raise ValueError(f"Missing CSV columns: {', '.join(sorted(missing_columns))}")

    required = EXPECTED_COLUMNS - {"description"}
    blank_fields = [field for field in required if not cleaned[field]]
    if blank_fields:
        raise ValueError(f"Row {row_number}: blank fields: {', '.join(sorted(blank_fields))}")
    if cleaned["status"] not in {"available", "returned"}:
        raise ValueError(f"Row {row_number}: status must be available or returned")

    cleaned["found_date"] = parse_date(cleaned["found_date"], row_number)
    cleaned["description"] = cleaned["description"] or None
    return {key: cleaned[key] for key in EXPECTED_COLUMNS}


def import_dataset() -> None:
    if not CSV_PATH.exists():
        print(f"CSV file not found: {CSV_PATH}")
        return

    inserted = 0
    skipped = 0
    insert_sql = """
        INSERT INTO found_items (
            reference_code, item_name, category, color, found_location,
            found_date, description, status
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as csv_file:
        rows = list(csv.DictReader(csv_file))

    with database_connection() as connection:
        cursor = connection.cursor()
        try:
            for row_number, raw_row in enumerate(rows, start=2):
                row = clean_row(raw_row, row_number)
                cursor.execute(
                    "SELECT 1 FROM found_items WHERE reference_code = %s",
                    (row["reference_code"],),
                )
                if cursor.fetchone():
                    skipped += 1
                    continue
                cursor.execute(
                    insert_sql,
                    (
                        row["reference_code"], row["item_name"], row["category"],
                        row["color"], row["found_location"], row["found_date"],
                        row["description"], row["status"],
                    ),
                )
                inserted += 1
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            cursor.close()
    print(f"Import complete. Inserted: {inserted}; skipped: {skipped}")


if __name__ == "__main__":
    import_dataset()
