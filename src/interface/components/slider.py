from __future__ import annotations

import math
import pygame as pg
from typing import Callable, override

from src.core.services import input_manager
from src.sprites import Sprite
from .component import UIComponent


class Slider(UIComponent):
    """
    horizontal slider that reports a value in the range [0, 1].
    can be dragged or clicked to change value
    """

    def __init__(
        self,
        track_img: str,
        knob_img: str,
        x: int,
        y: int,
        width: int,
        height: int,
        knob_size: tuple[int, int] | None = None,
        initial_value: float = 0.0,
        on_change: Callable[[float], None] | None = None,
    ) -> None:
        knob_size = knob_size or (height, height)

        self.track_sprite = Sprite(track_img, (width, height))
        self.knob_sprite = Sprite(knob_img, knob_size)
        self.track_sprite.rect.topleft = (x, y)

        track_rect = self.track_sprite.rect
        knob_rect = self.knob_sprite.rect
        knob_rect.y = track_rect.y + (track_rect.height - knob_rect.height) // 2

        self._min_x = track_rect.x
        self._max_x = track_rect.right - knob_rect.width
        self._dragging = False
        self._grab_offset = 0

        self._value = 0.0
        self.on_change = on_change
        self._set_value(initial_value, notify=False)

    @property
    def value(self) -> float:
        return self._value

    @value.setter
    def value(self, new_value: float) -> None:
        self._set_value(new_value, notify=False)

    def _set_value(self, new_value: float, *, notify: bool) -> None:
        clamped_value = max(0.0, min(1.0, new_value))
        target_left = self._min_x
        if self._max_x > self._min_x:
            target_left += int((self._max_x - self._min_x) * clamped_value)

        changed = not math.isclose(clamped_value, self._value, abs_tol=1e-4)
        self._value = clamped_value
        self.knob_sprite.rect.x = target_left

        if changed and notify and self.on_change is not None:
            self.on_change(self._value)

    def _update_from_mouse(self, desired_left: int) -> None:
        # ensure the new position.x is within bounds
        new_left = max(self._min_x, min(self._max_x, desired_left))
        span = max(1, self._max_x - self._min_x)
        normalized = (new_left - self._min_x) / span
        self._set_value(normalized, notify=True)

    @override
    def update(self, dt: float) -> None:
        mouse_pos = input_manager.mouse_pos
        mouse_x = mouse_pos[0]

        knob_rect = self.knob_sprite.rect
        track_rect = self.track_sprite.rect
        hovered_knob = knob_rect.collidepoint(mouse_pos)
        hovered_track = track_rect.collidepoint(mouse_pos)

        if input_manager.mouse_pressed(1):
            if hovered_knob:
                self._dragging = True
                self._grab_offset = mouse_x - knob_rect.x
            elif hovered_track:
                self._dragging = True
                self._grab_offset = knob_rect.width // 2
                self._update_from_mouse(mouse_x - self._grab_offset)

        if self._dragging and input_manager.mouse_down(1):
            self._update_from_mouse(mouse_x - self._grab_offset)
        elif self._dragging and input_manager.mouse_released(1):
            self._dragging = False

    @override
    def draw(self, screen: pg.Surface) -> None:
        # draw indicator bar
        if self.value > 0:
            fill_rect = self.track_sprite.rect.copy()
            fill_rect.width = self.knob_sprite.rect.centerx - self.track_sprite.rect.left
            pg.draw.rect(screen, (0, 200, 0), fill_rect)

        # draw track frame
        screen.blit(self.track_sprite.image, self.track_sprite.rect)
        
        # draw knob
        screen.blit(self.knob_sprite.image, self.knob_sprite.rect)
