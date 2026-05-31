"""Command-line helpers for manual projection checks."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from projector_controller import ProjectionWindow, list_displays
from projector_controller.config import Point, Size


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
    parser.add_argument(
        "--x",
        type=int,
        default=None,
        help="window x in absolute desktop coordinates (omit to center on --display)",
    )
    parser.add_argument(
        "--y",
        type=int,
        default=None,
        help="window y in absolute desktop coordinates (omit to center on --display)",
    )
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


def placement_from_args(args: argparse.Namespace) -> tuple[Point | None, Size]:
    """Resolve --x/--y/--width/--height into (position, size).

    Omitting both --x and --y yields position=None, i.e. center on the target display.
    """

    size = Size(args.width, args.height)
    if args.x is None and args.y is None:
        return None, size
    return Point(args.x or 0, args.y or 0), size


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.list_displays:
        for display in list_displays():
            name = f" {display.name}" if display.name else ""
            print(f"{display.index}: {display.size.width}x{display.size.height}{name}")
        return 0

    position, size = placement_from_args(args)
    with ProjectionWindow(
        display=args.display,
        fullscreen=args.fullscreen,
        position=position,
        size=size,
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
