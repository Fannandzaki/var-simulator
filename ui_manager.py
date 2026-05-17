"""
ui_manager.py — UIManager class
=================================
Owns and renders every UI element:
  - Layout zones (monitor frame, control panel, decision panel)
  - Video slider
  - Control buttons (Play/Pause, Rewind, Zoom, Line-Draw)
  - Decision buttons (Red Card, Penalty, Offside, No Foul)
  - Overlays (decision recorded banner, tool hints)
"""

from __future__ import annotations
import pygame
from button import Button

# ─── Colour tokens ────────────────────────────────────────────────────────────
BG_DARK         = (10,  15,  25)
PANEL_BG        = (18,  25,  40)
PANEL_BORDER    = (40,  60, 100)
ACCENT_BLUE     = (60, 130, 255)
ACCENT_GREEN    = (50, 200, 100)
ACCENT_RED      = (220,  55,  55)
ACCENT_YELLOW   = (240, 195,  40)
ACCENT_ORANGE   = (230, 120,  30)
TEXT_PRIMARY    = (220, 235, 255)
TEXT_SECONDARY  = (120, 140, 175)
SLIDER_TRACK    = (30,  45,  70)
SLIDER_FILL     = (60, 130, 255)
SLIDER_THUMB    = (200, 220, 255)


