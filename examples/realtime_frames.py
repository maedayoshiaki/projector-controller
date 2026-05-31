"""Send generated RGBA frames to the Rust GPU renderer."""

from __future__ import annotations

import time

from projector_controller import RealtimeProjection


def make_frame(width: int, height: int, frame_index: int) -> bytearray:
    data = bytearray(width * height * 4)
    offset = 0
    shift = frame_index * 3
    for y in range(height):
        gy = (y * 255) // max(1, height - 1)
        for x in range(width):
            rx = (x * 255) // max(1, width - 1)
            data[offset] = (rx + shift) % 256
            data[offset + 1] = (gy + shift // 2) % 256
            data[offset + 2] = (x + y + shift) % 256
            data[offset + 3] = 255
            offset += 4
    return data


def main() -> None:
    width = 640
    height = 360
    fps = 60
    frame_duration = 1.0 / fps

    with RealtimeProjection(display=0, fullscreen=False, size=(1280, 720)) as projection:
        next_frame = time.perf_counter()
        for frame_index in range(fps * 10):
            projection.submit_frame(
                make_frame(width, height, frame_index),
                width=width,
                height=height,
                pixel_format="rgba8",
            )
            next_frame += frame_duration
            time.sleep(max(0.0, next_frame - time.perf_counter()))


if __name__ == "__main__":
    main()
