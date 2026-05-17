"""
game_manager.py — GameManager class
======================================
Orchestrates the game loop, level data, tool interactions, and ties
VideoPlayer, UIManager, and graphics primitives together.

Level data structure:
    {
        "id"                : int,
        "title"             : str,
        "video_path"        : str,
        "correct_decision"  : str,   # matches a decision button label
        "requires_offside"  : bool,  # hint: offside line tool needed
        "description"       : str,
    }
"""

from __future__ import annotations
import sys
import pygame
from video_player import VideoPlayer
from ui_manager   import UIManager
from graphics     import bresenham_line, apply_zoom, bgr_array_to_surface


# ---------------------------------------------------------------------------
# Level definitions — extend freely
# ---------------------------------------------------------------------------

LEVELS: list[dict] = [
    {
        "id": 1,
        "title": "Penalty Box Incident",
        "video_path": "assets/level1_foul.mp4",
        "correct_decision": "Possible Penalty",
        "requires_offside": False,
        "description": "Player goes down in the penalty area. Check if contact was made.",
    },
    {
        "id": 2,
        "title": "Striker's Last Touch",
        "video_path": "assets/level2_offside.mp4",
        "correct_decision": "Offside",
        "requires_offside": True,
        "description": "Draw the offside line to determine if the attacker was level.",
    },
    {
        "id": 3,
        "title": "Violent Conduct",
        "video_path": "assets/level3_redcard.mp4",
        "correct_decision": "Possible Red Card",
        "requires_offside": False,
        "description": "Use zoom to inspect the elbow contact in close replay.",
    },
]


# ---------------------------------------------------------------------------
# GameManager
# ---------------------------------------------------------------------------

