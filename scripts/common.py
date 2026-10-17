import os

import httpx

HEADERS = {"User-Agent": os.environ["PS_USER_AGENT"]}
PROXY_URL = os.environ.get("PROXY_URL") or None
PROXY_MOUNTS = {"all://airport-data.com": httpx.AsyncHTTPTransport(proxy=PROXY_URL)} if PROXY_URL else None
