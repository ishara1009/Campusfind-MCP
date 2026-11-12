from datetime import date, datetime
from typing import Any

from mysql.connector import IntegrityError, MySQLConnection


ITEM_COLUMNS = """
    id, reference_code, item_name, category, color,
    found_location, found_date, description, status, created_at
"""


def _serialize_row(row: dict[str, Any] | None) -> dict[str, Any] | None:
    if row is None:
        return None
    serialized = dict(row)
    for key in ("found_date", "created_at"):
        value = serialized.get(key)
        if isinstance(value, (date, datetime)):
            serialized[key] = value.isoformat()
    return serialized


def search_items(connection: MySQLConnection, filters: dict[str, Any]) -> list[dict[str, Any]]:
    clauses = ["status = 'available'"]
    values: list[Any] = []

    if filters.get("item_name"):
        clauses.append("INSTR(LOWER(item_name), LOWER(%s)) > 0")
        values.append(filters["item_name"])
    for field_name in ("category", "color", "found_location"):
        if filters.get(field_name):
            clauses.append(f"LOWER({field_name}) = LOWER(%s)")
            values.append(filters[field_name])
    if filters.get("date_from"):
        clauses.append("found_date >= %s")
        values.append(filters["date_from"])
    if filters.get("date_to"):
        clauses.append("found_date <= %s")
        values.append(filters["date_to"])

    query = f"""
        SELECT {ITEM_COLUMNS}
        FROM found_items
        WHERE {' AND '.join(clauses)}
        ORDER BY found_date DESC, id DESC
        LIMIT 30
    """
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(query, tuple(values))
        return [_serialize_row(row) for row in cursor.fetchall()]
    finally:
        cursor.close()


def create_item(
    connection: MySQLConnection,
    reference_code: str,
    item: dict[str, Any],
) -> dict[str, Any]:
    query = """
        INSERT INTO found_items (
            reference_code, item_name, category, color,
            found_location, found_date, description, status
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, 'available')
    """
    values = (
        reference_code,
        item["item_name"],
        item["category"],
        item["color"],
        item["found_location"],
        item["found_date"],
        item.get("description"),
    )
    cursor = connection.cursor()
    try:
        cursor.execute(query, values)
        new_id = cursor.lastrowid
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
    saved = get_item_by_id(connection, new_id)
    if saved is None:
        raise RuntimeError("The report was saved but could not be read back")
    return saved


def get_item_by_id(connection: MySQLConnection, item_id: int) -> dict[str, Any] | None:
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            f"SELECT {ITEM_COLUMNS} FROM found_items WHERE id = %s",
            (item_id,),
        )
        return _serialize_row(cursor.fetchone())
    finally:
        cursor.close()


def get_item_by_reference(
    connection: MySQLConnection, reference_code: str
) -> dict[str, Any] | None:
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            f"SELECT {ITEM_COLUMNS} FROM found_items WHERE reference_code = %s",
            (reference_code,),
        )
        return _serialize_row(cursor.fetchone())
    finally:
        cursor.close()


def is_reference_collision(error: IntegrityError) -> bool:
    return error.errno == 1062 and "reference_code" in str(error).lower()
