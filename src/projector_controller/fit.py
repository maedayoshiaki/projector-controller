"""Pure geometry helpers for placing media inside a projection window."""

from __future__ import annotations

from projector_controller.config import FitMode, Size, WindowGeometry


def ensure_size(value: Size | tuple[int, int]) -> Size:
    if isinstance(value, Size):
        return value
    return Size.from_tuple(value)


def compute_fit_rect(
    source_size: Size | tuple[int, int],
    target_size: Size | tuple[int, int],
    fit_mode: FitMode,
) -> WindowGeometry:
    """Return the rectangle where source media should be drawn inside a target area."""

    source = ensure_size(source_size)
    target = ensure_size(target_size)

    if fit_mode == "stretch":
        return WindowGeometry(0, 0, target.width, target.height)

    if fit_mode == "native":
        x = (target.width - source.width) // 2
        y = (target.height - source.height) // 2
        return WindowGeometry(x, y, source.width, source.height)

    if fit_mode == "contain":
        scale = min(target.width / source.width, target.height / source.height)
    elif fit_mode == "cover":
        scale = max(target.width / source.width, target.height / source.height)
    else:
        msg = f"unsupported fit mode: {fit_mode}"
        raise ValueError(msg)

    width = max(1, round(source.width * scale))
    height = max(1, round(source.height * scale))
    x = (target.width - width) // 2
    y = (target.height - height) // 2
    return WindowGeometry(x, y, width, height)
