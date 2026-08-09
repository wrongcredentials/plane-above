from typing import Any

import httpx

from .locker import SourceLock, SourceLockedError, SourceUnavailableError

TIMEOUT = httpx.Timeout(connect=2.0, read=4.0, write=2.0, pool=1.0)


class PlaneAboveClient(httpx.AsyncClient):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.source_lock = SourceLock()
        self.timeout = TIMEOUT

    async def send(self, request: httpx.Request, *args: Any, **kwargs: Any) -> httpx.Response:
        source = request.url.host

        if self.source_lock.is_locked(source):
            raise SourceLockedError(source)

        try:
            response = await super().send(request, *args, **kwargs)

        except httpx.TimeoutException as exc:
            self.source_lock.lock(source)
            raise SourceUnavailableError(source) from exc

        if httpx.codes.is_server_error(response.status_code):
            self.source_lock.lock(source)
            raise SourceUnavailableError(source)

        return response
