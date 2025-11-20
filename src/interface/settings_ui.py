import pygame as pg
from typing import Callable

from src.utils import GameSettings
from src.core.services import sound_manager
from src.interface.components import Button, ToggleButton, Slider

class SettingsUI:
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        on_save: Callable[[], None],
        on_load: Callable[[], None],
        on_exit: Callable[[], None]
    ):
        self.rect = pg.Rect(x, y, width, height)
        self.font = pg.font.Font("assets/fonts/Minecraft.ttf", 24)
        
        # Center point for relative positioning
        cx, cy = self.rect.centerx, self.rect.centery
        
        # --- Volume Controls ---
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

        element_x = cx - 250
        
        # Layout calculations for left alignment (matching backpack style)
        padding_left = 50
        start_x = self.rect.left + padding_left
        
        # Vertical positions
        y_toggle = cy - 120
        y_slider = cy - 20
        y_buttons = cy + 80
        
        button_size = 100
        gap = 25
        
        self.volume_toggle = ToggleButton(
            "UI/raw/UI_Flat_ToggleOff01a.png", "UI/raw/UI_Flat_ToggleOn01a.png",
            start_x, y_toggle,
            40, 40,
            on_toggle=_handle_mute_toggle
        )
        
        slider_width = width - (padding_left * 2)
        slider_height = 24
        slider_x = start_x
        slider_y = y_slider

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
        
        # --- Save / Load Buttons ---
        self.save_button = Button(
            "UI/button_save.png", "UI/button_save_hover.png",
            start_x, y_buttons, button_size, button_size,
            on_save
        )
        self.load_button = Button(
            "UI/button_load.png", "UI/button_load_hover.png",
            start_x + button_size + gap, y_buttons, button_size, button_size,
            on_load
        )
        self.exit_button = Button(
            "UI/button_back.png", "UI/button_back_hover.png",
            start_x + (button_size + gap) * 2, y_buttons, button_size, button_size,
            on_exit
        )
        
        # --- Labels ---
        self.settings_title = pg.font.Font("assets/fonts/Minecraft.ttf", 32).render("Settings", True, (255, 255, 255))
        self.volume_label = None
        self.mute_label = None
        
        self._update_volume_label()
        self._update_mute_label()

    def _update_volume_label(self):
        volume_text = f"Volume: {int(self.volume_slider.value * 100)}%"
        self.volume_label = self.font.render(volume_text, True, (255, 255, 255))

    def _update_mute_label(self):
        mute_text = "Muted" if self.volume_toggle.is_on else "Unmuted"
        self.mute_label = self.font.render(mute_text, True, (255, 255, 255))

    def update(self, dt: float):
        self.volume_toggle.update(dt)
        self.volume_slider.update(dt)
        self.save_button.update(dt)
        self.load_button.update(dt)
        self.exit_button.update(dt)

    def draw(self, screen: pg.Surface):
        # Draw Title
        title_rect = self.settings_title.get_rect(center=(self.rect.centerx, self.rect.top + 40))
        screen.blit(self.settings_title, title_rect)
        
        # Draw Controls
        self.volume_toggle.draw(screen)
        self.volume_slider.draw(screen)
        self.save_button.draw(screen)
        self.load_button.draw(screen)
        self.exit_button.draw(screen)
        
        # Draw Labels
        if self.volume_label:
            screen.blit(self.volume_label, (self.volume_slider.track_sprite.rect.left, self.volume_slider.track_sprite.rect.top - 30))
        if self.mute_label:
            screen.blit(self.mute_label, (self.volume_toggle.hitbox.left, self.volume_toggle.hitbox.top - 30))
