from projector_controller.cli import build_parser


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
