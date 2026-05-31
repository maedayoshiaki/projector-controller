"""pygame/SDL backend for projector windows."""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any

from projector_controller.config import DisplaySpec, FitMode, ProjectionConfig, Size
from projector_controller.fit import compute_fit_rect

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
# Windows: become per-monitor DPI aware before SDL initializes so pygame reports
# physical pixels (e.g. 2880x1800) instead of scaled logical sizes (1440x900 at
# 200%). Set as a hint so users can override; ignored on non-Windows platforms.
os.environ.setdefault("SDL_WINDOWS_DPI_AWARENESS", "permonitorv2")
import pygame  # noqa: E402


def list_pygame_displays() -> list[DisplaySpec]:
    """Return displays known to pygame."""

    pygame.display.init()
    sizes = pygame.display.get_desktop_sizes()
    return [
        DisplaySpec(index=index, size=Size(width, height))
        for index, (width, height) in enumerate(sizes)
    ]


class PygameProjectionBackend:
    """Concrete backend using pygame display surfaces."""

    def __init__(self, config: ProjectionConfig) -> None:
        self._config = config
        self._surface: Any | None = None
        self._is_open = False

    def open(self) -> None:
        if self._is_open:
            return

        display = self._config.display if self._config.display is not None else 0
        # Only force an absolute position when the user asked for one. With no position,
        # passing ``display=N`` lets SDL center the window on that display (its default),
        # which avoids the previous bug of always pinning windows to (0, 0).
        place_absolute = not self._config.fullscreen and self._config.position is not None
        previous_window_pos = os.environ.get("SDL_VIDEO_WINDOW_POS")
        if place_absolute:
            assert self._config.position is not None
            os.environ["SDL_VIDEO_WINDOW_POS"] = (
                f"{self._config.position.x},{self._config.position.y}"
            )

        try:
            pygame.init()
            pygame.font.init()
            flags = self._window_flags()
            # Fullscreen uses (0, 0) so SDL picks the display's full size (mode
            # switch). DPI awareness ensures that size is the physical resolution.
            size = (0, 0) if self._config.fullscreen else self._config.size.as_tuple()
            self._surface = pygame.display.set_mode(size, flags=flags, display=display)
            pygame.display.set_caption("projector-controller")
            self._surface.fill(self._config.background)
            pygame.display.flip()
            self._is_open = True
        finally:
            if place_absolute:
                if previous_window_pos is None:
                    os.environ.pop("SDL_VIDEO_WINDOW_POS", None)
                else:
                    os.environ["SDL_VIDEO_WINDOW_POS"] = previous_window_pos

    def close(self) -> None:
        if not self._is_open:
            return
        pygame.display.quit()
        pygame.font.quit()
        self._surface = None
        self._is_open = False

    def show_image(self, path: str | Path, *, fit_mode: FitMode | None = None) -> None:
        self._ensure_open()
        image_path = Path(path)
        if not image_path.exists():
            msg = f"image does not exist: {image_path}"
            raise FileNotFoundError(msg)

        image = pygame.image.load(str(image_path)).convert_alpha()
        self._draw_surface(image, fit_mode or self._config.fit_mode)

    def show_test_pattern(self) -> None:
        self._ensure_open()
        assert self._surface is not None
        target = self._target_size()
        pattern = pygame.Surface(target.as_tuple())
        pattern.fill("black")
        self._draw_grid(pattern)
        self._draw_center_lines(pattern)
        self._draw_border(pattern)
        self._draw_label(pattern)
        self._surface.blit(pattern, (0, 0))
        pygame.display.flip()

    def poll_events(self) -> bool:
        self._ensure_open()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return False
        return True

    def wait(self, seconds: float | None = None) -> None:
        self._ensure_open()
        clock = pygame.time.Clock()
        if seconds is None:
            while self.poll_events():
                clock.tick(60)
            return

        if seconds < 0:
            msg = "seconds must be non-negative"
            raise ValueError(msg)

        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline and self.poll_events():
            clock.tick(60)

    def _window_flags(self) -> int:
        flags = 0
        if self._config.fullscreen:
            flags |= pygame.FULLSCREEN
        elif self._config.borderless:
            flags |= pygame.NOFRAME
        return flags

    def _draw_surface(self, source: Any, fit_mode: FitMode) -> None:
        self._ensure_open()
        assert self._surface is not None
        target = self._target_size()
        source_size = Size(source.get_width(), source.get_height())
        rect = compute_fit_rect(source_size, target, fit_mode)
        self._surface.fill(self._config.background)

        if (rect.width, rect.height) == source_size.as_tuple():
            rendered = source
        else:
            rendered = pygame.transform.smoothscale(source, (rect.width, rect.height))

        self._surface.blit(rendered, (rect.x, rect.y))
        pygame.display.flip()

    def _target_size(self) -> Size:
        self._ensure_open()
        assert self._surface is not None
        return Size(self._surface.get_width(), self._surface.get_height())

    def _draw_grid(self, surface: Any) -> None:
        width = surface.get_width()
        height = surface.get_height()
        step = max(40, min(width, height) // 10)
        for x in range(0, width, step):
            pygame.draw.line(surface, (80, 80, 80), (x, 0), (x, height), 1)
        for y in range(0, height, step):
            pygame.draw.line(surface, (80, 80, 80), (0, y), (width, y), 1)

    def _draw_center_lines(self, surface: Any) -> None:
        width = surface.get_width()
        height = surface.get_height()
        pygame.draw.line(surface, (255, 64, 64), (width // 2, 0), (width // 2, height), 2)
        pygame.draw.line(surface, (64, 255, 64), (0, height // 2), (width, height // 2), 2)
        pygame.draw.circle(surface, (64, 128, 255), (width // 2, height // 2), 24, 2)

    def _draw_border(self, surface: Any) -> None:
        width = surface.get_width()
        height = surface.get_height()
        pygame.draw.rect(surface, "white", (0, 0, width, height), 2)

    def _draw_label(self, surface: Any) -> None:
        width = surface.get_width()
        height = surface.get_height()
        font_size = max(16, min(width, height) // 32)
        font = pygame.font.SysFont("consolas", font_size)
        display = self._config.display if self._config.display is not None else 0
        mode = "fullscreen" if self._config.fullscreen else "windowed"
        label = f"display={display} {width}x{height} {mode}"
        text = font.render(label, True, "white", "black")
        surface.blit(text, (16, 16))

    def _ensure_open(self) -> None:
        if not self._is_open or self._surface is None:
            msg = "projection window is not open"
            raise RuntimeError(msg)
