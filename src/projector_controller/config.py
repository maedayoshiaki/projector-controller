"""Typed configuration objects used by the public API and adapters."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

type FitMode = Literal["contain", "cover", "stretch", "native"]
type ColorValue = str | tuple[int, int, int] | tuple[int, int, int, int]
# Pixel layout of a raw frame buffer passed to ProjectionWindow.show_frame. These are
# pygame.image.frombuffer format strings; bytes-per-pixel is fixed per format.
type PixelFormat = Literal["RGB", "RGBA"]

VALID_FIT_MODES: frozenset[str] = frozenset(("contain", "cover", "stretch", "native"))
PIXEL_FORMAT_BYTES: dict[PixelFormat, int] = {"RGB": 3, "RGBA": 4}


@dataclass(frozen=True)
class Size:
    """Pixel dimensions."""

    width: int
    height: int

    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0:
            msg = "width and height must be positive"
            raise ValueError(msg)

    @classmethod
    def from_tuple(cls, value: tuple[int, int]) -> Size:
        return cls(width=value[0], height=value[1])

    def as_tuple(self) -> tuple[int, int]:
        return (self.width, self.height)


@dataclass(frozen=True)
class Point:
    """Desktop coordinate point."""

    x: int
    y: int

    @classmethod
    def from_tuple(cls, value: tuple[int, int]) -> Point:
        return cls(x=value[0], y=value[1])

    def as_tuple(self) -> tuple[int, int]:
        return (self.x, self.y)


@dataclass(frozen=True)
class WindowGeometry:
    """Desktop position and pixel size for a projection window."""

    x: int
    y: int
    width: int
    height: int

    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0:
            msg = "width and height must be positive"
            raise ValueError(msg)

    @classmethod
    def from_position_size(cls, position: Point, size: Size) -> WindowGeometry:
        return cls(x=position.x, y=position.y, width=size.width, height=size.height)

    @property
    def position(self) -> Point:
        return Point(self.x, self.y)

    @property
    def size(self) -> Size:
        return Size(self.width, self.height)

    def as_rect_tuple(self) -> tuple[int, int, int, int]:
        return (self.x, self.y, self.width, self.height)


@dataclass(frozen=True)
class DisplaySpec:
    """Display information reported by a backend."""

    index: int
    size: Size
    name: str | None = None

    def __post_init__(self) -> None:
        if self.index < 0:
            msg = "display index must be non-negative"
            raise ValueError(msg)


@dataclass(frozen=True)
class ProjectionConfig:
    """Projection window configuration independent from a concrete backend."""

    display: int | None = 0
    fullscreen: bool = False
    # position is None means "let the backend center the window on the target display".
    # A concrete Point means absolute desktop coordinates (origin = top-left of the
    # whole desktop). See docs/ARCHITECTURE.md "Window Placement".
    position: Point | None = None
    size: Size = field(default_factory=lambda: Size(1280, 720))
    fit_mode: FitMode = "contain"
    background: ColorValue = "black"
    borderless: bool = False

    def __post_init__(self) -> None:
        if self.display is not None and self.display < 0:
            msg = "display index must be non-negative"
            raise ValueError(msg)
        if self.fit_mode not in VALID_FIT_MODES:
            msg = f"unsupported fit mode: {self.fit_mode}"
            raise ValueError(msg)


def normalize_fit_mode(value: str) -> FitMode:
    """Validate a user-provided fit mode and narrow it for type checkers."""

    if value not in VALID_FIT_MODES:
        msg = f"unsupported fit mode: {value}"
        raise ValueError(msg)
    return value  # type: ignore[return-value]


def normalize_pixel_format(value: str) -> PixelFormat:
    """Validate a user-provided pixel format and narrow it for type checkers."""

    if value not in PIXEL_FORMAT_BYTES:
        msg = f"unsupported pixel format: {value}"
        raise ValueError(msg)
    # ``value in dict[PixelFormat, int]`` lets mypy narrow str -> PixelFormat here, so
    # (unlike normalize_fit_mode against a frozenset[str]) no return-value ignore is needed.
    return value
