import pygame as pg
from src.data.bag import Bag
from src.utils import GameSettings
from src.core.services import resource_manager
from src.sprites import Sprite

class BackpackUI:
    def __init__(self, bag: Bag, x: int, y: int, width: int, height: int):
        self.bag = bag
        self.rect = pg.Rect(x, y, width, height)
        self.font = pg.font.Font("assets/fonts/Minecraft.ttf", 16)
        self.title_font = pg.font.Font("assets/fonts/Minecraft.ttf", 32)
        
        # Layout constants
        self.padding = 20
        self.slot_size = 64
        self.cols = 4
        
        # Load banner for monsters
        self.monster_banner = resource_manager.get_image("UI/raw/UI_Flat_Banner03a.png")
        self.banner_width = 245
        self.banner_height = 70
        self.monster_banner = pg.transform.scale(self.monster_banner, (self.banner_width, self.banner_height))
        
    def update(self, dt: float):
        # Future: Handle scrolling or clicking items
        pass

    def draw(self, screen: pg.Surface):
        # Define columns
        col_width = self.rect.width // 2
        start_y = self.rect.top + self.padding
        item_spacing = 10
        
        title_surf = self.title_font.render("Backpack", True, (0, 0, 0))
        title_rect = title_surf.get_rect(topleft=(self.rect.x + self.padding, self.rect.top + self.padding))
        screen.blit(title_surf, title_rect)
        
        # --- Monsters Column (Left) ---
        monster_start_y = start_y + 40
        monster_start_x = self.rect.left + self.padding
        
        # More compact spacing
        entry_height = self.banner_height + 2
        
        for i, monster in enumerate(self.bag.monsters):
            x = monster_start_x
            y = monster_start_y + i * entry_height
            
            # Draw Banner Background
            screen.blit(self.monster_banner, (x, y))
            
            # Icon offset inside banner
            icon_x = x + 20
            icon_y = y - 4
            
            try:
                if monster['sprite_path']:
                    img = resource_manager.get_image(monster['sprite_path'])
                    img = pg.transform.scale(img, (self.slot_size, self.slot_size))
                    screen.blit(img, (icon_x, icon_y))
                else:
                    pg.draw.rect(screen, (100, 100, 100), (icon_x, icon_y, self.slot_size, self.slot_size))
            except Exception:
                pg.draw.rect(screen, (0, 0, 255), (icon_x, icon_y, self.slot_size, self.slot_size))
            
            # Info Area
            info_x = icon_x + self.slot_size + 15
            info_y_start = y + 7
            
            # Name
            name_surf = self.font.render(monster['name'], True, (0, 0, 0))
            screen.blit(name_surf, (info_x, info_y_start))
            
            # HP Bar
            bar_width = 80
            bar_height = 8
            bar_y = info_y_start + 15
            
            hp_ratio = monster['hp'] / max(1, monster['max_hp'])
            pg.draw.rect(screen, (50, 50, 50), (info_x, bar_y, bar_width, bar_height)) # Background
            pg.draw.rect(screen, (0, 255, 0), (info_x, bar_y, int(bar_width * hp_ratio), bar_height)) # Foreground
            
            # Level
            lvl_surf = self.font.render(f"Lv{monster['level']}", True, (0, 0, 0))
            screen.blit(lvl_surf, (info_x + bar_width + 10, bar_y - (bar_height // 2)))
            
            # HP Text
            hp_text = f"{monster['hp']}/{monster['max_hp']}"
            hp_surf = self.font.render(hp_text, True, (0, 0, 0))
            screen.blit(hp_surf, (info_x, bar_y + 12))

        # --- Items Column (Right) ---
        item_start_y = start_y + 40
        item_start_x = self.rect.left + col_width + self.padding
        
        for i, item in enumerate(self.bag.items):
            x = item_start_x
            y = item_start_y + i * (self.slot_size + 10)
            
            # Draw Item Icon
            try:
                if item['sprite_path']:
                    img = resource_manager.get_image(item['sprite_path'])
                    img = pg.transform.scale(img, (self.slot_size, self.slot_size))
                    screen.blit(img, (x, y))
                else:
                    pg.draw.rect(screen, (100, 100, 100), (x, y, self.slot_size, self.slot_size))
            except Exception:
                 pg.draw.rect(screen, (255, 0, 0), (x, y, self.slot_size, self.slot_size))

            # Draw Count
            count_surf = self.font.render(f"x{item['count']}", True, (0, 0, 0))
            screen.blit(count_surf, (x + self.slot_size + 10, y + self.slot_size // 2 - 10))
            
            # Draw Name
            name_surf = self.font.render(item['name'], True, (0, 0, 0))
            screen.blit(name_surf, (x + self.slot_size + 10, y))

            # Draw Count
            count_surf = self.font.render(f"x{item['count']}", True, (0, 0, 0))
            screen.blit(count_surf, (x + self.slot_size + 10, y + self.slot_size // 2 - 10))
            
            # Draw Name
            name_surf = self.font.render(item['name'], True, (0, 0, 0))
            screen.blit(name_surf, (x + self.slot_size + 10, y))

