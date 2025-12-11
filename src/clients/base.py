from abc import ABC, abstractmethod
from typing import Any, Mapping


class AbstractHTTPClient(ABC):

    @abstractmethod
    async def get(  # noqa
        self,
        path: str,
        params: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> Any: ...

    @abstractmethod
    async def post(  # noqa
        self,
        path: str,
        body: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> Any: ...
