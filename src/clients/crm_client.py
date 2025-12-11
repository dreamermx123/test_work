from functools import lru_cache

import backoff
from httpx import AsyncClient, HTTPStatusError, TransportError

from clients.base import AbstractHTTPClient
from core.config import settings
from logger import logger

RETRYABLE_STATUSES: set[int] = {429, 500, 502, 503, 504}
MAX_RETRIES = 5


def _give_up(exc: Exception) -> bool:
    if isinstance(exc, HTTPStatusError):
        return exc.response.status_code not in RETRYABLE_STATUSES
    return False


class CrmClient(AbstractHTTPClient):
    @backoff.on_exception(
        backoff.expo,
        (TransportError, HTTPStatusError),
        max_tries=MAX_RETRIES,
        giveup=_give_up,
        jitter=backoff.full_jitter,
    )
    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, object] | None = None,
        data: dict[str, object] | None = None,
        json: dict[str, object] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, object]:
        async with AsyncClient() as client:
            try:
                response = await client.request(
                    method=method,
                    url=f"{settings.base_url}{path}",
                    headers={"X-API-KEY": settings.api_key, **(headers or {})},
                    params=params or {},
                    data=data,
                    json=json,
                )
                response.raise_for_status()
                return response.json()

            except HTTPStatusError as exc:
                logger.error("RetailCRM %s: %s", exc.response.status_code, exc)
                raise
            except TransportError as exc:
                logger.error("CRM transport error: %s", exc)
                raise

    async def get(
        self,
        path: str,
        params: dict[str, object] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, object]:
        return await self._request(
            "GET",
            path,
            params=params,
            headers=headers,
        )

    async def post(
        self,
        path: str,
        *,
        params: dict[str, object] | None = None,
        data: dict[str, object] | None = None,
        json: dict[str, object] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, object]:
        return await self._request(
            "POST",
            path,
            params=params,
            data=data,
            json=json,
            headers=headers,
        )


crm_client = CrmClient()


@lru_cache
def get_crm_client() -> CrmClient:
    return crm_client
