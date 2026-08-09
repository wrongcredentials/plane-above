import json
from typing import Any
from dataclasses import dataclass

import httpx

from .locker import SourceLockedError, SourceUnavailableError
from ..logger import log


@dataclass(frozen=True, slots=True)
class HttpResult:
    status_code: int
    data: str
    json_data: dict


async def async_get(async_client: httpx.AsyncClient, *args: Any, **kwargs: Any) -> HttpResult:
    try:
        r = await async_client.get(*args, **kwargs)
        r.raise_for_status()
        if "application/json" in r.headers.get("content-type", "").lower():
            return HttpResult(r.status_code, r.text, r.json())
        return HttpResult(r.status_code, r.text, {})

    except SourceLockedError as exc:
        log.warning(f" ✈ Source is locked: {exc}")
        return HttpResult(httpx.codes.SERVICE_UNAVAILABLE, "", {})

    except SourceUnavailableError as exc:
        log.error(f" ✈ Source unavailable: {exc}; locking for future calls.")
        return HttpResult(httpx.codes.GATEWAY_TIMEOUT, "", {})

    except json.JSONDecodeError as exc:
        log.error(f" ✈ Exception occurred with parsing json: {exc}")
        return HttpResult(httpx.codes.INTERNAL_SERVER_ERROR, "", {})

    except httpx.HTTPStatusError:
        return HttpResult(r.status_code, "", {})

    except httpx.HTTPError as exc:
        log.error(f" ✈ Exception occurred with request: {exc}")
        return HttpResult(httpx.codes.SERVICE_UNAVAILABLE, "", {})
