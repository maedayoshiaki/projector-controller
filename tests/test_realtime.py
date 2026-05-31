import struct
from collections import deque
from io import StringIO
from pathlib import Path

import pytest

from projector_controller.config import Point, Size
from projector_controller.realtime import (
    RealtimeProjection,
    _drain_stream,
    _encode_frame_header,
    _parse_monitor_lines,
)


def test_realtime_renderer_command_uses_window_options() -> None:
    projection = RealtimeProjection(
        display=1,
        fullscreen=True,
        position=Point(10, 20),
        size=Size(640, 480),
        fit_mode="cover",
        renderer_path=Path("renderer-bin"),
    )

    assert projection._renderer_command() == [
        "renderer-bin",
        "--bind",
        "127.0.0.1:0",
        "--display",
        "1",
        "--width",
        "640",
        "--height",
        "480",
        "--fit-mode",
        "cover",
        "--fullscreen",
        "--x",
        "10",
        "--y",
        "20",
    ]


def test_realtime_frame_header_encodes_protocol_fields() -> None:
    header = _encode_frame_header(
        width=2,
        height=3,
        pixel_format="rgba8",
        fit_mode="contain",
        byte_length=24,
    )

    assert struct.unpack("<4sIIBBHI", header) == (b"PCF1", 2, 3, 1, 1, 0, 24)


def test_realtime_projection_rejects_bad_frame_size_before_open() -> None:
    projection = RealtimeProjection(renderer_path=Path("renderer-bin"))

    with pytest.raises(ValueError, match="byte length"):
        projection.submit_frame(b"\x00" * 15, width=2, height=2)


def test_drain_stream_keeps_last_lines_within_bound() -> None:
    sink: deque[str] = deque(maxlen=2)

    _drain_stream(StringIO("first\nsecond\nthird\n"), sink)

    # Lines are stripped of newlines and the bounded buffer keeps only the latest.
    assert list(sink) == ["second", "third"]


def test_parse_monitor_lines_parses_fields_and_skips_noise() -> None:
    text = (
        "MONITOR\t0\t0\t0\t2880\t1800\t2.0\tBuilt-in Display\n"
        "junk line\n"
        "MONITOR\t1\t2880\t0\t1920\t1080\t1\t\n"
    )

    monitors = _parse_monitor_lines(text)

    assert [m.index for m in monitors] == [0, 1]
    # Names with spaces survive; the second monitor has an empty name.
    assert monitors[0].name == "Built-in Display"
    assert monitors[1].name == ""
    # Origin and scale are parsed; index 1 sits to the right of index 0.
    assert (monitors[1].x, monitors[1].y) == (2880, 0)
    assert monitors[0].scale == 2.0
    assert monitors[1].scale == 1.0
