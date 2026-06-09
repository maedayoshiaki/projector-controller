import pytest

from projector_controller.adapters.pygame_backend import PygameProjectionBackend
from projector_controller.config import (
    PIXEL_FORMAT_BYTES,
    ProjectionConfig,
    Size,
    normalize_pixel_format,
)


def test_pixel_format_bytes_per_pixel() -> None:
    assert PIXEL_FORMAT_BYTES == {"RGB": 3, "RGBA": 4}


def test_normalize_pixel_format_narrows_valid_value() -> None:
    assert normalize_pixel_format("RGBA") == "RGBA"


def test_normalize_pixel_format_rejects_unknown() -> None:
    with pytest.raises(ValueError, match="pixel format"):
        normalize_pixel_format("BGR")


def _backend() -> PygameProjectionBackend:
    # The buffer is validated before the window is touched, so these checks need no
    # display: a closed backend still rejects malformed input.
    return PygameProjectionBackend(ProjectionConfig())


def test_show_frame_rejects_rgb_length_mismatch() -> None:
    backend = _backend()
    # 2x2 RGB needs 12 bytes; give 10.
    with pytest.raises(ValueError, match="got 10, expected 12"):
        backend.show_frame(bytes(10), (2, 2), pixel_format="RGB")


def test_show_frame_rejects_rgba_length_mismatch() -> None:
    backend = _backend()
    # 2x2 RGBA needs 16 bytes; give 12.
    with pytest.raises(ValueError, match="got 12, expected 16"):
        backend.show_frame(bytes(12), Size(2, 2), pixel_format="RGBA")


def test_show_frame_rejects_unknown_pixel_format() -> None:
    backend = _backend()
    with pytest.raises(ValueError, match="pixel format"):
        backend.show_frame(bytes(12), (2, 2), pixel_format="BGR")  # type: ignore[arg-type]
