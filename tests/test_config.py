import pytest

from projector_controller.config import (
    Point,
    ProjectionConfig,
    Size,
    WindowGeometry,
    normalize_fit_mode,
)
from projector_controller.window import ProjectionWindow


def test_size_requires_positive_dimensions() -> None:
    with pytest.raises(ValueError, match="positive"):
        Size(0, 100)


def test_projection_config_rejects_negative_display() -> None:
    with pytest.raises(ValueError, match="display"):
        ProjectionConfig(display=-1)


def test_projection_config_rejects_unknown_fit_mode() -> None:
    with pytest.raises(ValueError, match="fit mode"):
        ProjectionConfig(fit_mode="tile")  # type: ignore[arg-type]


def test_normalize_fit_mode_narrows_valid_value() -> None:
    assert normalize_fit_mode("contain") == "contain"


def test_projection_window_uses_explicit_position_and_size() -> None:
    window = ProjectionWindow(position=(10, 20), size=(300, 200))
    assert window.config.position == Point(10, 20)
    assert window.config.size == Size(300, 200)


def test_projection_window_defaults_to_centered_position() -> None:
    # No position given -> None means "center on the target display".
    window = ProjectionWindow(display=1)
    assert window.config.position is None
    assert window.config.size == Size(1280, 720)


def test_projection_window_geometry_sets_explicit_position() -> None:
    # The legacy geometry argument is treated as an explicit (non-centered) position.
    window = ProjectionWindow(geometry=WindowGeometry(5, 6, 300, 200))
    assert window.config.position == Point(5, 6)
    assert window.config.size == Size(300, 200)
