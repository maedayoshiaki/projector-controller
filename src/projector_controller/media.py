"""Dedicated media process: decode a video file with PyAV and feed the Rust renderer.

This is case C of the realtime design: the renderer stays a pure frame sink, and a
separate process owns decoding and audio + A/V sync. Run as a subprocess by
``VideoPlayer``:

    python -m projector_controller.media --connect HOST:PORT --file video.mp4

Audio is the master clock: it plays continuously in a background thread (via
``sounddevice``) and video frames are presented to match the audio position. If the file
has no audio track, no output device is available, or ``--mute`` is given, playback falls
back to wall-clock pacing.

PyAV and sounddevice are optional dependencies (the ``[video]`` extra); they are imported
lazily so the rest of the package stays importable without them.
"""

from __future__ import annotations

import argparse
import socket
import threading
import time
from collections.abc import Callable, Iterable, Iterator, Sequence
from dataclasses import dataclass
from pathlib import Path

from projector_controller.config import FitMode, normalize_fit_mode
from projector_controller.realtime import _encode_frame_header, _encode_quit_header

# Audio is decoded/resampled to interleaved signed 16-bit stereo for output.
_AUDIO_CHANNELS = 2
_AUDIO_BYTES_PER_SAMPLE = 2


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


def _has_audio_stream(path: str | Path) -> bool:
    import av

    try:
        with av.open(str(path)) as container:
            return len(container.streams.audio) > 0
    except Exception:
        return False


class AudioMaster:
    """Play a file's audio in a background thread and expose a playback clock (seconds).

    Audio is the A/V sync master: video frames are presented to match ``clock()``. When the
    file has no audio stream or no output device is available, ``start()`` returns ``False``
    and the caller should fall back to wall-clock pacing.
    """

    def __init__(self, path: str | Path) -> None:
        self._path = str(path)
        self._lock = threading.Lock()
        self._written = 0.0  # seconds of audio handed to the device
        self._latency = 0.0  # device output latency, so clock() ~ played position
        self._finished = False
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def clock(self) -> float:
        with self._lock:
            return max(0.0, self._written - self._latency)

    def is_done(self) -> bool:
        with self._lock:
            return self._finished

    def start(self) -> bool:
        if not _has_audio_stream(self._path):
            return False
        try:
            import sounddevice

            sounddevice.query_devices(kind="output")
        except Exception:
            return False
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        return True

    def stop(self) -> None:
        self._stop.set()
        thread = self._thread
        if thread is not None:
            thread.join(timeout=2)

    def _run(self) -> None:
        import av
        import sounddevice as sd

        try:
            with av.open(self._path) as container:
                stream = container.streams.audio[0]
                rate = int(stream.rate)
                resampler = av.AudioResampler(format="s16", layout="stereo", rate=rate)
                with sd.RawOutputStream(
                    samplerate=rate, channels=_AUDIO_CHANNELS, dtype="int16"
                ) as out:
                    with self._lock:
                        self._latency = float(out.latency)
                    for frame in container.decode(stream):
                        if self._stop.is_set():
                            break
                        for resampled in resampler.resample(frame):
                            samples = int(resampled.samples)
                            tight = samples * _AUDIO_CHANNELS * _AUDIO_BYTES_PER_SAMPLE
                            out.write(bytes(resampled.planes[0])[:tight])
                            with self._lock:
                                self._written += samples / rate
        except Exception:
            # No usable audio path; the video side falls back to its own pacing.
            pass
        finally:
            with self._lock:
                self._finished = True


def _run_stream(
    sock: socket.socket,
    frames: Iterable[DecodedFrame],
    fit_mode: FitMode | None,
    wait: Callable[[DecodedFrame], None],
) -> int:
    sent = 0
    for frame in frames:
        wait(frame)
        _send_frame(sock, frame, fit_mode)
        sent += 1
    return sent


def stream_frames(
    sock: socket.socket,
    frames: Iterable[DecodedFrame],
    *,
    fit_mode: FitMode | None = None,
    pace: bool = True,
) -> int:
    """Push frames to the renderer, paced by PTS against a wall clock (no audio)."""

    if not pace:
        return _run_stream(sock, frames, fit_mode, lambda _frame: None)

    anchor: float | None = None

    def wait(frame: DecodedFrame) -> None:
        nonlocal anchor
        now = time.perf_counter()
        if anchor is None:
            anchor = now - frame.pts
        delay = (anchor + frame.pts) - now
        if delay > 0:
            time.sleep(delay)

    return _run_stream(sock, frames, fit_mode, wait)


def stream_frames_synced(
    sock: socket.socket,
    frames: Iterable[DecodedFrame],
    clock: Callable[[], float],
    is_done: Callable[[], bool],
    *,
    fit_mode: FitMode | None = None,
    offset: float = 0.0,
) -> int:
    """Push frames paced to a master ``clock`` (seconds), e.g. the audio playback position.

    ``offset`` presents each frame ``offset`` seconds early to compensate for renderer
    latency. If ``is_done()`` becomes true (audio ended) any remaining frames are sent at
    once instead of waiting forever.
    """

    def wait(frame: DecodedFrame) -> None:
        target = frame.pts - offset
        while True:
            remaining = target - clock()
            if remaining <= 0 or is_done():
                return
            time.sleep(min(0.005, remaining))

    return _run_stream(sock, frames, fit_mode, wait)


def play(
    sock: socket.socket,
    path: str | Path,
    *,
    fit_mode: FitMode | None = None,
    mute: bool = False,
    av_offset: float = 0.0,
) -> None:
    """Decode ``path`` and stream it to the renderer, syncing video to audio when possible."""

    audio = None if mute else AudioMaster(path)
    use_audio = audio.start() if audio is not None else False
    try:
        frames = decode_video_frames(path)
        if use_audio and audio is not None:
            stream_frames_synced(
                sock, frames, audio.clock, audio.is_done, fit_mode=fit_mode, offset=av_offset
            )
        else:
            stream_frames(sock, frames, fit_mode=fit_mode)
    finally:
        if audio is not None:
            audio.stop()


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
    parser.add_argument("--mute", action="store_true", help="do not play the audio track")
    parser.add_argument(
        "--av-offset-ms",
        type=float,
        default=0.0,
        help="present video this many ms early to compensate for renderer latency",
    )
    parser.add_argument("--connect-timeout", type=float, default=5.0)
    args = parser.parse_args(argv)

    host, port = _parse_address(args.connect)
    fit_mode = normalize_fit_mode(args.fit_mode) if args.fit_mode is not None else None

    sock = socket.create_connection((host, port), timeout=args.connect_timeout)
    sock.settimeout(None)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    try:
        play(
            sock,
            args.file,
            fit_mode=fit_mode,
            mute=args.mute,
            av_offset=args.av_offset_ms / 1000.0,
        )
        # Tell the renderer the stream is finished so it can shut down cleanly.
        sock.sendall(_encode_quit_header())
    finally:
        sock.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
