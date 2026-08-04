import httpx


class SourceLockedError(httpx.RequestError):
    pass


class SourceUnavailableError(httpx.RequestError):
    pass


class SourceLock:
    __slots__ = ("_locked",)

    def __init__(self) -> None:
        self._locked: set[str] = set()

    def is_locked(self, source: str) -> bool:
        return source in self._locked

    def lock(self, source: str) -> None:
        self._locked.add(source)
