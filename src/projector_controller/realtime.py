"""Python facade for the Rust realtime frame renderer."""

from __future__ import annotations

import socket
import struct
import subprocess
import sys
import time
from pathlib import Path
from types import TracebackType
from typing import IO, Literal, Self

from projector_controller.config import FitMode, Point, Size, normalize_fit_mode

FramePixelFormat = Literal["rgba8", "bgra8"]

_FRAME_HEADER = struct.Struct("<4sIIBBHI")
_FRAME_MAGIC = b"PCF1"
_QUIT_MAGIC = b"PCQ1"
_PIXEL_FORMATS: dict[FramePixelFormat, int] = {"rgba8": 1, "bgra8": 2}
_FIT_MODES: dict[FitMode | None, int] = {
    None: 0,
    "contain": 1,
    "cover": 2,
    "stretch": 3,
    "native": 4,
}


class RealtimeProjection:
    """Control the Rust GPU frame renderer from Python.

    The renderer process owns the window, event loop, and GPU device. Python only starts
    the process and submits frames, keeping expensive rendering work outside the GIL.
    """

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
        self._process: subprocess.Popen[str] | None = None
        self._socket: socket.socket | None = None

    def open(self) -> Self:
        if self._process is not None:
            return self

        command = self._renderer_command()
        self._process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        try:
            address = self._read_ready_address()
            self._socket = socket.create_connection(address, timeout=self.connect_timeout)
            self._socket.settimeout(None)
        except Exception:
            self.close()
            raise
        return self

    def close(self) -> None:
        sock = self._socket
        self._socket = None
        if sock is not None:
            try:
                sock.sendall(_encode_quit_header())
            except OSError:
                pass
            sock.close()

        process = self._process
        self._process = None
        if process is None:
            return
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.terminate()
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=2)

    def submit_frame(
        self,
        data: bytes | bytearray | memoryview,
        *,
        width: int,
        height: int,
        pixel_format: FramePixelFormat = "rgba8",
        fit_mode: FitMode | None = None,
    ) -> None:
        if width <= 0 or height <= 0:
            msg = "width and height must be positive"
            raise ValueError(msg)
        if pixel_format not in _PIXEL_FORMATS:
            msg = f"unsupported pixel format: {pixel_format}"
            raise ValueError(msg)
        normalized_fit_mode = normalize_fit_mode(fit_mode) if fit_mode is not None else None
        payload = memoryview(data).cast("B")
        expected = width * height * 4
        if payload.nbytes != expected:
            msg = f"frame byte length mismatch: got {payload.nbytes}, expected {expected}"
            raise ValueError(msg)

        sock = self._ensure_socket()
        sock.sendall(
            _encode_frame_header(
                width=width,
                height=height,
                pixel_format=pixel_format,
                fit_mode=normalized_fit_mode,
                byte_length=payload.nbytes,
            )
        )
        sock.sendall(payload)

    def __enter__(self) -> Self:
        return self.open()

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()

    def _renderer_command(self) -> list[str]:
        binary = self.renderer_path or find_renderer_binary()
        command = [
            str(binary),
            "--bind",
            "127.0.0.1:0",
            "--display",
            str(self.display),
            "--width",
            str(self.size.width),
            "--height",
            str(self.size.height),
            "--fit-mode",
            self.fit_mode,
        ]
        if self.fullscreen:
            command.append("--fullscreen")
        if self.position is not None:
            command.extend(["--x", str(self.position.x), "--y", str(self.position.y)])
        return command

    def _read_ready_address(self) -> tuple[str, int]:
        process = self._ensure_process()
        stdout = process.stdout
        if stdout is None:
            msg = "renderer stdout is not available"
            raise RuntimeError(msg)

        deadline = time.monotonic() + self.connect_timeout
        while time.monotonic() < deadline:
            if process.poll() is not None:
                raise RuntimeError(_renderer_exit_message(process))
            line = stdout.readline()
            if not line:
                continue
            parts = line.strip().split(maxsplit=1)
            if len(parts) == 2 and parts[0] == "READY":
                host, port_text = parts[1].rsplit(":", maxsplit=1)
                return host, int(port_text)

        msg = "renderer did not report READY before timeout"
        raise TimeoutError(msg)

    def _ensure_process(self) -> subprocess.Popen[str]:
        if self._process is None:
            msg = "renderer process is not open"
            raise RuntimeError(msg)
        return self._process

    def _ensure_socket(self) -> socket.socket:
        if self._socket is None:
            msg = "realtime projection is not open"
            raise RuntimeError(msg)
        return self._socket


def find_renderer_binary() -> Path:
    """Return the Rust renderer binary path for local development."""

    exe = (
        "projector-controller-renderer.exe"
        if sys.platform == "win32"
        else "projector-controller-renderer"
    )
    repo_root = Path(__file__).resolve().parents[2]
    candidates = [
        repo_root / "target" / "debug" / exe,
        repo_root / "target" / "release" / exe,
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate

    msg = (
        "Rust renderer binary not found. Build it with "
        "`cargo build -p projector-controller-renderer` or pass renderer_path=..."
    )
    raise FileNotFoundError(msg)


def _encode_frame_header(
    *,
    width: int,
    height: int,
    pixel_format: FramePixelFormat,
    fit_mode: FitMode | None,
    byte_length: int,
) -> bytes:
    return _FRAME_HEADER.pack(
        _FRAME_MAGIC,
        width,
        height,
        _PIXEL_FORMATS[pixel_format],
        _FIT_MODES[fit_mode],
        0,
        byte_length,
    )


def _encode_quit_header() -> bytes:
    return _FRAME_HEADER.pack(_QUIT_MAGIC, 0, 0, 0, 0, 0, 0)


def _renderer_exit_message(process: subprocess.Popen[str]) -> str:
    stderr = _read_remaining(process.stderr)
    if stderr:
        return f"renderer exited with code {process.returncode}: {stderr.strip()}"
    return f"renderer exited with code {process.returncode}"


def _read_remaining(stream: IO[str] | None) -> str:
    if stream is None:
        return ""
    data = stream.read()
    return data
