import pygame as pg

from src.utils import GameSettings, Position
from src.sprites import Sprite, BackgroundSprite
from src.scenes.scene import Scene
from src.interface.components import Button
from src.core.services import scene_manager, sound_manager, input_manager
from src.interface.settings_ui import SettingsUI
from src.utils import Logger
from typing import override

class BattleScene(Scene):
    # Background Image
    background: BackgroundSprite
    # Buttons
    play_button: Button
    setting_button: Button
    
    # Settings Overlay
    settings_ui: SettingsUI
    show_settings: bool
    
    def __init__(self):
        super().__init__()
        self.background = BackgroundSprite("backgrounds/background1.png")
        self.show_settings = False

        px, py = GameSettings.SCREEN_WIDTH // 2, GameSettings.SCREEN_HEIGHT * 3 // 4
        self.play_button = Button(
            "UI/button_play.png", "UI/button_play_hover.png",
            px + 50, py, 100, 100,
            lambda: scene_manager.change_scene("game")
        )
        
        self.setting_button = Button(
            "UI/button_setting.png", "UI/button_setting_hover.png",
            px - 100, py, 100, 100,
            self._toggle_settings
        )
        
        # Initialize Settings UI
        # Centered on screen
        sx, sy = GameSettings.SCREEN_WIDTH // 2, GameSettings.SCREEN_HEIGHT // 2
        
        frame_width, frame_height = 800, 500
        
        self.bg_frame = Sprite(
            "UI/raw/UI_Flat_Frame01a.png",
            (frame_width, frame_height)
        )
        self.bg_frame.update_pos(Position(sx - frame_width // 2, sy - frame_height // 2))

        self.settings_ui = SettingsUI(
            sx - frame_width // 2, sy - frame_height // 2, frame_width, frame_height,
            on_save=lambda: Logger.info("Save not available in menu"),
            on_load=lambda: Logger.info("Load not available in menu"),
            on_exit=self._toggle_settings
        )
        
    def _toggle_settings(self):
        self.show_settings = not self.show_settings

        
    @override
    def enter(self) -> None:
        sound_manager.play_bgm("RBY 101 Opening (Part 1).ogg")
        pass

    @override
    def exit(self) -> None:
        pass

    @override
    def update(self, dt: float) -> None:
        if self.show_settings:
            self.settings_ui.update(dt)
            return

        if input_manager.key_pressed(pg.K_SPACE):
            scene_manager.change_scene("game")
            return
        self.play_button.update(dt)
        self.setting_button.update(dt)
        

    @override
    def draw(self, screen: pg.Surface) -> None:
        self.background.draw(screen)
        self.play_button.draw(screen)
        self.setting_button.draw(screen)
        
        if self.show_settings:
            # Draw a semi-transparent overlay
            overlay = pg.Surface((GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT), pg.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))
            
            self.bg_frame.draw(screen)
            self.settings_ui.draw(screen)

