import os

import httpx

from plane_above.static.enums import DataSource

HEADERS = {"User-Agent": os.environ["USER_AGENT"]}
PROXY_URL = os.environ.get("PROXY_URL") or None
PROXY_MOUNTS = {f"all://{DataSource.AD}": httpx.AsyncHTTPTransport(proxy=PROXY_URL)} if PROXY_URL else None
