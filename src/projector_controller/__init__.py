"""Public API for projector-controller."""

from projector_controller.config import (
    DisplaySpec,
    Point,
    ProjectionConfig,
    Size,
    WindowGeometry,
)
from projector_controller.display import list_displays
from projector_controller.realtime import RealtimeProjection
from projector_controller.window import ProjectionWindow

__all__ = [
    "DisplaySpec",
    "Point",
    "ProjectionConfig",
    "RealtimeProjection",
    "ProjectionWindow",
    "Size",
    "WindowGeometry",
    "list_displays",
]
