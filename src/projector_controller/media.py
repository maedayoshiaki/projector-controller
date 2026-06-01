"""Dedicated media process: decode a video file with PyAV and feed the Rust renderer.

This is case C of the realtime design: the renderer stays a pure frame sink, and a
separate process owns decoding (and later audio + A/V sync). Run as a subprocess by
``VideoPlayer``:

    python -m projector_controller.media --connect HOST:PORT --file video.mp4

PyAV is an optional dependency (the ``[video]`` extra); it is imported lazily so the rest
of the package stays importable without it.
"""

from __future__ import annotations

import argparse
import socket
import time
from collections.abc import Iterable, Iterator, Sequence
from dataclasses import dataclass
from pathlib import Path

from projector_controller.config import FitMode, normalize_fit_mode
from projector_controller.realtime import _encode_frame_header, _encode_quit_header


@dataclass(frozen=True)
class DecodedFrame:
    """A decoded, tightly-packed RGBA8 frame with its presentation time in seconds."""

    data: bytes
    width: int
    height: int
    pts: float


def decode_video_frames(path: str | Path) -> Iterator[DecodedFrame]:
    """Decode a video file to tightly-packed RGBA8 frames using PyAV.

    Yields frames in presentation order. ``pts`` is seconds from the stream start; frames
    without a timestamp fall back to a running counter at the stream's average rate.
    """

    import av  # lazy: PyAV is the optional [video] extra

    with av.open(str(path)) as container:
        stream = container.streams.video[0]
        rate = stream.average_rate
        fallback_step = 1.0 / float(rate) if rate else 1.0 / 30.0
        for index, frame in enumerate(container.decode(stream)):
            rgba = frame.reformat(format="rgba")
            width = int(rgba.width)
            height = int(rgba.height)
            plane = rgba.planes[0]
            data = _pack_rgba(
                bytes(plane), width=width, height=height, line_size=int(plane.line_size)
            )
            frame_time = frame.time
            pts = float(frame_time) if frame_time is not None else index * fallback_step
            yield DecodedFrame(data=data, width=width, height=height, pts=pts)


def _pack_rgba(raw: bytes, *, width: int, height: int, line_size: int) -> bytes:
    """Strip per-row padding so the frame matches the renderer's tightly-packed protocol.

    PyAV aligns each row to a boundary, so ``line_size`` can exceed ``width * 4``.
    """

    tight = width * 4
    if line_size == tight:
        return raw
    return b"".join(raw[y * line_size : y * line_size + tight] for y in range(height))


def stream_frames(
    sock: socket.socket,
    frames: Iterable[DecodedFrame],
    *,
    fit_mode: FitMode | None = None,
    pace: bool = True,
) -> int:
    """Push decoded frames to a connected renderer, optionally paced by PTS.

    Returns the number of frames sent. With ``pace=True`` (the default) each frame is held
    until its presentation time relative to the first frame, so playback runs at real time.
    """

    start: float | None = None
    sent = 0
    for frame in frames:
        if pace:
            now = time.perf_counter()
            if start is None:
                start = now - frame.pts
            delay = (start + frame.pts) - now
            if delay > 0:
                time.sleep(delay)
        _send_frame(sock, frame, fit_mode)
        sent += 1
    return sent


def _send_frame(sock: socket.socket, frame: DecodedFrame, fit_mode: FitMode | None) -> None:
    header = _encode_frame_header(
        width=frame.width,
        height=frame.height,
        pixel_format="rgba8",
        fit_mode=fit_mode,
        byte_length=len(frame.data),
    )
    sock.sendall(header)
    sock.sendall(frame.data)


def _parse_address(text: str) -> tuple[str, int]:
    host, sep, port = text.rpartition(":")
    if not host or not sep or not port:
        msg = f"invalid --connect address: {text!r} (expected HOST:PORT)"
        raise ValueError(msg)
    return host, int(port)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="projector-controller-media")
    parser.add_argument("--connect", required=True, help="renderer frame socket HOST:PORT")
    parser.add_argument("--file", required=True, type=Path, help="video file to play")
    parser.add_argument(
        "--fit-mode",
        choices=("contain", "cover", "stretch", "native"),
        default=None,
        help="override the renderer's fit mode for this stream",
    )
    parser.add_argument("--connect-timeout", type=float, default=5.0)
    args = parser.parse_args(argv)

    host, port = _parse_address(args.connect)
    fit_mode = normalize_fit_mode(args.fit_mode) if args.fit_mode is not None else None

    sock = socket.create_connection((host, port), timeout=args.connect_timeout)
    sock.settimeout(None)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    try:
        stream_frames(sock, decode_video_frames(args.file), fit_mode=fit_mode)
        # Tell the renderer the stream is finished so it can shut down cleanly.
        sock.sendall(_encode_quit_header())
    finally:
        sock.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
