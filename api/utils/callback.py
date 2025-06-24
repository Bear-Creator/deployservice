"""Callback utilities for the DeployService API."""

import asyncio
from typing import Any, Dict

import aiohttp
import structlog

from api.config import settings

logger = structlog.get_logger(__name__)


def serialize_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Serialize data for JSON transmission, handling AnyHttpUrl objects."""

    def _serialize_value(value: Any) -> Any:
        if hasattr(value, '__str__'):
            return str(value)
        elif isinstance(value, dict):
            return {k: _serialize_value(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [_serialize_value(v) for v in value]
        return value

    return _serialize_value(data)  # type: ignore


async def send_callback(url: str, data: Dict[str, Any]) -> None:
    """Send callback to the specified URL."""
    try:
        # Serialize data to handle AnyHttpUrl objects
        serialized_data = serialize_data(data)

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                json=serialized_data,
                timeout=aiohttp.ClientTimeout(total=settings.callback_timeout),
            ) as response:
                if response.status >= 400:
                    logger.warning(
                        "Callback failed",
                        url=url,
                        status=response.status,
                        response=await response.text(),
                    )
                else:
                    logger.info(
                        "Callback sent successfully", url=url, status=response.status
                    )
    except asyncio.TimeoutError:
        logger.error("Callback timeout", url=url)
    except Exception as e:
        logger.error("Callback error", url=url, error=str(e))
