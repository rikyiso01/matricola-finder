from collections.abc import Callable
from typing import Any

class Site:
    @staticmethod
    def make_site(
        *,
        searchpath: str = ...,
        contexts: list[tuple[str, Callable[[], dict[str, Any]]]] = ...,
        outpath: str = ...,
    ) -> Site: ...
    def render(self, *, use_reloader: bool = ...) -> None: ...
