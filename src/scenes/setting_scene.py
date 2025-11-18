'''
[TODO HACKATHON 5]
Try to mimic the menu_scene.py or game_scene.py to create this new scene
'''
import pygame as pg

from src.utils import GameSettings
from src.sprites import BackgroundSprite, Sprite
from src.scenes.scene import Scene
from src.interface.components import Button
from src.core.services import scene_manager, sound_manager, input_manager
from typing import override
from src.utils import Position

class SettingScene(Scene):
    # Background Image
    background: BackgroundSprite
    # Buttons
    back_button: Button
    fake_bg: Button
    bg_frame: Sprite
    
    def __init__(self):
        super().__init__()
        self.background = BackgroundSprite("backgrounds/background1.png")

        px, py = GameSettings.SCREEN_WIDTH // 2, GameSettings.SCREEN_HEIGHT // 2
        self.back_button = Button(
            "UI/button_back.png", "UI/button_back_hover.png",
            px - 400, py + 150, 100, 100,
            lambda: scene_manager.change_scene("menu")
        )
        
        self.fake_bg = Button(
            "placeholder/placeholder.jpg", "placeholder/placeholder.jpg",
            GameSettings.SCREEN_WIDTH // 2 - 400, py - 225, 800, 450,
            lambda: scene_manager.change_scene("setting")
        )
        
        self.bg_frame = Sprite(
            "UI/raw/UI_Flat_Frame01a.png",
            (900, 600)
        )
        self.bg_frame.update_pos(Position(GameSettings.SCREEN_WIDTH // 2 - 450, py - 300))
        
    @override
    def enter(self) -> None:
        sound_manager.play_bgm("RBY 101 Opening (Part 1).ogg")
        pass

    @override
    def exit(self) -> None:
        pass

    @override
    def update(self, dt: float) -> None:
        # self.fake_bg.update(dt)
        self.back_button.update(dt)
        

    @override
    def draw(self, screen: pg.Surface) -> None:
        self.background.draw(screen)
        # self.fake_bg.draw(screen)
        self.bg_frame.draw(screen)
        self.back_button.draw(screen)
