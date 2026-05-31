"""Command-line helpers for manual projection checks."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from projector_controller import ProjectionWindow, list_displays
from projector_controller.config import WindowGeometry


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="projector-controller")
    parser.add_argument(
        "--list-displays", action="store_true", help="print known displays and exit"
    )
    parser.add_argument("--image", type=Path, help="image file to project")
    parser.add_argument("--display", type=int, default=0, help="target display index")
    parser.add_argument(
        "--fullscreen", action="store_true", help="open fullscreen on the target display"
    )
    parser.add_argument("--borderless", action="store_true", help="open a borderless window")
    parser.add_argument("--x", type=int, default=0, help="window x position in desktop coordinates")
    parser.add_argument("--y", type=int, default=0, help="window y position in desktop coordinates")
    parser.add_argument("--width", type=int, default=1280, help="window width")
    parser.add_argument("--height", type=int, default=720, help="window height")
    parser.add_argument(
        "--fit-mode",
        choices=("contain", "cover", "stretch", "native"),
        default="contain",
        help="how media should fit inside the projection window",
    )
    parser.add_argument("--duration", type=float, help="seconds to keep the window open")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.list_displays:
        for display in list_displays():
            name = f" {display.name}" if display.name else ""
            print(f"{display.index}: {display.size.width}x{display.size.height}{name}")
        return 0

    geometry = WindowGeometry(args.x, args.y, args.width, args.height)
    with ProjectionWindow(
        display=args.display,
        fullscreen=args.fullscreen,
        geometry=geometry,
        fit_mode=args.fit_mode,
        borderless=args.borderless,
    ) as window:
        if args.image is None:
            window.show_test_pattern()
        else:
            window.show_image(args.image, fit_mode=args.fit_mode)
        window.wait(args.duration)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
