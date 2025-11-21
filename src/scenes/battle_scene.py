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
    BUSY = auto() # Animations, text scrolling
    WON = auto()
    LOST = auto()

class BattleScene(Scene):
    def __init__(self):
        super().__init__()
        self.state = BattleState.PLAYER_TURN
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
        self.enemy_pos = Position(900, 200)
        self.enemy_sprite.update_pos(self.enemy_pos)
        self.enemy_is_trainer = False

        # Active Monsters State
        self.active_player_monster: dict | None = None
        self.active_enemy_monster: dict | None = None
        self.player_banner: MonsterBanner | None = None
        self.enemy_banner: MonsterBanner | None = None
        self.pending_enemy_monster: dict | None = None

        # UI Elements
        self.dialogue_text = "A wild Monster appeared!"
        self.dialogue_hint = "Press SPACE to continue."
        
        # Buttons
        button_size = 100
        start_x = GameSettings.SCREEN_WIDTH - button_size * 2 - 50
        start_y = GameSettings.SCREEN_HEIGHT - button_size * 2 - 50
        
        self.buttons: list[tuple[Button, str]] = []
        
        labels = ["Attack", "Bag", "Pokemon", "Run"]
        for i, label in enumerate(labels):
            x = start_x + (i % 2) * (button_size + 10)
            y = start_y + (i // 2) * (button_size + 10)
            
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
        
        if type == "trainer":
            sound_manager.play_bgm("RBY 107 Battle! (Trainer).ogg")
            self.dialogue_text = "Trainer wants to battle!"
            self.player_sprite.switch("up")
            
            self.enemy_sprite = Animation("character/ow1.png", ["down", "left", "right", "up"], 4, (128, 128))
            self.enemy_sprite.switch("down")
            self.enemy_sprite.update_pos(self.enemy_pos)
            self.enemy_sprite.update(0)
            self.enemy_is_trainer = True
            
            if enemy_monster:
                self.pending_enemy_monster = enemy_monster
                self.state = BattleState.BUSY
            
        else:
            sound_manager.play_bgm("RBY 110 Battle! (Wild Pokemon).ogg")
            self.dialogue_text = "A wild Monster appeared!"
            self.player_sprite.switch("right")
            
            if enemy_monster:
                self.switch_enemy_monster(enemy_monster)
            else:
                # Fallback if no monster provided
                self.enemy_sprite = Animation("sprites/sprite1_idle.png", ["idle"], 4, (256, 256))
                self.enemy_sprite.update_pos(self.enemy_pos)
                self.enemy_is_trainer = False


    def switch_player_monster(self, monster_data: dict):
        self.active_player_monster = monster_data
        
        # Update Banner
        if self.player_banner is None:
            # Position: Bottom Right, above buttons
            self.player_banner = MonsterBanner(GameSettings.SCREEN_WIDTH - 280, GameSettings.SCREEN_HEIGHT - 300, monster_data)
        else:
            self.player_banner.update_data(monster_data)
            
        # Update Sprite
        path = monster_data.get('sprite_path', 'sprites/placeholder.png')
        if not "idle" in path and "sprites" in path:
             path = path.replace(".png", "_idle.png")
             
        self.player_sprite = Animation(path, ["idle"], 4, (256, 256))
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
        path = monster_data.get('sprite_path', 'sprites/placeholder.png')
        if not "idle" in path and "sprites" in path:
             path = path.replace(".png", "_idle.png")
             
        self.enemy_sprite = Animation(path, ["idle"], 4, (256, 256))
        self.enemy_sprite.update_pos(Position(850, 150))
        self.enemy_is_trainer = False

    def on_button_click(self, label: str):
        self.dialogue_text = f"Player chose {label}!"
        if label == "Run":
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
            if self.pending_enemy_monster and input_manager.key_pressed(pg.K_SPACE):
                self.switch_enemy_monster(self.pending_enemy_monster)
                self.pending_enemy_monster = None
                self.state = BattleState.PLAYER_TURN
                    
        elif self.state == BattleState.PLAYER_TURN:
            # Waiting for player input (handled by buttons)
            pass
        elif self.state == BattleState.ENEMY_TURN:
            # Simple AI: Attack after a delay
            self.enemy_attack()
            
    def enemy_attack(self):
        self.dialogue_text = "Enemy attacked!"
        # Apply damage logic here
        self.state = BattleState.PLAYER_TURN
        
        

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
        
        # Draw Dialogue Box
        dialogue_rect = pg.Rect(50, GameSettings.SCREEN_HEIGHT - 150, 600, 130)
        pg.draw.rect(screen, (245, 245, 220), dialogue_rect)
        pg.draw.rect(screen, (0, 0, 0), dialogue_rect, 4) # Border
        
        text_surf = self.font.render(self.dialogue_text, True, (0, 0, 0))
        screen.blit(text_surf, (dialogue_rect.x + 20, dialogue_rect.y + 20))
        
        hint_surf = self.font.render(self.dialogue_hint, True, (0, 0, 0, 150))
        screen.blit(hint_surf, (dialogue_rect.right - 225, dialogue_rect.bottom - 30))
        
        # Draw Buttons
        for btn, label in self.buttons:
            btn.draw(screen)
            # Draw label on button
            label_surf = self.font.render(label, True, (0, 0, 0))
            label_rect = label_surf.get_rect(center=btn.hitbox.center)
            screen.blit(label_surf, label_rect)
