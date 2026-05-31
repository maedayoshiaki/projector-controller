from projector_controller.cli import build_parser, placement_from_args
from projector_controller.config import Point, Size


def test_cli_parses_projection_window_options() -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "--display",
            "1",
            "--fullscreen",
            "--width",
            "1920",
            "--height",
            "1080",
            "--fit-mode",
            "cover",
        ]
    )

    assert args.display == 1
    assert args.fullscreen is True
    assert args.width == 1920
    assert args.height == 1080
    assert args.fit_mode == "cover"


def test_placement_without_xy_centers_on_display() -> None:
    parser = build_parser()
    args = parser.parse_args(["--display", "1"])
    position, size = placement_from_args(args)
    assert position is None
    assert size == Size(1280, 720)


def test_placement_with_xy_uses_absolute_coordinates() -> None:
    parser = build_parser()
    args = parser.parse_args(["--x", "1500", "--y", "100", "--width", "800", "--height", "600"])
    position, size = placement_from_args(args)
    assert position == Point(1500, 100)
    assert size == Size(800, 600)
