"""Build a raw RGB byte buffer and show it via the pygame backend."""

from projector_controller import ProjectionWindow


def make_rgb_gradient(width: int, height: int) -> bytes:
    data = bytearray(width * height * 3)
    offset = 0
    for y in range(height):
        green = (y * 255) // max(1, height - 1)
        for x in range(width):
            data[offset] = (x * 255) // max(1, width - 1)  # R: left->right
            data[offset + 1] = green  # G: top->bottom
            data[offset + 2] = 128  # B: constant
            offset += 3
    return bytes(data)


def main() -> None:
    width, height = 640, 360
    frame = make_rgb_gradient(width, height)

    with ProjectionWindow(display=0, fullscreen=False, size=(1280, 720)) as window:
        window.show_frame(frame, (width, height), pixel_format="RGB")
        window.wait()


if __name__ == "__main__":
    main()
