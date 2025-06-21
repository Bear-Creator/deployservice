"""Callback utilities for the DeployService API."""

import asyncio
from typing import Any, Dict

import aiohttp
import structlog

from api.config import settings

logger = structlog.get_logger(__name__)


async def send_callback(url: str, data: Dict[str, Any]) -> None:
    """Send callback to the specified URL."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                json=data,
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
