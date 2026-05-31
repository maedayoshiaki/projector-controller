import pytest

from projector_controller.config import (
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


def test_projection_window_builds_geometry_from_position_and_size() -> None:
    window = ProjectionWindow(position=(10, 20), size=(300, 200))
    assert window.config.geometry == WindowGeometry(10, 20, 300, 200)
