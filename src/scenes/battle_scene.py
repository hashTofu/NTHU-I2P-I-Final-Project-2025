import random
import pygame as pg
from src.scenes.scene import Scene
from src.utils import GameSettings, Position
from src.core.services import scene_manager, sound_manager, input_manager
from src.interface.components.button import Button
from src.interface.components.monster_banner import MonsterBanner
from src.sprites import Sprite, Animation
from typing import override
from enum import Enum, auto

class BattleState(Enum):
    PLAYER_TURN = auto()
    ENEMY_TURN = auto()
    BUSY = auto()
    WON = auto()
    LOST = auto()

class BattleScene(Scene):
    def __init__(self):
        super().__init__()
        self.state = BattleState.PLAYER_TURN
        self.next_state: BattleState | None = None
        self.font = pg.font.Font("assets/fonts/Minecraft.ttf", 16)
        
        # Background
        self.background = Sprite("backgrounds/background1.png", (GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT))

        # Player Animation
        self.player_sprite = Animation("character/ow1.png", ["down", "left", "right", "up"], 4, (256, 256))
        self.player_sprite.switch("up")
        self.player_pos = Position(100, 300)
        self.player_sprite.update_pos(self.player_pos)

        # Enemy Animation
        self.enemy_sprite = Animation("sprites/sprite1_idle.png", ["idle"], 4, (256, 256))
        self.enemy_pos = Position(900, 100)
        self.enemy_sprite.update_pos(self.enemy_pos)
        self.enemy_is_trainer = False

        # Active Monsters State
        self.active_player_monster: dict | None = None
        self.active_enemy_monster: dict | None = None
        self.player_banner: MonsterBanner | None = None
        self.enemy_banner: MonsterBanner | None = None
        self.pending_enemy_monster: dict | None = None
        self.pending_player_monster: dict | None = None

        # UI Elements
        self.dialogue_text = "A wild Monster appeared!"
        self.dialogue_hint = "Press SPACE to continue."
        
        # Buttons
        button_size = 100
        # Align buttons in a single row on the right side
        total_width = 4 * button_size + 3 * 10
        start_x = GameSettings.SCREEN_WIDTH - total_width - 50
        start_y = GameSettings.SCREEN_HEIGHT - button_size - 40
        
        self.buttons: list[tuple[Button, str]] = []
        self._create_buttons(["Attack", "Bag", "Pokemon", "Run"])

    def _create_buttons(self, labels: list[str]):
        self.buttons = []
        button_size = 100
        total_width = 4 * button_size + 3 * 10
        start_x = GameSettings.SCREEN_WIDTH - total_width - 50
        start_y = GameSettings.SCREEN_HEIGHT - button_size - 40
        
        for i, label in enumerate(labels):
            x = start_x + i * (button_size + 10)
            y = start_y
            
            btn = Button(
                "UI/raw/UI_Flat_Button01a_2.png",
                "UI/raw/UI_Flat_Button01a_1.png",
                int(x), int(y), button_size, button_size,
                lambda l=label: self.on_button_click(l)
            )
            self.buttons.append((btn, label))

    def setup_battle(self, type: str, enemy_monster: dict | None = None):
        self.active_player_monster = None
        self.active_enemy_monster = None
        self.player_banner = None
        self.enemy_banner = None
        self.pending_player_monster = None
        
        # Setup Buttons
        if type == "wild":
            self._create_buttons(["Attack", "Catch", "Pokemon", "Run"])
        else:
            self._create_buttons(["Attack", "Bag", "Pokemon", "Run"])
        
        # Reset player sprite to trainer
        self.player_sprite = Animation("character/ow1.png", ["down", "left", "right", "up"], 4, (256, 256))
        if type == "trainer":
             self.player_sprite.switch("up")
        else:
             self.player_sprite.switch("right")
        self.player_pos = Position(100, 300)
        self.player_sprite.update_pos(self.player_pos)
        
        if type == "trainer":
            sound_manager.play_bgm("RBY 107 Battle! (Trainer).ogg")
            self.dialogue_text = "Trainer challenges you to a battle!"
            
            self.enemy_sprite = Animation("character/ow1.png", ["down", "left", "right", "up"], 4, (128, 128))
            self.enemy_sprite.switch("down")
            self.enemy_sprite.update_pos(Position(900, 250))
            self.enemy_sprite.update(0)
            self.enemy_is_trainer = True
            
            if enemy_monster:
                self.pending_enemy_monster = enemy_monster
                self.state = BattleState.BUSY
            
        else:
            sound_manager.play_bgm("RBY 110 Battle! (Wild Pokemon).ogg")
            
            if enemy_monster:
                self.switch_enemy_monster(enemy_monster)
                self.dialogue_text = f"A wild {enemy_monster['name']} appeared!"
                self.state = BattleState.BUSY # Wait for player to send out monster
            else:
                self.dialogue_text = "A wild Monster appeared!"
                # Fallback if no monster provided
                self.enemy_sprite = Animation("sprites/sprite1_idle.png", ["idle"], 4, (256, 256))
                self.enemy_sprite.update_pos(self.enemy_pos)
                self.enemy_is_trainer = False

        # Get Player's Monster from Bag
        game_scene = scene_manager.get_scene("game")
        if hasattr(game_scene, "game_manager"):
             bag = game_scene.game_manager.bag
             if bag.monsters:
                 self.pending_player_monster = random.choice(bag.monsters)


    def switch_player_monster(self, monster_data: dict):
        self.active_player_monster = monster_data
        
        # Update Banner
        if self.player_banner is None:
            # Position: Bottom Right, above buttons
            self.player_banner = MonsterBanner(GameSettings.SCREEN_WIDTH - 280, GameSettings.SCREEN_HEIGHT - 300, monster_data)
        else:
            self.player_banner.update_data(monster_data)
            
        # Update Sprite
        monster_id = monster_data.get("id", 1)
        path = f"sprites/sprite{monster_id}.png"
             
        # Use static sprite with right half of the image
        self.player_sprite = Sprite(path)
        
        # Crop right half
        full_w, full_h = self.player_sprite.image.get_size()
        half_w = full_w // 2
        right_half = self.player_sprite.image.subsurface(pg.Rect(half_w, 0, half_w, full_h))
        
        # Scale to 384x384 (multiple of 96)
        size = 96 * 4
        self.player_sprite.image = pg.transform.scale(right_half, (size, size))
        self.player_sprite.rect = self.player_sprite.image.get_rect()
        
        # Position adjustment
        panel_y = GameSettings.SCREEN_HEIGHT - 180
        sprite_height = size
        new_y = panel_y - sprite_height
        self.player_pos = Position(100, new_y)
        self.player_sprite.update_pos(self.player_pos)
        
    def switch_enemy_monster(self, monster_data: dict):
        self.active_enemy_monster = monster_data
        
        self.dialogue_text = f"Enemy chose {monster_data["name"]}!"
        
        # Update Banner
        if self.enemy_banner is None:
            # Position: Top Left
            self.enemy_banner = MonsterBanner(20, 20, monster_data)
        else:
            self.enemy_banner.update_data(monster_data)
            
        # Update Sprite
        monster_id = monster_data.get("id", 1)
        path = f"sprites/sprite{monster_id}_idle.png"
             
        self.enemy_sprite = Animation(path, ["idle"], 4, (256, 256))
        self.enemy_sprite.update_pos(Position(850, 100))
        self.enemy_is_trainer = False

    def on_button_click(self, label: str):
        if self.state != BattleState.PLAYER_TURN:
            return

        if label == "Attack":
            damage = 10 # Fixed damage for now
            self.dialogue_text = f"{self.active_player_monster['name']} attacked {self.active_enemy_monster['name']} for {damage} damage!"
            self.active_enemy_monster['hp'] -= damage
            if self.active_enemy_monster['hp'] < 0:
                self.active_enemy_monster['hp'] = 0
            
            if self.enemy_banner:
                self.enemy_banner.update_data(self.active_enemy_monster)
                
            if self.active_enemy_monster['hp'] <= 0:
                self.state = BattleState.WON
                self.dialogue_text = "You Won!"
                self.dialogue_hint = "Press SPACE to exit."
            else:
                self.state = BattleState.BUSY
                self.next_state = BattleState.ENEMY_TURN
                self.dialogue_hint = "Press SPACE to continue."

        elif label == "Catch":
             # Add monster to bag
             game_scene = scene_manager.get_scene("game")
             if hasattr(game_scene, "game_manager"):
                 bag = game_scene.game_manager.bag
                 if self.active_enemy_monster:
                     bag.add_monster(self.active_enemy_monster)
                     self.dialogue_text = f"You caught {self.active_enemy_monster['name']}!"
                     self.state = BattleState.WON
                     self.dialogue_hint = "Press SPACE to exit."

        elif label == "Run":
             scene_manager.change_scene("game")

    @override
    def enter(self) -> None:
        pass

    @override
    def exit(self) -> None:
        pass

    @override
    def update(self, dt: float) -> None:
        if self.active_player_monster != None:
            self.player_sprite.update(dt)
        if self.active_enemy_monster != None:
            self.enemy_sprite.update(dt)
        for btn, _ in self.buttons:
            btn.update(dt)
            
        # Battle Loop Logic
        if self.state == BattleState.BUSY:
            if input_manager.key_pressed(pg.K_SPACE):
                if self.pending_enemy_monster:
                    self.switch_enemy_monster(self.pending_enemy_monster)
                    self.pending_enemy_monster = None
                elif self.pending_player_monster:
                    self.switch_player_monster(self.pending_player_monster)
                    self.dialogue_text = f"Go! {self.active_player_monster['name']}!"
                    self.pending_player_monster = None
                    self.state = BattleState.PLAYER_TURN
                    self.dialogue_hint = ""
                else:
                    self.state = self.next_state if self.next_state else BattleState.PLAYER_TURN
                    self.next_state = None
                    
                    # Reset enemy sprite to idle
                    if self.active_enemy_monster:
                        monster_id = self.active_enemy_monster.get("id", 1)
                        path = f"sprites/sprite{monster_id}_idle.png"
                        self.enemy_sprite = Animation(path, ["idle"], 4, (256, 256))
                        self.enemy_sprite.update_pos(Position(850, 100))
                    
        elif self.state == BattleState.PLAYER_TURN:
            # Waiting for player input (handled by buttons)
            pass
        elif self.state == BattleState.ENEMY_TURN:
            # Simple AI: Attack after a delay
            self.enemy_attack()
        
        elif self.state == BattleState.WON or self.state == BattleState.LOST:
             if input_manager.key_pressed(pg.K_SPACE):
                 scene_manager.change_scene("game")
            
    def enemy_attack(self):
        damage = 5 # Fixed damage for now
        self.dialogue_text = f"Enemy {self.active_enemy_monster['name']} attacked {self.active_player_monster['name']} for {damage} damage!"
        
        # Change sprite to attack
        monster_id = self.active_enemy_monster.get("id", 1)
        path = f"sprites/sprite{monster_id}_attack.png"
        self.enemy_sprite = Animation(path, ["attack"], 4, (256, 256))
        self.enemy_sprite.update_pos(Position(850, 100))
        
        self.active_player_monster['hp'] -= damage
        if self.active_player_monster['hp'] < 0:
            self.active_player_monster['hp'] = 0
            
        if self.player_banner:
            self.player_banner.update_data(self.active_player_monster)
            
        if self.active_player_monster['hp'] <= 0:
            self.state = BattleState.LOST
            self.dialogue_text = "You Lost!"
            self.dialogue_hint = "Press SPACE to exit."
        else:
            self.state = BattleState.BUSY
            self.next_state = BattleState.PLAYER_TURN
            self.dialogue_hint = "Press SPACE to continue."
        
        

    @override
    def draw(self, screen: pg.Surface) -> None:
        self.background.draw(screen)
        
        # Draw sprites
        self.player_sprite.draw(screen)
        self.enemy_sprite.draw(screen)
        
        # Draw Banners
        if self.player_banner:
            self.player_banner.draw(screen)
        if self.enemy_banner:
            self.enemy_banner.draw(screen)
        
        # Draw UI Background Panel
        panel_height = 180
        panel_y = GameSettings.SCREEN_HEIGHT - panel_height
        panel_rect = pg.Rect(0, panel_y, GameSettings.SCREEN_WIDTH, panel_height)
        pg.draw.rect(screen, (40, 40, 40), panel_rect)
        pg.draw.rect(screen, (20, 20, 20), panel_rect, 4)

        # Draw Dialogue Box
        dialogue_rect = pg.Rect(50, GameSettings.SCREEN_HEIGHT - 140, 600, 100)
        pg.draw.rect(screen, (245, 245, 220), dialogue_rect)
        pg.draw.rect(screen, (0, 0, 0), dialogue_rect, 4) # Border
        
        text_surf = self.font.render(self.dialogue_text, True, (0, 0, 0))
        screen.blit(text_surf, (dialogue_rect.x + 20, dialogue_rect.y + 20))
        
        hint_surf = self.font.render(self.dialogue_hint, True, (0, 0, 0, 150))
        screen.blit(hint_surf, (dialogue_rect.right - 225, dialogue_rect.bottom - 30))
        
        # Draw Buttons
        if self.state is BattleState.PLAYER_TURN:
            for btn, label in self.buttons:
                btn.draw(screen)
                # Draw label on button
                label_surf = self.font.render(label, True, (0, 0, 0))
                label_rect = label_surf.get_rect(center=btn.hitbox.center)
                screen.blit(label_surf, label_rect)
