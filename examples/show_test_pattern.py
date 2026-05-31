"""Show the built-in test pattern on display 0."""

from projector_controller import ProjectionWindow


def main() -> None:
    with ProjectionWindow(display=0, fullscreen=False, size=(1280, 720)) as window:
        window.show_test_pattern()
        window.wait()


if __name__ == "__main__":
    main()
