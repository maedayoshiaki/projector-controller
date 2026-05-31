"""Display discovery helpers."""

from __future__ import annotations

from projector_controller.config import DisplaySpec


def list_displays(*, backend: str = "pygame") -> list[DisplaySpec]:
    """List displays using the selected backend."""

    if backend != "pygame":
        msg = f"unsupported backend: {backend}"
        raise ValueError(msg)

    from projector_controller.adapters.pygame_backend import list_pygame_displays

    return list_pygame_displays()
