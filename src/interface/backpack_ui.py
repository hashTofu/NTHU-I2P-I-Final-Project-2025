import pygame as pg
from src.data.bag import Bag
from src.utils import GameSettings
from src.core.services import resource_manager
from src.sprites import Sprite
from src.interface.components.monster_banner import MonsterBanner

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
        
        self.monster_banners: list[MonsterBanner] = []
        self.rebuild_banners()
        
    def rebuild_banners(self):
        self.monster_banners = []
        start_y = self.rect.top + self.padding + 40
        start_x = self.rect.left + self.padding
        entry_height = 70 + 2
        
        for i, monster in enumerate(self.bag.monsters):
            y = start_y + i * entry_height
            banner = MonsterBanner(start_x, y, monster)
            self.monster_banners.append(banner)
        
    def update(self, dt: float):
        if len(self.monster_banners) != len(self.bag.monsters):
            self.rebuild_banners()
        
        for i, banner in enumerate(self.monster_banners):
            banner.update_data(self.bag.monsters[i])

    def draw(self, screen: pg.Surface):
        # Define columns
        col_width = self.rect.width // 2
        start_y = self.rect.top + self.padding
        item_spacing = 10
        
        title_surf = self.title_font.render("Backpack", True, (0, 0, 0))
        title_rect = title_surf.get_rect(topleft=(self.rect.x + self.padding, self.rect.top + self.padding))
        screen.blit(title_surf, title_rect)
        
        # --- Monsters Column (Left) ---
        for banner in self.monster_banners:
            banner.draw(screen)

        # --- Items Column (Right) ---
        item_start_y = start_y + 40
        item_start_x = self.rect.left + col_width + self.padding
        
        item_icon_size = self.slot_size // 2

        for i, item in enumerate(self.bag.items):
            x = item_start_x
            y = item_start_y + i * (item_icon_size + 10)
            
            # Draw Item Icon
            try:
                if item['sprite_path']:
                    img = resource_manager.get_image(item['sprite_path'])
                    img = pg.transform.scale(img, (item_icon_size, item_icon_size))
                    screen.blit(img, (x, y))
                else:
                    pg.draw.rect(screen, (100, 100, 100), (x, y, item_icon_size, item_icon_size))
            except Exception:
                 pg.draw.rect(screen, (255, 0, 0), (x, y, item_icon_size, item_icon_size))

            # Draw Count
            count_surf = self.font.render(f"x{item['count']}", True, (0, 0, 0))
            screen.blit(count_surf, (x + item_icon_size + 10, y + item_icon_size // 2))
            
            # Draw Name
            name_surf = self.font.render(item['name'], True, (0, 0, 0))
            screen.blit(name_surf, (x + item_icon_size + 10, y))

