"""Show an image file in a projection window."""

from pathlib import Path

from projector_controller import ProjectionWindow


def main() -> None:
    image_path = Path("media/test-pattern.png")
    with ProjectionWindow(display=0, fullscreen=False, size=(1280, 720)) as window:
        window.show_image(image_path)
        window.wait()


if __name__ == "__main__":
    main()
