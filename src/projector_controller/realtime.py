"""Python facade for the Rust realtime frame renderer."""

from __future__ import annotations

import os
import shutil
import socket
import struct
import subprocess
import sys
import sysconfig
import threading
import time
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from types import TracebackType
from typing import IO, Literal, Self

from projector_controller.config import FitMode, Point, Size, normalize_fit_mode

FramePixelFormat = Literal["rgba8", "bgra8"]
Backpressure = Literal["latest", "all"]

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
_MONITOR_PREFIX = "MONITOR"
_MONITOR_FIELDS = 8
# Env var an installed user can point at the renderer binary, taking precedence over
# PATH discovery. Useful when the binary lives outside PATH or for pinning a build.
_RENDERER_ENV_VAR = "PROJECTOR_CONTROLLER_RENDERER"


@dataclass(frozen=True)
class RendererMonitor:
    """A monitor as enumerated by the Rust renderer (winit).

    These indices are authoritative for the realtime path: ``index`` is exactly the
    value to pass as ``RealtimeProjection(display=...)``. They are produced by winit and
    may differ from the pygame-based ``list_displays()`` ordering, so prefer this when
    choosing a target monitor for the Rust renderer.
    """

    index: int
    name: str
    x: int
    y: int
    width: int
    height: int
    scale: float


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
        backpressure: Backpressure = "latest",
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
        if backpressure not in ("latest", "all"):
            msg = f"unsupported backpressure mode: {backpressure}"
            raise ValueError(msg)
        self.backpressure = backpressure
        self.renderer_path = Path(renderer_path) if renderer_path is not None else None
        self.connect_timeout = connect_timeout
        self._process: subprocess.Popen[str] | None = None
        self._socket: socket.socket | None = None
        # Bounded buffers fed by background drain threads so the renderer can never
        # block writing to a full stdout/stderr pipe. Kept for error diagnostics.
        self._stderr_lines: deque[str] = deque(maxlen=200)
        self._stdout_lines: deque[str] = deque(maxlen=50)
        self._drain_threads: list[threading.Thread] = []

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
            # Drain stderr from the start so a chatty renderer cannot fill the OS pipe
            # buffer and block its own thread. stdout is read directly until READY,
            # then drained the same way.
            self._spawn_drain(self._process.stderr, self._stderr_lines)
            address = self._read_ready_address()
            self._socket = socket.create_connection(address, timeout=self.connect_timeout)
            self._socket.settimeout(None)
            # Send small frame headers immediately instead of letting Nagle hold them
            # back waiting for the payload; frame latency matters more than packet count.
            self._socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            self._spawn_drain(self._process.stdout, self._stdout_lines)
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
        finally:
            self._join_drains(0.5)
            self._drain_threads.clear()

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
            "--backpressure",
            self.backpressure,
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
                raise RuntimeError(self._renderer_exit_message(process))
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

    def _spawn_drain(self, stream: IO[str] | None, sink: deque[str]) -> None:
        if stream is None:
            return
        thread = threading.Thread(target=_drain_stream, args=(stream, sink), daemon=True)
        thread.start()
        self._drain_threads.append(thread)

    def _join_drains(self, timeout: float) -> None:
        for thread in self._drain_threads:
            thread.join(timeout)

    def _renderer_exit_message(self, process: subprocess.Popen[str]) -> str:
        # The pipe is at EOF once the process has exited, so the drain thread finishes
        # quickly; join it to capture the full stderr before reporting.
        self._join_drains(0.5)
        stderr = "\n".join(self._stderr_lines).strip()
        if stderr:
            return f"renderer exited with code {process.returncode}: {stderr}"
        return f"renderer exited with code {process.returncode}"


def list_renderer_monitors(
    renderer_path: str | Path | None = None,
    *,
    timeout: float = 5.0,
) -> list[RendererMonitor]:
    """List monitors as seen by the Rust renderer (the authoritative realtime order).

    Runs the renderer with ``--list-monitors`` and parses its output. The returned
    indices match ``RealtimeProjection(display=...)``.
    """

    binary = Path(renderer_path) if renderer_path is not None else find_renderer_binary()
    result = subprocess.run(
        [str(binary), "--list-monitors"],
        capture_output=True,
        text=True,
        timeout=timeout,
        check=True,
    )
    return _parse_monitor_lines(result.stdout)


