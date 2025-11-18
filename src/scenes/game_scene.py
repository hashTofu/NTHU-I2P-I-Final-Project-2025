import pygame as pg
import threading
import time

from src.scenes.scene import Scene
from src.core import GameManager, OnlineManager
from src.utils import Logger, PositionCamera, GameSettings, Position
from src.core.services import sound_manager
from src.sprites import Sprite
from typing import override
from src.interface.components import Button


class GameScene(Scene):
    game_manager: GameManager
    online_manager: OnlineManager | None
    sprite_online: Sprite
    
    inv_button: Button
    settings_button: Button
    back_button: Button
    show_overlay: bool
    
    
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
        
        self.show_overlay = False
        def _toggle_overlay(self):
            self.show_overlay = not self.show_overlay
        px, py = GameSettings.SCREEN_WIDTH *0.85, GameSettings.SCREEN_HEIGHT * 0.05
        self.inv_button = Button(
            "UI/button_backpack.png", "UI/button_backpack_hover.png",
            px, py, 50, 50,
            lambda: _toggle_overlay(self)
        )
        self.settings_button = Button(
            "UI/button_setting.png", "UI/button_setting_hover.png",
            px + 75, py, 50, 50,
            lambda: _toggle_overlay(self)
        )
        self.back_button = Button(
            "UI/button_back.png", "UI/button_back_hover.png",
            px + 75, py, 50, 50,
            lambda: _toggle_overlay(self)
        )
        
        
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
        if self.show_overlay:
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
        
        self.game_manager.bag.draw(screen)
        if self.show_overlay:
            overlay = pg.Surface((GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT), pg.SRCALPHA)
            overlay.fill((0, 0, 0, 160))  # RGBA
            screen.blit(overlay, (0, 0))
            self.back_button.draw(screen)
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
