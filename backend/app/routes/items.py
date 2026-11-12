import asyncio

from fastapi import APIRouter, HTTPException, status

from app.schemas import (
    ReportFoundItemRequest,
    ReportResponse,
    SearchRequest,
    SearchResponse,
    StatusResponse,
)
from app.services.mcp_client import CampusFindMCPError, call_tool
from app.services.search_parser import SearchParserUnavailable, parse_search_query


router = APIRouter(prefix="/api/items", tags=["items"])


def _no_filters_error() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail="Add an item, color, location, category, or date to search.",
    )


@router.post("/search", response_model=SearchResponse)
async def search_items(request: SearchRequest) -> dict:
    if request.query is not None:
        try:
            filters = await asyncio.to_thread(parse_search_query, request.query)
        except SearchParserUnavailable as error:
            raise HTTPException(status_code=503, detail=str(error)) from error
    else:
        filters = request.filters

    if filters is None or not filters.has_filter():
        raise _no_filters_error()

    arguments = filters.model_dump(mode="json", exclude_none=True)
    try:
        result = await call_tool("search_found_items", arguments)
    except CampusFindMCPError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error
    return {"items": result.get("items", [])}


@router.post("", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def report_item(request: ReportFoundItemRequest) -> dict:
    try:
        return await call_tool(
            "report_found_item",
            request.model_dump(mode="json", exclude_none=True),
        )
    except CampusFindMCPError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error


@router.get("/{reference_code}", response_model=StatusResponse)
async def get_item_status(reference_code: str) -> dict:
    normalized = reference_code.strip().upper()
    if not normalized:
        raise HTTPException(status_code=422, detail="Reference code is required.")
    try:
        result = await call_tool("get_report_status", {"reference_code": normalized})
    except CampusFindMCPError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error
    if not result.get("found"):
        raise HTTPException(status_code=404, detail="No report was found for that reference code.")
    return result