def _parse_monitor_lines(text: str) -> list[RendererMonitor]:
    monitors: list[RendererMonitor] = []
    for line in text.splitlines():
        # maxsplit keeps a name containing spaces (or empty) intact as the last field.
        parts = line.split("\t", _MONITOR_FIELDS - 1)
        if len(parts) != _MONITOR_FIELDS or parts[0] != _MONITOR_PREFIX:
            continue
        _, index, x, y, width, height, scale, name = parts
        monitors.append(
            RendererMonitor(
                index=int(index),
                name=name,
                x=int(x),
                y=int(y),
                width=int(width),
                height=int(height),
                scale=float(scale),
            )
        )
    return monitors


def find_renderer_binary() -> Path:
    """Locate the Rust renderer binary.

    Search order (first hit wins):

    1. ``PROJECTOR_CONTROLLER_RENDERER`` env var (must exist if set, else error).
    2. PATH via ``shutil.which`` — finds it when the venv's scripts dir is activated.
    3. This interpreter's ``sysconfig`` scripts dir — where the
       ``projector-controller-renderer`` wheel installs the binary, even when the venv
       is not on PATH (the common "just pip install and run a script" case).
    4. ``packages/renderer/target/{debug,release}`` relative to the repo, for local
       development with a ``cargo build`` in that package.
    """

    name = _renderer_exe_name()

    env_path = os.environ.get(_RENDERER_ENV_VAR)
    if env_path:
        candidate = Path(env_path)
        if candidate.exists():
            return candidate
        # Honor explicit intent: a set-but-wrong env var should fail loudly rather
        # than silently falling back to PATH or the dev tree.
        msg = f"{_RENDERER_ENV_VAR} points to a missing renderer binary: {candidate}"
        raise FileNotFoundError(msg)

    on_path = shutil.which(name)
    if on_path:
        return Path(on_path)

    scripts_candidate = _scripts_dir_candidate(name)
    if scripts_candidate is not None and scripts_candidate.exists():
        return scripts_candidate

    for candidate in _repo_target_candidates(name):
        if candidate.exists():
            return candidate

    msg = (
        "Rust renderer binary not found. Install it with "
        '`pip install "projector-controller[realtime]"`, build it with '
        "`cargo build` in packages/renderer, "
        f"set {_RENDERER_ENV_VAR}=<path>, or pass renderer_path=..."
    )
    raise FileNotFoundError(msg)


def _renderer_exe_name() -> str:
    return (
        "projector-controller-renderer.exe"
        if sys.platform == "win32"
        else "projector-controller-renderer"
    )


def _scripts_dir_candidate(name: str) -> Path | None:
    """Path to the binary in this interpreter's scripts dir, if resolvable.

    maturin's ``bin`` bindings install the renderer as a wheel script, which lands in
    the environment's scripts directory (``Scripts`` on Windows, ``bin`` elsewhere).
    ``shutil.which`` misses it when that dir is not on PATH, so check it directly.
    """

    scripts = sysconfig.get_path("scripts")
    if not scripts:
        return None
    return Path(scripts) / name


def _repo_target_candidates(name: str) -> list[Path]:
    """Dev-tree fallback locations for a locally built renderer binary."""

    repo_root = Path(__file__).resolve().parents[2]
    renderer_pkg = repo_root / "packages" / "renderer"
    return [
        renderer_pkg / "target" / "debug" / name,
        renderer_pkg / "target" / "release" / name,
    ]


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


def _drain_stream(stream: IO[str], sink: deque[str]) -> None:
    """Continuously copy a renderer pipe into a bounded buffer.

    Without this, a renderer that writes enough to stdout/stderr would fill the OS
    pipe buffer and block on its next write, stalling frame rendering.
    """

    try:
        for line in stream:
            sink.append(line.rstrip("\n"))
    except (OSError, ValueError):
        # Stream was closed while the renderer was shutting down.
        pass
