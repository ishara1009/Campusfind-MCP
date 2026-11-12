from openai import APIError, OpenAI
from pydantic import BaseModel, ConfigDict

from app.config import get_settings
from app.schemas import SearchFilters


class SearchExtraction(BaseModel):
    item_name: str | None
    category: str | None
    color: str | None
    found_location: str | None
    date_from: str | None
    date_to: str | None

    model_config = ConfigDict(extra="forbid")


class SearchParserUnavailable(Exception):
    pass


SYSTEM_PROMPT = """You extract filters for a campus lost-and-found search.
Return only the schema fields. Understand English, simple Sinhala, and mixed input.
Translate dataset values to concise English (for example: කළු -> Black, පුස්තකාලය -> Library).
Never guess a color, location, date, category, or item. Use null when unspecified.
Dates must be YYYY-MM-DD. A single exact date may set both date_from and date_to.
If the input is unrelated or contains no supported search detail, return null for every field.
Do not write SQL and do not add fields.
"""


def parse_search_query(query: str) -> SearchFilters:
    settings = get_settings()
    if not settings.openai_api_key:
        raise SearchParserUnavailable(
            "Natural-language search is unavailable. Add an OpenAI API key or use manual search."
        )

    client = OpenAI(api_key=settings.openai_api_key, timeout=12.0, max_retries=1)
    try:
        completion = client.chat.completions.parse(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": query},
            ],
            response_format=SearchExtraction,
        )
        parsed = completion.choices[0].message.parsed
        if parsed is None:
            raise SearchParserUnavailable("The search query could not be understood. Try manual search.")
        return SearchFilters.model_validate(parsed.model_dump())
    except SearchParserUnavailable:
        raise
    except (APIError, ValueError, IndexError, AttributeError) as error:
        raise SearchParserUnavailable(
            "Natural-language search is temporarily unavailable. Please use manual search."
        ) from error
