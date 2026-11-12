import logging
import secrets
import sys
from datetime import date, datetime
from typing import Any
from zoneinfo import ZoneInfo

from mcp.server.fastmcp import FastMCP
from mysql.connector import IntegrityError

from campusfind_mcp.database import database_connection
from campusfind_mcp.items_repository import (
    create_item,
    get_item_by_reference,
    is_reference_collision,
    search_items,
)


logging.basicConfig(stream=sys.stderr, level=logging.INFO)
logger = logging.getLogger("campusfind-mcp")
mcp = FastMCP("CampusFind")


def _clean_optional(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


@mcp.tool()
def search_found_items(
    item_name: str | None = None,
    category: str | None = None,
    color: str | None = None,
    found_location: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """Search available found-item reports using one or more filters."""
    filters: dict[str, Any] = {
        "item_name": _clean_optional(item_name),
        "category": _clean_optional(category),
        "color": _clean_optional(color),
        "found_location": _clean_optional(found_location),
    }
    for field_name, value in (("date_from", date_from), ("date_to", date_to)):
        cleaned = _clean_optional(value)
        if cleaned:
            try:
                filters[field_name] = date.fromisoformat(cleaned)
            except ValueError as error:
                raise ValueError(f"{field_name} must use YYYY-MM-DD format") from error
        else:
            filters[field_name] = None

    if not any(filters.values()):
        raise ValueError("At least one search filter is required")
    if filters["date_from"] and filters["date_to"]:
        if filters["date_from"] > filters["date_to"]:
            raise ValueError("date_from must be on or before date_to")

    with database_connection() as connection:
        return {"items": search_items(connection, filters)}


@mcp.tool()
def report_found_item(
    item_name: str,
    category: str,
    color: str,
    found_location: str,
    found_date: str,
    description: str | None = None,
) -> dict[str, Any]:
    """Save a new found-item report and return its reference code."""
    required = {
        "item_name": item_name,
        "category": category,
        "color": color,
        "found_location": found_location,
        "found_date": found_date,
    }
    cleaned: dict[str, Any] = {}
    for field_name, value in required.items():
        normalized = value.strip() if isinstance(value, str) else ""
        if not normalized:
            raise ValueError(f"{field_name} must not be blank")
        cleaned[field_name] = normalized

    try:
        parsed_date = date.fromisoformat(cleaned["found_date"])
    except ValueError as error:
        raise ValueError("found_date must use YYYY-MM-DD format") from error
    today_in_colombo = date.today()
    try:
        today_in_colombo = datetime.now(ZoneInfo("Asia/Colombo")).date()
    except (KeyError, OSError):
        logger.warning("Asia/Colombo timezone data unavailable; using local date")
    if parsed_date > today_in_colombo:
        raise ValueError("found_date cannot be in the future")

    cleaned["found_date"] = parsed_date
    cleaned["description"] = _clean_optional(description)

    with database_connection() as connection:
        for _ in range(5):
            reference_code = f"CF-{secrets.token_hex(4).upper()}"
            try:
                saved = create_item(connection, reference_code, cleaned)
                return {"reference_code": reference_code, "item": saved}
            except IntegrityError as error:
                if is_reference_collision(error):
                    continue
                raise
    raise RuntimeError("Could not generate a unique reference code")


@mcp.tool()
def get_report_status(reference_code: str) -> dict[str, Any]:
    """Look up a report by reference code, including returned reports."""
    normalized = reference_code.strip().upper()
    if not normalized:
        raise ValueError("reference_code must not be blank")
    with database_connection() as connection:
        item = get_item_by_reference(connection, normalized)
    if item is None:
        return {
            "found": False,
            "reference_code": normalized,
            "message": "No report was found for that reference code.",
        }
    return {"found": True, "item": item}


if __name__ == "__main__":
    mcp.run(transport="stdio")
