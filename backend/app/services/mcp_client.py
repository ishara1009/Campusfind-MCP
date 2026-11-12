import asyncio
import json
import os
import sys
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from app.config import BACKEND_DIR, get_settings


class CampusFindMCPError(Exception):
    pass


def _server_environment() -> dict[str, str]:
    settings = get_settings()
    environment = dict(os.environ)
    environment.update(
        {
            "MYSQL_HOST": settings.mysql_host,
            "MYSQL_PORT": str(settings.mysql_port),
            "MYSQL_USER": settings.mysql_user,
            "MYSQL_PASSWORD": settings.mysql_password,
            "MYSQL_DATABASE": settings.mysql_database,
        }
    )
    return environment


def _read_tool_result(result: Any) -> dict[str, Any]:
    if getattr(result, "isError", False):
        raise CampusFindMCPError("The CampusFind data service rejected the request.")
    structured = getattr(result, "structuredContent", None)
    if isinstance(structured, dict):
        return structured
    for content in getattr(result, "content", []):
        text = getattr(content, "text", None)
        if text:
            try:
                decoded = json.loads(text)
                if isinstance(decoded, dict):
                    return decoded
            except json.JSONDecodeError:
                continue
    raise CampusFindMCPError("The CampusFind data service returned an invalid response.")


async def call_tool(tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    settings = get_settings()
    server = StdioServerParameters(
        command=sys.executable,
        args=["-m", "campusfind_mcp.server"],
        env=_server_environment(),
        cwd=str(BACKEND_DIR),
    )
    try:
        async with asyncio.timeout(settings.mcp_timeout_seconds):
            async with stdio_client(server) as (read_stream, write_stream):
                async with ClientSession(read_stream, write_stream) as session:
                    await session.initialize()
                    result = await session.call_tool(tool_name, arguments=arguments)
                    return _read_tool_result(result)
    except CampusFindMCPError:
        raise
    except TimeoutError as error:
        raise CampusFindMCPError("The CampusFind data service timed out.") from error
    except Exception as error:
        raise CampusFindMCPError("The CampusFind data service is unavailable.") from error
