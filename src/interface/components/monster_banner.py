import pygame as pg
from src.core.services import resource_manager
from .component import UIComponent

class MonsterBanner(UIComponent):
    def __init__(self, x: int, y: int, monster_data: dict):
        self.rect = pg.Rect(x, y, 245, 70)
        self.monster_data = monster_data
        
        self.font = resource_manager.get_font("Minecraft.ttf", 16)
        
        # Load banner
        self.banner_img = resource_manager.get_image("UI/raw/UI_Flat_Banner03a.png")
        self.banner_img = pg.transform.scale(self.banner_img, (self.rect.width, self.rect.height))
        
        self.slot_size = 64

    def update(self, dt: float) -> None:
        pass

    def update_data(self, monster_data: dict):
        self.monster_data = monster_data

    def draw(self, screen: pg.Surface) -> None:
        x, y = self.rect.topleft
        
        # Draw Banner Background
        screen.blit(self.banner_img, (x, y))
        
        if not self.monster_data:
            return

        # Icon offset inside banner
        icon_x = x + 20
        icon_y = y - 4
        
        try:
            if self.monster_data.get('id'):
                img = resource_manager.get_image(f'menu_sprites/menusprite{self.monster_data['id']}.png')
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
        name_surf = self.font.render(self.monster_data.get('name', 'Unknown'), True, (0, 0, 0))
        screen.blit(name_surf, (info_x, info_y_start))
        
        # HP Bar
        bar_width = 80
        bar_height = 8
        bar_y = info_y_start + 15
        
        hp = self.monster_data.get('hp', 0)
        max_hp = self.monster_data.get('max_hp', 1)
        hp_ratio = hp / max(1, max_hp)
        
        pg.draw.rect(screen, (50, 50, 50), (info_x, bar_y, bar_width, bar_height)) # Background
        pg.draw.rect(screen, (0, 255, 0), (info_x, bar_y, int(bar_width * hp_ratio), bar_height)) # Foreground
        
        # Level
        lvl_surf = self.font.render(f"Lv{self.monster_data.get('level', 1)}", True, (0, 0, 0))
        screen.blit(lvl_surf, (info_x + bar_width + 10, bar_y - (bar_height // 2)))
        
        # HP Text
        hp_text = f"{hp}/{max_hp}"
        hp_surf = self.font.render(hp_text, True, (0, 0, 0))
        screen.blit(hp_surf, (info_x, bar_y + 12))
