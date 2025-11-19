import pygame as pg
import threading
import time

from src.scenes.scene import Scene
from src.core import GameManager, OnlineManager
from src.utils import Logger, PositionCamera, GameSettings, Position
from src.core.services import sound_manager
from src.sprites import Sprite
from typing import override
from src.interface.components import Button, ToggleButton, Slider


class GameScene(Scene):
    game_manager: GameManager
    online_manager: OnlineManager | None
    sprite_online: Sprite
    
    inv_button: Button
    settings_button: Button
    
    # overlay handling
    back_button: Button
    active_overlay: str | None
    
    # settings overlay
    volume_toggle: ToggleButton
    volume_slider: Slider
    bg_frame: Sprite
    
    volume_label: pg.Surface
    mute_label: pg.Surface
    settings_title: pg.Surface
    font: pg.font.Font

    save_button: Button
    load_button: Button
    
    def __init__(self):
        super().__init__()
        # Game Manager
        manager = GameManager.load("saves/game0.json")
        if manager is None:
            Logger.error("Failed to load game manager")
            exit(1)
        self.game_manager = manager
        
        # Online Manager
        if GameSettings.IS_ONLINE:
            self.online_manager = OnlineManager()
        else:
            self.online_manager = None
        self.sprite_online = Sprite("ingame_ui/options1.png", (GameSettings.TILE_SIZE, GameSettings.TILE_SIZE))
        
        self.active_overlay: str | None = None

        def _toggle_overlay(target: str | None) -> None:
            if self.active_overlay == target:
                self.active_overlay = None
            else:
                self.active_overlay = target
        px, py = GameSettings.SCREEN_WIDTH *0.85, GameSettings.SCREEN_HEIGHT * 0.05
        
        # buttons
        self.inv_button = Button(
            "UI/button_backpack.png", "UI/button_backpack_hover.png",
            px, py, 50, 50,
            lambda: _toggle_overlay("backpack")
        )
        self.settings_button = Button(
            "UI/button_setting.png", "UI/button_setting_hover.png",
            px + 75, py, 50, 50,
            lambda: _toggle_overlay("settings")
        )
        
        # settings overlay elements
        self.back_button = Button(
            "UI/button_back.png", "UI/button_back_hover.png",
            px + 75, py, 50, 50,
            lambda: _toggle_overlay(None)
        )
        
        px, py = GameSettings.SCREEN_WIDTH // 2, GameSettings.SCREEN_HEIGHT // 2
        
        self.bg_frame = Sprite(
            "UI/raw/UI_Flat_Frame01a.png",
            (600, 400)
        )
        self.bg_frame.update_pos(Position(px - 300, py - 200))
        
        def _handle_volume_change(value: float) -> None:
            GameSettings.AUDIO_VOLUME = value
            if sound_manager.current_bgm:
                sound_manager.current_bgm.set_volume(value)
            self._update_volume_label()

        def _handle_mute_toggle(is_on: bool):
            if is_on:
                sound_manager.pause_all()
            else:
                sound_manager.resume_all()
            self._update_mute_label()

        element_x = px - 250
        self.volume_toggle = ToggleButton(
            "UI/raw/UI_Flat_ToggleOff01a.png", "UI/raw/UI_Flat_ToggleOn01a.png",
            element_x, py - 100,
            40, 40,
            on_toggle=_handle_mute_toggle
        )
        slider_width = 320
        slider_height = 24
        slider_x = element_x
        slider_y = py

        self.volume_slider = Slider(
            "UI/raw/UI_Flat_Bar05a.png",
            "UI/raw/UI_Flat_Handle01a.png",
            slider_x,
            slider_y,
            slider_width,
            slider_height,
            knob_size=(32, 32),
            initial_value=GameSettings.AUDIO_VOLUME,
            on_change=_handle_volume_change,
        )
        
        self.font = pg.font.Font("assets/fonts/Minecraft.ttf", 24)
        
        # Create text surfaces
        self._update_volume_label()
        self._update_mute_label()
        self.settings_title = self.font.render("Settings", True, (255, 255, 255))
        
        button_size = 100
        self.save_button = Button(
            "UI/button_save.png", "UI/button_save_hover.png",
            element_x, py + 50, button_size, button_size,
            lambda: self.game_manager.save("saves/game0.json")
        )
        self.load_button = Button(
            "UI/button_load.png", "UI/button_load_hover.png",
            element_x + button_size + 25, py + 50, button_size, button_size,
            self._load_game
        )

    def _load_game(self) -> None:
        manager = GameManager.load("saves/game0.json")
        if manager:
            self.game_manager = manager
            Logger.info("Game loaded successfully")
        else:
            Logger.warning("Failed to load game")
    def _update_volume_label(self):
        volume_text = f"Volume: {int(self.volume_slider.value * 100)}%"
        self.volume_label = self.font.render(volume_text, True, (255, 255, 255))

    def _update_mute_label(self):
        mute_text = "Muted" if self.volume_toggle.is_on else "Unmuted"
        self.mute_label = self.font.render(mute_text, True, (255, 255, 255))
        
    @override
    def enter(self) -> None:
        sound_manager.play_bgm("RBY 103 Pallet Town.ogg")
        if self.online_manager:
            self.online_manager.enter()
        
    @override
    def exit(self) -> None:
        if self.online_manager:
            self.online_manager.exit()
        
    @override
    def update(self, dt: float):
        # Check if there is assigned next scene
        self.game_manager.try_switch_map()
        
        # Update player and other data
        if self.game_manager.player:
            self.game_manager.player.update(dt)
        for enemy in self.game_manager.current_enemy_trainers:
            enemy.update(dt)
            
        # Update others
        self.game_manager.bag.update(dt)
        
        if self.game_manager.player is not None and self.online_manager is not None:
            _ = self.online_manager.update(
                self.game_manager.player.position.x, 
                self.game_manager.player.position.y,
                self.game_manager.current_map.path_name
            )
        if self.active_overlay == "settings":
            self.back_button.update(dt)
            self.volume_toggle.update(dt)
            self.volume_slider.update(dt)
            self.save_button.update(dt)
            self.load_button.update(dt)
        elif self.active_overlay == "backpack":
            self.back_button.update(dt)
        else:
            self.inv_button.update(dt)
            self.settings_button.update(dt)
        
    @override
    def draw(self, screen: pg.Surface):        
        if self.game_manager.player:
            '''
            [TODO HACKATHON 3]
            Implement the camera algorithm logic here
            Right now it's hard coded, you need to follow the player's positions
            you may use the below example, but the function still incorrect, you may trace the entity.py
            
            camera = self.game_manager.player.camera
            '''
            camera = PositionCamera(self.game_manager.player.position.x - GameSettings.SCREEN_WIDTH // 2, self.game_manager.player.position.y - GameSettings.SCREEN_HEIGHT // 2)
            self.game_manager.current_map.draw(screen, camera)
            self.game_manager.player.draw(screen, camera)
        else:
            camera = PositionCamera(0, 0)
            self.game_manager.current_map.draw(screen, camera)
        for enemy in self.game_manager.current_enemy_trainers:
            enemy.draw(screen, camera)

        self.game_manager.bag.draw(screen)
        
        if self.active_overlay:
            overlay = pg.Surface((GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT), pg.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))
            self.bg_frame.draw(screen)
            self.back_button.draw(screen)

            if self.active_overlay == "settings":
                self.volume_toggle.draw(screen)
                self.volume_slider.draw(screen)
                screen.blit(self.volume_label, (self.volume_slider.track_sprite.rect.left, self.volume_slider.track_sprite.rect.top - 30))
                screen.blit(self.mute_label, (self.volume_toggle.hitbox.left, self.volume_toggle.hitbox.top - 30))
                self.save_button.draw(screen)
                self.load_button.draw(screen)
                # draw title centered at the top of the frame
                title_rect = self.settings_title.get_rect(center=(GameSettings.SCREEN_WIDTH // 2, self.bg_frame.rect.top + 40))
                screen.blit(self.settings_title, title_rect)
            elif self.active_overlay == "backpack":
                pass  # temporary overlay only shows frame
        else:
            self.inv_button.draw(screen)
            self.settings_button.draw(screen)
            
            
        
        if self.online_manager and self.game_manager.player:
            list_online = self.online_manager.get_list_players()
            for player in list_online:
                if player["map"] == self.game_manager.current_map.path_name:
                    cam = self.game_manager.player.camera
                    pos = cam.transform_position_as_position(Position(player["x"], player["y"]))
                    self.sprite_online.update_pos(pos)
                    self.sprite_online.draw(screen)
