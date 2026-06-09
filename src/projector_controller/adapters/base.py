"""Protocols shared by concrete projection backends."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from projector_controller.config import FitMode, PixelFormat, Size


class ProjectionBackend(Protocol):
    """Minimal contract a backend must satisfy for ProjectionWindow."""

    def open(self) -> None:
        """Create the projection window."""

    def close(self) -> None:
        """Close the projection window and release backend resources."""

    def show_image(self, path: str | Path, *, fit_mode: FitMode | None = None) -> None:
        """Draw an image file to the projection window."""

    def show_test_pattern(self) -> None:
        """Draw a generated test pattern to the projection window."""

    def show_frame(
        self,
        data: bytes | bytearray | memoryview,
        size: Size | tuple[int, int],
        *,
        pixel_format: PixelFormat = "RGB",
        fit_mode: FitMode | None = None,
    ) -> None:
        """Draw a raw pixel buffer (RGB/RGBA, tightly packed) to the window."""

    def poll_events(self) -> bool:
        """Process backend events. Return False when the window should close."""

    def wait(self, seconds: float | None = None) -> None:
        """Keep the window alive for a duration, or until the user closes it."""
