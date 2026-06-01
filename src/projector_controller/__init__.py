"""Public API for projector-controller."""

from projector_controller.config import (
    DisplaySpec,
    Point,
    ProjectionConfig,
    Size,
    WindowGeometry,
)
from projector_controller.display import list_displays
from projector_controller.realtime import (
    RealtimeProjection,
    RendererMonitor,
    list_renderer_monitors,
)
from projector_controller.video import VideoPlayer
from projector_controller.window import ProjectionWindow

__all__ = [
    "DisplaySpec",
    "Point",
    "ProjectionConfig",
    "ProjectionWindow",
    "RealtimeProjection",
    "RendererMonitor",
    "Size",
    "VideoPlayer",
    "WindowGeometry",
    "list_displays",
    "list_renderer_monitors",
]
