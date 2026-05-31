"""Packaging-level guarantees for using projector_controller as a library."""

from __future__ import annotations

import subprocess
import sys

import projector_controller


def test_public_api_is_exported() -> None:
    # The names other Python code is expected to import must stay available.
    for name in (
        "ProjectionWindow",
        "RealtimeProjection",
        "RendererMonitor",
        "list_displays",
        "list_renderer_monitors",
        "ProjectionConfig",
        "Point",
        "Size",
    ):
        assert name in projector_controller.__all__
        assert hasattr(projector_controller, name)


def test_import_does_not_load_pygame() -> None:
    # Importing the package must stay lightweight: pygame is a GUI backend pulled in
    # lazily, so realtime-only consumers don't pay for it. Run in a fresh interpreter
    # so other tests can't pollute sys.modules.
    code = (
        "import sys, projector_controller\n"
        "assert 'pygame' not in sys.modules, 'pygame imported eagerly'\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