class UIManager:
    """
    Manages all UI rendering and interaction.

    Exposes:
        .handle_event(event) → dict | None   (action dict on interaction)
        .draw(surface, video_surface, draw_overlay_fn)
        .set_frame_progress(0.0 – 1.0)       (sync slider to video)
        .set_tool(tool_name)                  (set active tool)
        .show_decision_overlay(text)
        .monitor_rect                         (pygame.Rect, for hit testing)
    """

    LAYOUT = {
        "window_w": 1280,
        "window_h": 780,
        "monitor_x": 30,
        "monitor_y": 30,
        "monitor_w": 860,
        "monitor_h": 520,
        "control_y_offset": 560,   # below monitor
        "decision_x": 920,         # right column
    }

    def __init__(self, surface: pygame.Surface) -> None:
        self.surface = surface
        W = self.LAYOUT
        self._active_tool: str = "none"   # "zoom" | "line" | "none"
        self._overlay_text: str = ""
        self._overlay_timer: int = 0      # frames remaining to show overlay
        self._frame_progress: float = 0.0
        self._slider_dragging: bool = False
        self._is_playing: bool = False

        # ── Compute rects ────────────────────────────────────────
        self.monitor_rect = pygame.Rect(
            W["monitor_x"], W["monitor_y"], W["monitor_w"], W["monitor_h"])

        control_y = W["monitor_y"] + W["monitor_h"] + 20
        slider_rect = pygame.Rect(W["monitor_x"], control_y, W["monitor_w"], 14)
        self._slider_rect = slider_rect

        btn_y = control_y + 30
        dec_x = W["decision_x"]
        dec_y = W["monitor_y"]

        # ── Control buttons ──────────────────────────────────────
        self.btn_play = Button(
            (W["monitor_x"], btn_y, 110, 40), "▶  Play",
            color=(25, 100, 50), icon="")
        self.btn_pause = Button(
            (W["monitor_x"] + 120, btn_y, 110, 40), "⏸  Pause",
            color=(25, 60, 100), icon="")
        self.btn_rewind = Button(
            (W["monitor_x"] + 240, btn_y, 110, 40), "⏮  Rewind",
            color=(60, 40, 20), icon="")

        # ── Tool buttons ─────────────────────────────────────────
        self.btn_zoom = Button(
            (W["monitor_x"] + 370, btn_y, 120, 40), "🔍 Zoom",
            color=(40, 30, 80), icon="")
        self.btn_line = Button(
            (W["monitor_x"] + 500, btn_y, 130, 40), "📏 Draw Line",
            color=(40, 30, 80), icon="")
        self.btn_reset_tools = Button(
            (W["monitor_x"] + 640, btn_y, 110, 40), "✕ Clear",
            color=(60, 25, 25), icon="")

        # ── Decision buttons ─────────────────────────────────────
        dw, dh, dgap = 310, 68, 14
        self.decision_buttons = [
            Button((dec_x, dec_y + i * (dh + dgap), dw, dh), label,
                   color=color, font_size=17, border_radius=14, icon=icon)
            for i, (label, color, icon) in enumerate([
                ("Possible Red Card",  (160, 30, 30),  "🟥"),
                ("Possible Penalty",   (160, 90, 10),  "🟧"),
                ("Offside",            (140, 120, 10), "🟨"),
                ("No Foul",            (20,  110, 50), "🟩"),
            ])
        ]

        # ── Fonts ────────────────────────────────────────────────
        self._font_title  = pygame.font.SysFont("segoeui", 22, bold=True)
        self._font_label  = pygame.font.SysFont("segoeui", 15)
        self._font_hint   = pygame.font.SysFont("segoeui", 13)
        self._font_overlay = pygame.font.SysFont("segoeui", 30, bold=True)
        self._font_big    = pygame.font.SysFont("segoeui", 42, bold=True)

        self._all_buttons: list[Button] = [
            self.btn_play, self.btn_pause, self.btn_rewind,
            self.btn_zoom, self.btn_line, self.btn_reset_tools,
            *self.decision_buttons,
        ]

    # ──────────────────────────────────────────────────────────────────
    # Public setters
    # ──────────────────────────────────────────────────────────────────

    def set_frame_progress(self, progress: float) -> None:
        self._frame_progress = max(0.0, min(1.0, progress))

    def set_is_playing(self, val: bool) -> None:
        self._is_playing = val

    def set_tool(self, tool: str) -> None:
        self._active_tool = tool

    def show_decision_overlay(self, text: str, duration: int = 180) -> None:
        self._overlay_text = text
        self._overlay_timer = duration

    # ──────────────────────────────────────────────────────────────────
    # Event handling
    # ──────────────────────────────────────────────────────────────────

    def handle_event(self, event: pygame.event.Event) -> dict | None:
        """
        Processes events for all UI elements.
        Returns an action dict, e.g. {"action": "play"}, or None.
        """
        # ── Slider drag ──────────────────────────────────────────
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._slider_rect.collidepoint(event.pos):
                self._slider_dragging = True

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self._slider_dragging = False

        if event.type == pygame.MOUSEMOTION and self._slider_dragging:
            ratio = (event.pos[0] - self._slider_rect.x) / self._slider_rect.w
            ratio = max(0.0, min(1.0, ratio))
            self._frame_progress = ratio
            return {"action": "seek", "ratio": ratio}

        # ── Control buttons ──────────────────────────────────────
        if self.btn_play.handle_event(event):
            return {"action": "play"}
        if self.btn_pause.handle_event(event):
            return {"action": "pause"}
        if self.btn_rewind.handle_event(event):
            return {"action": "rewind"}
        if self.btn_zoom.handle_event(event):
            return {"action": "tool", "tool": "zoom"}
        if self.btn_line.handle_event(event):
            return {"action": "tool", "tool": "line"}
        if self.btn_reset_tools.handle_event(event):
            return {"action": "tool", "tool": "none"}

        # ── Decision buttons ─────────────────────────────────────
        labels = ["Possible Red Card", "Possible Penalty", "Offside", "No Foul"]
        for btn, label in zip(self.decision_buttons, labels):
            if btn.handle_event(event):
                return {"action": "decision", "label": label}

        return None

    # ──────────────────────────────────────────────────────────────────
    # Draw
    # ──────────────────────────────────────────────────────────────────

    def draw(self, surface: pygame.Surface,
             video_surface: pygame.Surface | None,
             draw_overlay_fn=None) -> None:
        """
        Render the full UI each frame.
        draw_overlay_fn(surface, monitor_rect) draws lines/zoom on top.
        """
        surface.fill(BG_DARK)
        self._draw_scanline_bg(surface)
        self._draw_header(surface)
        self._draw_monitor(surface, video_surface)
        if draw_overlay_fn:
            draw_overlay_fn(surface, self.monitor_rect)
        self._draw_slider(surface)
        self._draw_control_buttons(surface)
        self._draw_decision_panel(surface)
        self._draw_tool_hint(surface)
        self._draw_overlay_banner(surface)
        if self._overlay_timer > 0:
            self._overlay_timer -= 1

    # ──────────────────────────────────────────────────────────────────
    # Private draw helpers
    # ──────────────────────────────────────────────────────────────────

    def _draw_scanline_bg(self, surface: pygame.Surface) -> None:
        """Subtle horizontal scanline pattern for VOR room atmosphere."""
        for y in range(0, surface.get_height(), 4):
            pygame.draw.line(surface, (14, 20, 32),
                             (0, y), (surface.get_width(), y))

    def _draw_header(self, surface: pygame.Surface) -> None:
        W = self.LAYOUT
        # VAR title bar
        bar = pygame.Rect(0, 0, W["window_w"], 26)
        pygame.draw.rect(surface, (12, 18, 35), bar)

        title = self._font_label.render(
            "  ⚽  VAR — Video Assistant Referee Simulator  |  Computer Graphics Final Project",
            True, TEXT_SECONDARY)
        surface.blit(title, (8, 4))

        # Status indicator
        status = "● LIVE REVIEW" if self._is_playing else "⏸ PAUSED"
        color  = ACCENT_GREEN if self._is_playing else ACCENT_YELLOW
        status_surf = self._font_label.render(status, True, color)
        surface.blit(status_surf, (W["window_w"] - status_surf.get_width() - 12, 4))

    def _draw_monitor(self, surface: pygame.Surface,
                      video_surface: pygame.Surface | None) -> None:
        """Render the main video monitor with glowing border."""
        mr = self.monitor_rect

        # Glow effect — draw progressively darker rects outward
        for i in range(6, 0, -1):
            glow_rect = mr.inflate(i * 2, i * 2)
            alpha_surf = pygame.Surface(glow_rect.size, pygame.SRCALPHA)
            alpha_surf.fill((60, 130, 255, max(5, 25 - i * 4)))
            surface.blit(alpha_surf, glow_rect.topleft)

        # Monitor fill
        pygame.draw.rect(surface, (5, 8, 14), mr, border_radius=4)

        if video_surface:
            surface.blit(video_surface, mr.topleft)
        else:
            # Placeholder
            pygame.draw.rect(surface, (15, 20, 35), mr)
            msg = self._font_title.render("Loading video...", True, TEXT_SECONDARY)
            surface.blit(msg, msg.get_rect(center=mr.center))

        # Border
        pygame.draw.rect(surface, PANEL_BORDER, mr, width=2, border_radius=4)

        # Corner accents (decorative)
        size = 12
        for cx, cy in [(mr.x, mr.y), (mr.right, mr.y),
                       (mr.x, mr.bottom), (mr.right, mr.bottom)]:
            pygame.draw.rect(surface, ACCENT_BLUE,
                             (cx - size // 2, cy - size // 2, size, size), 2)

    def _draw_slider(self, surface: pygame.Surface) -> None:
        sr = self._slider_rect

        # Track background
        track_rect = pygame.Rect(sr.x, sr.y + sr.h // 2 - 3, sr.w, 6)
        pygame.draw.rect(surface, SLIDER_TRACK, track_rect, border_radius=3)

        # Fill (progress)
        fill_w = int(track_rect.w * self._frame_progress)
        if fill_w > 0:
            fill_rect = pygame.Rect(track_rect.x, track_rect.y, fill_w, track_rect.h)
            pygame.draw.rect(surface, SLIDER_FILL, fill_rect, border_radius=3)

        # Thumb
        thumb_x = sr.x + fill_w
        thumb_y = sr.y + sr.h // 2
        pygame.draw.circle(surface, SLIDER_THUMB, (thumb_x, thumb_y), 7)
        pygame.draw.circle(surface, ACCENT_BLUE,  (thumb_x, thumb_y), 7, 2)

        # Label
        label = self._font_hint.render("◀ Scrub timeline ▶", True, TEXT_SECONDARY)
        surface.blit(label, (sr.x, sr.y - 16))

    def _draw_control_buttons(self, surface: pygame.Surface) -> None:
        for btn in [self.btn_play, self.btn_pause, self.btn_rewind,
                    self.btn_zoom, self.btn_line, self.btn_reset_tools]:
            btn.draw(surface)

        # Active tool highlight
        tool_map = {"zoom": self.btn_zoom, "line": self.btn_line}
        if self._active_tool in tool_map:
            btn = tool_map[self._active_tool]
            draw_r = btn.base_rect.inflate(4, 4)
            pygame.draw.rect(surface, ACCENT_BLUE, draw_r, width=2, border_radius=12)

    def _draw_decision_panel(self, surface: pygame.Surface) -> None:
        W = self.LAYOUT
        dec_x = W["decision_x"]
        panel_rect = pygame.Rect(dec_x - 10, W["monitor_y"] - 10, 340, 560)

        # Panel background
        panel_surf = pygame.Surface(panel_rect.size, pygame.SRCALPHA)
        panel_surf.fill((18, 25, 40, 210))
        surface.blit(panel_surf, panel_rect.topleft)
        pygame.draw.rect(surface, PANEL_BORDER, panel_rect, width=1, border_radius=8)

        # Header
        title = self._font_title.render("⚖  REFEREE DECISION", True, TEXT_PRIMARY)
        surface.blit(title, (dec_x, W["monitor_y"] + 5))

        sep_y = W["monitor_y"] + 32
        pygame.draw.line(surface, PANEL_BORDER,
                         (dec_x - 8, sep_y), (dec_x + 328, sep_y))

        # Sub-label
        sub = self._font_hint.render("Select your ruling after review:", True, TEXT_SECONDARY)
        surface.blit(sub, (dec_x, sep_y + 6))

        # Draw buttons (offset y to clear header)
        for i, btn in enumerate(self.decision_buttons):
            orig_y = btn.base_rect.y
            btn.base_rect.y = sep_y + 28 + i * (btn.base_rect.h + 14)
            btn.draw(surface)
            btn.base_rect.y = orig_y

        # Level info box
        info_y = sep_y + 28 + len(self.decision_buttons) * 82 + 10
        info_rect = pygame.Rect(dec_x - 4, info_y, 322, 65)
        pygame.draw.rect(surface, (20, 30, 50), info_rect, border_radius=6)
        pygame.draw.rect(surface, PANEL_BORDER, info_rect, width=1, border_radius=6)
        info1 = self._font_label.render("Match: Premier League — Round 28", True, TEXT_SECONDARY)
        info2 = self._font_hint.render("Incident: Possible foul in penalty area", True, TEXT_SECONDARY)
        surface.blit(info1, (dec_x + 4, info_y + 8))
        surface.blit(info2, (dec_x + 4, info_y + 30))

    def _draw_tool_hint(self, surface: pygame.Surface) -> None:
        hints = {
            "zoom": "ZOOM ACTIVE — Click & drag on monitor to define zoom region",
            "line": "LINE DRAW — Click point A then point B on the monitor",
            "none": "No tool active — Select Zoom or Draw Line to inspect",
        }
        text = hints.get(self._active_tool, "")
        color = ACCENT_BLUE if self._active_tool != "none" else TEXT_SECONDARY
        hint_surf = self._font_hint.render(text, True, color)
        y = self.LAYOUT["monitor_y"] + self.LAYOUT["monitor_h"] + 8
        surface.blit(hint_surf, (self.LAYOUT["monitor_x"], y))

    def _draw_overlay_banner(self, surface: pygame.Surface) -> None:
        if self._overlay_timer <= 0 or not self._overlay_text:
            return
        alpha = min(255, self._overlay_timer * 8)

        # Semi-transparent dark backdrop
        banner = pygame.Surface((self.LAYOUT["window_w"], 90), pygame.SRCALPHA)
        banner.fill((0, 0, 0, min(180, alpha)))
        surface.blit(banner, (0, self.LAYOUT["window_h"] // 2 - 45))

        # "DECISION RECORDED" label
        label = self._font_big.render("✅  DECISION RECORDED", True,
                                      (*ACCENT_GREEN, alpha))
        surface.blit(label, label.get_rect(
            center=(self.LAYOUT["window_w"] // 2, self.LAYOUT["window_h"] // 2 - 16)))

        # Decision text
        dec = self._font_overlay.render(f"« {self._overlay_text} »", True,
                                        (*TEXT_PRIMARY, alpha))
        surface.blit(dec, dec.get_rect(
            center=(self.LAYOUT["window_w"] // 2, self.LAYOUT["window_h"] // 2 + 22)))
