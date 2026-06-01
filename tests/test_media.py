import socket
import struct
from pathlib import Path

import pytest

from projector_controller import VideoPlayer, media


def test_parse_address_splits_host_and_port() -> None:
    assert media._parse_address("127.0.0.1:54321") == ("127.0.0.1", 54321)


@pytest.mark.parametrize("text", ["", "127.0.0.1", ":5000", "host:"])
def test_parse_address_rejects_malformed(text: str) -> None:
    with pytest.raises(ValueError, match="--connect"):
        media._parse_address(text)


def test_pack_rgba_returns_input_when_tightly_packed() -> None:
    raw = bytes(range(8))  # 2 px * 1 row * 4 bytes
    assert media._pack_rgba(raw, width=2, height=1, line_size=8) == raw


def test_pack_rgba_strips_row_padding() -> None:
    # 1px-wide rows (4 bytes each) padded to a line_size of 8.
    raw = bytes([1, 2, 3, 4, 0, 0, 0, 0, 5, 6, 7, 8, 0, 0, 0, 0])
    packed = media._pack_rgba(raw, width=1, height=2, line_size=8)
    assert packed == bytes([1, 2, 3, 4, 5, 6, 7, 8])


def _recv_until_eof(sock: socket.socket) -> bytes:
    chunks = []
    while True:
        chunk = sock.recv(65536)
        if not chunk:
            break
        chunks.append(chunk)
    return b"".join(chunks)


def test_stream_frames_pushes_protocol_header_and_payload() -> None:
    sender, receiver = socket.socketpair()
    try:
        frames = [
            media.DecodedFrame(data=b"\x01\x02\x03\x04", width=1, height=1, pts=0.0),
            media.DecodedFrame(data=b"\xaa\xbb\xcc\xdd" * 2, width=2, height=1, pts=0.1),
        ]
        sent = media.stream_frames(sender, frames, fit_mode="cover", pace=False)
        assert sent == 2
        sender.shutdown(socket.SHUT_WR)
        received = _recv_until_eof(receiver)
    finally:
        sender.close()
        receiver.close()

    # First frame: 20-byte header (magic, w, h, pixel_format, fit_mode, reserved, len).
    magic, width, height, pixel_format, fit_mode, reserved, byte_len = struct.unpack(
        "<4sIIBBHI", received[:20]
    )
    assert magic == b"PCF1"
    # rgba8 == 1, cover == 2 (see realtime._PIXEL_FORMATS / _FIT_MODES).
    assert (width, height, pixel_format, fit_mode, reserved, byte_len) == (1, 1, 1, 2, 0, 4)
    assert received[20:24] == b"\x01\x02\x03\x04"
    # Header + payload for both frames: (20 + 4) + (20 + 8).
    assert len(received) == 24 + 28


def test_stream_frames_synced_presents_when_clock_reaches_pts() -> None:
    sender, receiver = socket.socketpair()
    try:
        frames = [
            media.DecodedFrame(data=b"\x00\x00\x00\x00", width=1, height=1, pts=0.0),
            media.DecodedFrame(data=b"\x00\x00\x00\x00", width=1, height=1, pts=5.0),
        ]
        # Master clock already far ahead of every PTS -> no real waiting.
        sent = media.stream_frames_synced(
            sender, frames, clock=lambda: 1_000.0, is_done=lambda: False
        )
        assert sent == 2
        sender.shutdown(socket.SHUT_WR)
        received = _recv_until_eof(receiver)
    finally:
        sender.close()
        receiver.close()
    assert len(received) == 2 * (20 + 4)


def test_stream_frames_synced_sends_remaining_when_audio_done() -> None:
    sender, receiver = socket.socketpair()
    try:
        # PTS far in the future and clock stuck at 0: only is_done() avoids hanging.
        frames = [media.DecodedFrame(data=b"\x00\x00\x00\x00", width=1, height=1, pts=1e9)]
        sent = media.stream_frames_synced(sender, frames, clock=lambda: 0.0, is_done=lambda: True)
        assert sent == 1
    finally:
        sender.close()
        receiver.close()


def test_video_player_play_requires_open() -> None:
    player = VideoPlayer(renderer_path=Path("renderer-bin"))
    with pytest.raises(RuntimeError, match="not open"):
        player.play("clip.mp4")


def test_audio_master_start_false_without_audio_stream(tmp_path: Path) -> None:
    av = pytest.importorskip("av")

    path = tmp_path / "silent.mp4"
    with av.open(str(path), mode="w") as container:
        stream = container.add_stream("mpeg4", rate=10)
        stream.width, stream.height, stream.pix_fmt = 32, 32, "yuv420p"
        for _ in range(3):
            frame = av.VideoFrame(32, 32, "rgb24").reformat(format="yuv420p")
            for packet in stream.encode(frame):
                container.mux(packet)
        for packet in stream.encode():
            container.mux(packet)

    master = media.AudioMaster(path)
    # No audio stream -> caller falls back to wall-clock pacing.
    assert master.start() is False
    assert master.is_done() is False


def test_decode_video_frames_roundtrip(tmp_path: Path) -> None:
    av = pytest.importorskip("av")

    path = tmp_path / "clip.mp4"
    width, height, count = 64, 48, 5
    with av.open(str(path), mode="w") as container:
        stream = container.add_stream("mpeg4", rate=10)
        stream.width = width
        stream.height = height
        stream.pix_fmt = "yuv420p"
        for _ in range(count):
            frame = av.VideoFrame(width, height, "rgb24").reformat(format="yuv420p")
            for packet in stream.encode(frame):
                container.mux(packet)
        for packet in stream.encode():  # flush the encoder
            container.mux(packet)

    frames = list(media.decode_video_frames(path))

    assert frames, "expected at least one decoded frame"
    for frame in frames:
        assert (frame.width, frame.height) == (width, height)
        assert len(frame.data) == width * height * 4
    # Presentation times are non-decreasing.
    assert all(b.pts >= a.pts for a, b in zip(frames, frames[1:], strict=False))
