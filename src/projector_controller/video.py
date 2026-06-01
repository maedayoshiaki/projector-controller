"""High-level video playback: orchestrate the Rust renderer and a media process (case C).

The renderer stays a pure frame sink. ``VideoPlayer`` spawns it with ``backpressure=all``
(so no frame is dropped), then spawns a separate media process that decodes the file with
PyAV and pushes frames straight to the renderer. Python here never touches frame data.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from types import TracebackType
from typing import Self

from projector_controller.config import FitMode, Point, Size, normalize_fit_mode
from projector_controller.realtime import (
    RendererProcess,
    build_renderer_command,
    find_renderer_binary,
)


class VideoPlayer:
    """Play a video file by orchestrating the renderer and a dedicated media process."""

    def __init__(
        self,
        *,
        display: int = 0,
        fullscreen: bool = False,
        position: Point | tuple[int, int] | None = None,
        size: Size | tuple[int, int] = (1280, 720),
        fit_mode: FitMode = "contain",
        renderer_path: str | Path | None = None,
        connect_timeout: float = 5.0,
    ) -> None:
        if display < 0:
            msg = "display index must be non-negative"
            raise ValueError(msg)
        self.display = display
        self.fullscreen = fullscreen
        self.position = (
            position
            if position is None or isinstance(position, Point)
            else Point.from_tuple(position)
        )
        self.size = size if isinstance(size, Size) else Size.from_tuple(size)
        self.fit_mode = normalize_fit_mode(fit_mode)
        self.renderer_path = Path(renderer_path) if renderer_path is not None else None
        self.connect_timeout = connect_timeout
        self._renderer: RendererProcess | None = None

    def open(self) -> Self:
        if self._renderer is not None:
            return self

        binary = self.renderer_path or find_renderer_binary()
        # Video must not drop frames, so the renderer paces the producer (backpressure=all)
        # rather than keeping only the latest.
        command = build_renderer_command(
            binary,
            display=self.display,
            fullscreen=self.fullscreen,
            position=self.position,
            size=self.size,
            fit_mode=self.fit_mode,
            backpressure="all",
        )
        renderer = RendererProcess(command, connect_timeout=self.connect_timeout)
        self._renderer = renderer
        try:
            renderer.start()
        except Exception:
            self.close()
            raise
        return self

    def play(self, path: str | Path, *, fit_mode: FitMode | None = None) -> int:
        """Decode ``path`` in a separate media process feeding the renderer; wait for it.

        Returns the media process exit code. The media process sends the renderer a quit
        message when the file ends, so the projection window closes on completion.
        """

        renderer = self._renderer
        if renderer is None or renderer.address is None:
            msg = "video player is not open"
            raise RuntimeError(msg)
        host, port = renderer.address
        command = [
            sys.executable,
            "-m",
            "projector_controller.media",
            "--connect",
            f"{host}:{port}",
            "--file",
            str(path),
        ]
        if fit_mode is not None:
            command.extend(["--fit-mode", normalize_fit_mode(fit_mode)])
        return subprocess.run(command, check=False).returncode

    def close(self) -> None:
        renderer = self._renderer
        self._renderer = None
        if renderer is not None:
            renderer.close()

    def __enter__(self) -> Self:
        return self.open()

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()
