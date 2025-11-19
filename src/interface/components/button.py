from __future__ import annotations
import pygame as pg

from src.sprites import Sprite
from src.core.services import input_manager
from src.utils import Logger
from typing import Callable, override
from .component import UIComponent

class Button(UIComponent):
    img_button: Sprite
    img_button_default: Sprite
    img_button_hover: Sprite
    hitbox: pg.Rect
    on_click: Callable[[], None] | None

    def __init__(
        self,
        img_path: str, img_hovered_path:str,
        x: int, y: int, width: int, height: int,
        on_click: Callable[[], None] | None = None
    ):
        self.img_button_default = Sprite(img_path, (width, height))
        self.hitbox = pg.Rect(x, y, width, height)
        
        self.img_button_hover = Sprite(img_hovered_path, (width, height))
        self.img_button = Sprite(img_path, (width, height))
        self.on_click = on_click

    @override
    def update(self, dt: float) -> None:
        if self.hitbox.collidepoint(input_manager.mouse_pos):
            self.img_button = self.img_button_hover
            if input_manager.mouse_pressed(1) and self.on_click is not None:
                self.on_click()
        else:
            self.img_button = self.img_button_default
    
    @override
    def draw(self, screen: pg.Surface) -> None:
        _ = screen.blit(self.img_button.image, self.hitbox)

class ToggleButton(Button):
    # optional on-hover sprite change is supported
    def __init__(
        self,
        img_off: str, img_on: str,
        x: int, y: int,
        width: int, height: int,
        img_off_hover: str | None = None,
        img_on_hover: str | None = None,
        initial: bool = False,
        on_toggle: Callable[[bool], None] | None = None,
    ):
        off_hover = img_off_hover or img_off
        super().__init__(img_off, off_hover, x, y, width, height, on_click=None)

        self.img_off_default = self.img_button_default
        self.img_off_hover = self.img_button_hover

        on_hover = img_on_hover or img_on
        self.img_on_default = Sprite(img_on, (width, height))
        self.img_on_hover = Sprite(on_hover, (width, height))

        self.is_on = initial
        self.on_toggle = on_toggle
        self._apply_state()
        self.img_button = self.img_button_default

    def _apply_state(self) -> None:
        if self.is_on:
            self.img_button_default = self.img_on_default
            self.img_button_hover = self.img_on_hover
        else:
            self.img_button_default = self.img_off_default
            self.img_button_hover = self.img_off_hover

    @override
    def update(self, dt: float) -> None:
        hovered = self.hitbox.collidepoint(input_manager.mouse_pos)
        if hovered and input_manager.mouse_pressed(1):
            self.is_on = not self.is_on
            if self.on_toggle is not None:
                self.on_toggle(self.is_on)
        self._apply_state()
        super().update(dt)



def main():
    import sys
    import os
    
    pg.init()

    WIDTH, HEIGHT = 800, 800
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("Button Test")
    clock = pg.time.Clock()
    
    bg_color = (0, 0, 0)
    def on_button_click():
        nonlocal bg_color
        if bg_color == (0, 0, 0):
            bg_color = (255, 255, 255)
        else:
            bg_color = (0, 0, 0)
        
    button = Button(
        img_path="UI/button_play.png",
        img_hovered_path="UI/button_play_hover.png",
        x=WIDTH // 2 - 50,
        y=HEIGHT // 2 - 50,
        width=100,
        height=100,
        on_click=on_button_click
    )
    
    running = True
    dt = 0
    
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            input_manager.handle_events(event)
        
        dt = clock.tick(60) / 1000.0
        button.update(dt)
        
        input_manager.reset()
        
        _ = screen.fill(bg_color)
        
        button.draw(screen)
        
        pg.display.flip()
    
    pg.quit()


if __name__ == "__main__":
    main()
