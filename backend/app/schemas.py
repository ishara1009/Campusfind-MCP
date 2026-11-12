from datetime import date, datetime
from typing import Literal
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class SearchFilters(BaseModel):
    item_name: str | None = None
    category: str | None = None
    color: str | None = None
    found_location: str | None = None
    date_from: date | None = None
    date_to: date | None = None

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def clean_and_validate(self) -> "SearchFilters":
        for field_name in ("item_name", "category", "color", "found_location"):
            value = getattr(self, field_name)
            if value is not None:
                cleaned = value.strip()
                setattr(self, field_name, cleaned or None)
        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise ValueError("date_from must be on or before date_to")
        return self

    def has_filter(self) -> bool:
        return any(value is not None for value in self.model_dump().values())


class SearchRequest(BaseModel):
    query: str | None = None
    filters: SearchFilters | None = None

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def require_exactly_one_mode(self) -> "SearchRequest":
        has_query = self.query is not None
        has_filters = self.filters is not None
        if has_query == has_filters:
            raise ValueError("Provide exactly one of query or filters")
        if self.query is not None:
            self.query = self.query.strip()
            if not self.query:
                raise ValueError("query must not be blank")
        return self


class FoundItem(BaseModel):
    id: int
    reference_code: str
    item_name: str
    category: str
    color: str
    found_location: str
    found_date: date
    description: str | None = None
    status: Literal["available", "returned"]
    created_at: datetime | None = None


class SearchResponse(BaseModel):
    items: list[FoundItem]


class ReportFoundItemRequest(BaseModel):
    item_name: str = Field(min_length=1, max_length=150)
    category: str = Field(min_length=1, max_length=80)
    color: str = Field(min_length=1, max_length=80)
    found_location: str = Field(min_length=1, max_length=150)
    found_date: date
    description: str | None = Field(default=None, max_length=2000)

    model_config = ConfigDict(extra="forbid")

    @field_validator("found_date")
    @classmethod
    def reject_future_date(cls, value: date) -> date:
        if value > datetime.now(ZoneInfo("Asia/Colombo")).date():
            raise ValueError("found_date cannot be in the future")
        return value

    @model_validator(mode="after")
    def trim_text(self) -> "ReportFoundItemRequest":
        for field_name in ("item_name", "category", "color", "found_location"):
            cleaned = getattr(self, field_name).strip()
            if not cleaned:
                raise ValueError(f"{field_name} must not be blank")
            setattr(self, field_name, cleaned)
        if self.description is not None:
            self.description = self.description.strip() or None
        return self


class ReportResponse(BaseModel):
    reference_code: str
    item: FoundItem


class StatusResponse(BaseModel):
    found: bool
    item: FoundItem