class GameManager:
    """
    Top-level controller.

    Responsibilities:
      - Maintain game state (current level, active tool, drawn lines, zoom)
      - Drive the pygame main loop at a target FPS
      - Route UI events to VideoPlayer / graphics tools
      - Render everything via UIManager
    """

    TARGET_FPS   = 30
    WINDOW_W     = 1280
    WINDOW_H     = 780

    def __init__(self) -> None:
        self.screen = pygame.display.set_mode((self.WINDOW_W, self.WINDOW_H))
        pygame.display.set_caption("VAR Simulator — Computer Graphics Project")
        self.clock = pygame.time.Clock()

        # ── Level state ───────────────────────────────────────────
        self._level_index: int = 0
        self._current_level: dict = LEVELS[self._level_index]

        # ── Subsystems ────────────────────────────────────────────
        self._video  = VideoPlayer(self._current_level["video_path"])
        self._ui     = UIManager(self.screen)

        # ── Tool state ────────────────────────────────────────────
        self._active_tool: str = "none"   # "zoom" | "line" | "none"

        # Bresenham line tool
        self._line_points: list[tuple[int, int]] = []  # up to 2 points
        self._drawn_lines: list[tuple[tuple, tuple]] = []  # committed lines

        # Zoom tool
        self._zoom_start: tuple[int, int] | None = None
        self._zoom_rect:  pygame.Rect     | None = None
        self._is_zooming: bool = False
        self._zoomed_surface: pygame.Surface | None = None

        # ── Decision overlay flag ─────────────────────────────────
        self._decision_frozen: bool = False
        self._freeze_timer: int = 0    # frames to keep "frozen" text

        print(f"\n{'='*60}")
        print(f"  VAR SIMULATOR — Level {self._current_level['id']}")
        print(f"  {self._current_level['title']}")
        print(f"  {self._current_level['description']}")
        print(f"{'='*60}\n")

    # ──────────────────────────────────────────────────────────────
    # Main loop
    # ──────────────────────────────────────────────────────────────

    def run(self) -> None:
        """Blocking game loop."""
        running = True
        while running:
            # ── Events ───────────────────────────────────────────
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        self._video.toggle_play_pause()
                        self._ui.set_is_playing(self._video.is_playing)
                    elif event.key == pygame.K_r:
                        self._reset_tools()

                # ── Delegate to UIManager ─────────────────────────
                action = self._ui.handle_event(event)
                if action:
                    self._handle_ui_action(action)

                # ── Tool mouse interactions on monitor ────────────
                if not self._decision_frozen:
                    self._handle_tool_event(event)

            # ── Tick video ────────────────────────────────────────
            if not self._decision_frozen:
                self._video.advance()

            # Sync slider
            if self._video.total_frames > 0:
                progress = self._video.current_frame_index / self._video.total_frames
                self._ui.set_frame_progress(progress)

            # ── Freeze counter ────────────────────────────────────
            if self._decision_frozen:
                self._freeze_timer -= 1
                if self._freeze_timer <= 0:
                    self._decision_frozen = False

            # ── Render ────────────────────────────────────────────
            video_surf = self._get_video_surface()
            self._ui.draw(self.screen, video_surf, self._draw_tool_overlay)
            pygame.display.flip()
            self.clock.tick(self.TARGET_FPS)

    # ──────────────────────────────────────────────────────────────
    # UI action routing
    # ──────────────────────────────────────────────────────────────

    def _handle_ui_action(self, action: dict) -> None:
        a = action["action"]

        if a == "play":
            self._video.is_playing = True
            self._ui.set_is_playing(True)

        elif a == "pause":
            self._video.is_playing = False
            self._ui.set_is_playing(False)

        elif a == "rewind":
            self._video.rewind()
            self._ui.set_is_playing(False)
            self._reset_tools()

        elif a == "seek":
            frame = int(action["ratio"] * self._video.total_frames)
            self._video.seek(frame)

        elif a == "tool":
            self._set_tool(action["tool"])

        elif a == "decision":
            self._record_decision(action["label"])

    # ──────────────────────────────────────────────────────────────
    # Tool management
    # ──────────────────────────────────────────────────────────────

    def _set_tool(self, tool: str) -> None:
        self._active_tool = tool
        self._ui.set_tool(tool)
        # Clear pending partial operations when switching tools
        self._line_points.clear()
        self._zoom_start = None
        self._zoom_rect  = None
        self._is_zooming = False
        self._zoomed_surface = None

    def _reset_tools(self) -> None:
        self._drawn_lines.clear()
        self._set_tool("none")

    def _handle_tool_event(self, event: pygame.event.Event) -> None:
        monitor = self._ui.monitor_rect

        if self._active_tool == "line":
            self._handle_line_tool(event, monitor)

        elif self._active_tool == "zoom":
            self._handle_zoom_tool(event, monitor)

    # ── Line tool ─────────────────────────────────────────────────

    def _handle_line_tool(self, event: pygame.event.Event,
                           monitor: pygame.Rect) -> None:
        """
        Collects two click points on the monitor then commits a Bresenham line.
        Points are stored in monitor-local coordinates.
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if monitor.collidepoint(event.pos):
                # Convert to monitor-local coords
                local = (event.pos[0] - monitor.x, event.pos[1] - monitor.y)
                self._line_points.append(local)

                if len(self._line_points) == 2:
                    # Commit line; keep for rendering
                    self._drawn_lines.append(
                        (self._line_points[0], self._line_points[1]))
                    print(f"[Line Tool] Bresenham line drawn: "
                          f"{self._line_points[0]} → {self._line_points[1]}")
                    self._line_points.clear()

    # ── Zoom tool ─────────────────────────────────────────────────

    def _handle_zoom_tool(self, event: pygame.event.Event,
                           monitor: pygame.Rect) -> None:
        """
        Click-and-drag to define a zoom rectangle (crop region).
        On MOUSEBUTTONUP the zoomed surface is computed via apply_zoom().
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if monitor.collidepoint(event.pos):
                self._zoom_start = event.pos
                self._is_zooming = True
                self._zoomed_surface = None
                self._zoom_rect = None

        elif event.type == pygame.MOUSEMOTION and self._is_zooming:
            if self._zoom_start:
                x0, y0 = self._zoom_start
                x1, y1 = event.pos
                # Build rect from two corners (allow any drag direction)
                self._zoom_rect = pygame.Rect(
                    min(x0, x1), min(y0, y1),
                    abs(x1 - x0), abs(y1 - y0))

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self._is_zooming and self._zoom_rect:
                self._is_zooming = False
                # Convert drag rect to video-frame local coords
                local_rect = self._zoom_rect.move(-monitor.x, -monitor.y)
                if local_rect.w > 10 and local_rect.h > 10:
                    # Scale local_rect from monitor-display-size to video-frame-size
                    video_surf = self._video.get_surface(monitor.size)
                    vw, vh = video_surf.get_size()
                    sx = vw / monitor.w
                    sy = vh / monitor.h
                    frame_rect = pygame.Rect(
                        int(local_rect.x * sx), int(local_rect.y * sy),
                        int(local_rect.w * sx), int(local_rect.h * sy))

                    raw_frame  = self._video.get_raw_frame()
                    raw_surf   = bgr_array_to_surface(raw_frame, (vw, vh))
                    self._zoomed_surface = apply_zoom(raw_surf, frame_rect,
                                                      monitor.size)
                    print(f"[Zoom Tool] Scaling matrix applied: "
                          f"crop={frame_rect} → {monitor.size}")
                self._zoom_rect = None

    # ──────────────────────────────────────────────────────────────
    # Video surface selection (normal or zoomed)
    # ──────────────────────────────────────────────────────────────

    def _get_video_surface(self) -> pygame.Surface:
        monitor_size = self._ui.monitor_rect.size
        if self._zoomed_surface:
            return self._zoomed_surface
        return self._video.get_surface(monitor_size)

    # ──────────────────────────────────────────────────────────────
    # Tool overlay drawing (passed as callback to UIManager.draw)
    # ──────────────────────────────────────────────────────────────

    def _draw_tool_overlay(self, surface: pygame.Surface,
                            monitor_rect: pygame.Rect) -> None:
        """
        Render all Bresenham lines and the live zoom drag rect
        on top of the video monitor.
        """
        # Committed Bresenham lines
        for p1, p2 in self._drawn_lines:
            abs_p1 = (p1[0] + monitor_rect.x, p1[1] + monitor_rect.y)
            abs_p2 = (p2[0] + monitor_rect.x, p2[1] + monitor_rect.y)
            bresenham_line(surface, abs_p1, abs_p2, (255, 220, 0), thickness=2)
            # Endpoint markers
            pygame.draw.circle(surface, (255, 80, 80), abs_p1, 6)
            pygame.draw.circle(surface, (255, 80, 80), abs_p2, 6)

        # Pending first point (line tool)
        if self._active_tool == "line" and len(self._line_points) == 1:
            p = (self._line_points[0][0] + monitor_rect.x,
                 self._line_points[0][1] + monitor_rect.y)
            pygame.draw.circle(surface, (255, 200, 0), p, 6)
            # Rubber-band line to mouse
            mx, my = pygame.mouse.get_pos()
            if monitor_rect.collidepoint(mx, my):
                bresenham_line(surface, p, (mx, my), (200, 200, 80), thickness=1)

        # Live zoom drag rect
        if self._is_zooming and self._zoom_rect:
            drag_surf = pygame.Surface(self._zoom_rect.size, pygame.SRCALPHA)
            drag_surf.fill((60, 130, 255, 50))
            surface.blit(drag_surf, self._zoom_rect.topleft)
            pygame.draw.rect(surface, (60, 130, 255), self._zoom_rect, 2)

    # ──────────────────────────────────────────────────────────────
    # Decision recording
    # ──────────────────────────────────────────────────────────────

    def _record_decision(self, label: str) -> None:
        correct = self._current_level["correct_decision"]
        is_correct = label.lower() == correct.lower()

        print(f"\n{'='*60}")
        print(f"  📋 DECISION: {label}")
        print(f"  {'✅ CORRECT!' if is_correct else '❌ INCORRECT — Expected: ' + correct}")
        print(f"{'='*60}\n")

        overlay_text = f"{label}  {'✅' if is_correct else '❌'}"
        self._ui.show_decision_overlay(overlay_text, duration=210)

        self._decision_frozen = True
        self._freeze_timer    = 210   # ~7 seconds at 30 FPS
        self._video.is_playing = False
        self._ui.set_is_playing(False)
