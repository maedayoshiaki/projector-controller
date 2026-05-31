"""Public ProjectionWindow facade."""

from __future__ import annotations

from pathlib import Path
from types import TracebackType
from typing import Self

from projector_controller.adapters.base import ProjectionBackend
from projector_controller.config import (
    ColorValue,
    FitMode,
    Point,
    ProjectionConfig,
    Size,
    WindowGeometry,
)

# Placement is expressed by (position, size). ``position is None`` asks the backend to
# center the window on the target display; a concrete Point is absolute desktop
# coordinates. The legacy ``geometry`` argument, when given, is treated as an explicit
# position + size (it cannot express "centered").


class ProjectionWindow:
    """High-level projection window API.

    The facade keeps public code independent from pygame so future backends can be
    added without changing call sites.
    """

    def __init__(
        self,
        *,
        display: int | None = 0,
        fullscreen: bool = False,
        geometry: WindowGeometry | None = None,
        position: Point | tuple[int, int] | None = None,
        size: Size | tuple[int, int] = (1280, 720),
        fit_mode: FitMode = "contain",
        background: ColorValue = "black",
        borderless: bool = False,
        backend: str = "pygame",
    ) -> None:
        resolved_position, resolved_size = _resolve_placement(
            geometry=geometry, position=position, size=size
        )
        self.config = ProjectionConfig(
            display=display,
            fullscreen=fullscreen,
            position=resolved_position,
            size=resolved_size,
            fit_mode=fit_mode,
            background=background,
            borderless=borderless,
        )
        self._backend_name = backend
        self._backend: ProjectionBackend | None = None

    def open(self) -> Self:
        if self._backend is None:
            self._backend = self._make_backend()
        self._backend.open()
        return self

    def close(self) -> None:
        if self._backend is None:
            return
        self._backend.close()

    def show_image(self, path: str | Path, *, fit_mode: FitMode | None = None) -> None:
        self._ensure_open().show_image(path, fit_mode=fit_mode)

    def show_test_pattern(self) -> None:
        self._ensure_open().show_test_pattern()

    def poll_events(self) -> bool:
        return self._ensure_open().poll_events()

    def wait(self, seconds: float | None = None) -> None:
        self._ensure_open().wait(seconds)

    def __enter__(self) -> Self:
        return self.open()

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()

    def _ensure_open(self) -> ProjectionBackend:
        if self._backend is None:
            self.open()
        assert self._backend is not None
        return self._backend

    def _make_backend(self) -> ProjectionBackend:
        if self._backend_name != "pygame":
            msg = f"unsupported backend: {self._backend_name}"
            raise ValueError(msg)

        from projector_controller.adapters.pygame_backend import PygameProjectionBackend

        return PygameProjectionBackend(self.config)


def _resolve_placement(
    *,
    geometry: WindowGeometry | None,
    position: Point | tuple[int, int] | None,
    size: Size | tuple[int, int],
) -> tuple[Point | None, Size]:
    """Resolve constructor arguments into (position, size).

    ``geometry`` (legacy) wins and is an explicit position. Otherwise ``position`` is
    used as-is: ``None`` keeps the centered-on-display default.
    """

    if geometry is not None:
        return geometry.position, geometry.size

    resolved_position = (
        position if position is None or isinstance(position, Point) else Point.from_tuple(position)
    )
    resolved_size = size if isinstance(size, Size) else Size.from_tuple(size)
    return resolved_position, resolved_size
