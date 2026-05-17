"""
button.py — Button class
=========================
A reusable UI Button with:
  - Bounding-box hit detection
  - Hover state (color shift + subtle scale-up via rect expansion)
  - Click callback support
  - Optional icon character prefix
"""

from __future__ import annotations
import pygame


# ---------------------------------------------------------------------------
# Colour palette (shared constants)
# ---------------------------------------------------------------------------

CLR_BTN_NORMAL   = (30,  40,  60)
CLR_BTN_HOVER    = (50,  70, 110)
CLR_BTN_BORDER   = (80, 120, 200)
CLR_BTN_TEXT     = (220, 235, 255)
CLR_BTN_ACTIVE   = (200,  60,  60)   # for destructive / decision buttons


class Button:
    """
    Renders a rounded rectangle button and detects hover / click states.

    Args:
        rect        : (x, y, w, h) bounding box
        label       : text to display
        callback    : callable invoked on confirmed click
        color       : base fill colour (defaults to CLR_BTN_NORMAL)
        text_color  : label colour
        font_size   : pixels
        border_radius: corner rounding
        icon        : optional emoji / unicode prefix
    """

    def __init__(self,
                 rect: tuple[int, int, int, int],
                 label: str,
                 callback=None,
                 color: tuple = CLR_BTN_NORMAL,
                 text_color: tuple = CLR_BTN_TEXT,
                 font_size: int = 18,
                 border_radius: int = 10,
                 icon: str = "") -> None:

        self.base_rect      = pygame.Rect(rect)
        self.label          = label
        self.callback       = callback
        self.base_color     = color
        self.text_color     = text_color
        self.border_radius  = border_radius
        self.icon           = icon

        self.is_hovered     = False
        self.is_pressed     = False   # True for one frame after click

        self._font = pygame.font.SysFont("segoeui", font_size, bold=False)
        self._font_bold = pygame.font.SysFont("segoeui", font_size, bold=True)

    # ------------------------------------------------------------------
    def _get_draw_rect(self) -> pygame.Rect:
        """
        When hovered, expand the rect by 3px on each side to simulate a
        subtle scale-up without a full matrix transform.
        """
        if self.is_hovered:
            return self.base_rect.inflate(6, 6)
        return self.base_rect

    def _get_color(self) -> tuple:
        if self.is_pressed:
            return tuple(min(c + 60, 255) for c in self.base_color)
        if self.is_hovered:
            # Blend toward CLR_BTN_HOVER
            blended = tuple(
                int(self.base_color[i] * 0.4 + CLR_BTN_HOVER[i] * 0.6)
                for i in range(3)
            )
            return blended
        return self.base_color

    # ------------------------------------------------------------------
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Process mouse events. Returns True if the button was clicked.
        Call this inside the game event loop.
        """
        mouse_pos = pygame.mouse.get_pos()
        self.is_hovered = self.base_rect.collidepoint(mouse_pos)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                self.is_pressed = True
                return False  # wait for MOUSEBUTTON_UP to confirm

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            was_pressed = self.is_pressed
            self.is_pressed = False
            if was_pressed and self.is_hovered:
                if self.callback:
                    self.callback()
                return True  # click confirmed

        return False

    # ------------------------------------------------------------------
    def draw(self, surface: pygame.Surface) -> None:
        """Render the button onto *surface*."""
        draw_rect = self._get_draw_rect()
        color     = self._get_color()

        # Shadow (subtle depth effect)
        shadow_rect = draw_rect.move(2, 3)
        shadow_surf = pygame.Surface((draw_rect.w, draw_rect.h), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 80),
                         (0, 0, draw_rect.w, draw_rect.h),
                         border_radius=self.border_radius)
        surface.blit(shadow_surf, shadow_rect.topleft)

        # Fill
        pygame.draw.rect(surface, color, draw_rect,
                         border_radius=self.border_radius)

        # Border — brighter when hovered
        border_color = CLR_BTN_BORDER if self.is_hovered else (50, 70, 100)
        pygame.draw.rect(surface, border_color, draw_rect,
                         width=1, border_radius=self.border_radius)

        # Label
        full_label = f"{self.icon}  {self.label}" if self.icon else self.label
        font = self._font_bold if self.is_hovered else self._font
        text_surf = font.render(full_label, True, self.text_color)
        text_rect = text_surf.get_rect(center=draw_rect.center)
        surface.blit(text_surf, text_rect)
