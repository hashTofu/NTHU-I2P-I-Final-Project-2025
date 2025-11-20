import pygame as pg
import threading
import time

from src.scenes.scene import Scene
from src.core import GameManager, OnlineManager
from src.utils import Logger, PositionCamera, GameSettings, Position
from src.core.services import sound_manager, scene_manager
from src.sprites import Sprite
from typing import override
from src.interface.components import Button, ToggleButton, Slider
from src.interface.backpack_ui import BackpackUI
from src.interface.settings_ui import SettingsUI


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
    settings_ui: SettingsUI
    bg_frame: Sprite
    
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
        
        frame_width, frame_height = 800, 500
        
        self.bg_frame = Sprite(
            "UI/raw/UI_Flat_Frame01a.png",
            (frame_width, frame_height)
        )
        self.bg_frame.update_pos(Position(px - frame_width // 2, py - frame_height // 2))
        
        self.backpack_ui = BackpackUI(self.game_manager.bag, int(px - frame_width // 2), int(py - frame_height // 2), frame_width, frame_height)
        
        self.settings_ui = SettingsUI(
            int(px - frame_width // 2), int(py - frame_height // 2), frame_width, frame_height,
            on_save=lambda: self.game_manager.save("saves/game0.json"),
            on_load=self._load_game,
            on_exit=lambda: scene_manager.change_scene("menu")
        )

    def _load_game(self) -> None:
        manager = GameManager.load("saves/game0.json")
        if manager:
            self.game_manager = manager
            Logger.info("Game loaded successfully")
        else:
            Logger.warning("Failed to load game")
        
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
            self.settings_ui.update(dt)
        elif self.active_overlay == "backpack":
            self.back_button.update(dt)
            self.backpack_ui.update(dt)
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
                self.settings_ui.draw(screen)
            elif self.active_overlay == "backpack":
                self.backpack_ui.draw(screen)
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
