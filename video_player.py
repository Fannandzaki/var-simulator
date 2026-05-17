"""
video_player.py — VideoPlayer class
=====================================
Wraps cv2.VideoCapture to provide frame-by-frame access and
slider-based scrubbing, then converts frames to pygame Surfaces
via the graphics module.
"""

from __future__ import annotations
import os
import numpy as np
import cv2
import pygame
from graphics import bgr_array_to_surface


# ---------------------------------------------------------------------------
# Synthetic video generator (fallback when no real .mp4 exists)
# ---------------------------------------------------------------------------

def _generate_synthetic_frames(n_frames: int = 120,
                                w: int = 640, h: int = 360) -> list[np.ndarray]:
    """
    Produce animated gradient BGR frames as a stand-in for a real video.
    Each frame is a smooth animated gradient with a moving circle overlay.
    """
    frames = []
    for i in range(n_frames):
        t = i / n_frames                           # 0 → 1 progress
        img = np.zeros((h, w, 3), dtype=np.uint8)

        # Animated horizontal gradient
        for x in range(w):
            ratio = x / w
            b = int(40 + 80 * ratio + 60 * np.sin(2 * np.pi * t))
            g = int(20 + 40 * t)
            r = int(60 * ratio)
            img[:, x] = [np.clip(b, 0, 255), np.clip(g, 0, 255), np.clip(r, 0, 255)]

        # Moving circle (simulates ball / player)
        cx = int(w * t)
        cy = h // 2
        cv2.circle(img, (cx, cy), 18, (255, 255, 255), -1)
        cv2.circle(img, (cx, cy), 18, (0, 0, 0), 2)

        # Frame number text
        cv2.putText(img, f"SYNTHETIC FRAME {i+1}/{n_frames}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 200), 1)
        cv2.putText(img, "Place real .mp4 in assets/", (10, h - 12),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (160, 160, 160), 1)
        frames.append(img)
    return frames


# ---------------------------------------------------------------------------
# VideoPlayer
# ---------------------------------------------------------------------------

class VideoPlayer:
    """
    Loads and plays back a video file frame-by-frame inside pygame.

    Public API:
        .get_surface(target_size)   → pygame.Surface for current frame
        .advance()                  → move to next frame (call each tick)
        .seek(frame_index)          → jump to a specific frame
        .toggle_play_pause()
        .rewind()
        .current_frame_index        → int (for slider sync)
        .total_frames               → int
        .is_playing                 → bool
    """

    def __init__(self, video_path: str) -> None:
        self.video_path = video_path
        self.is_playing: bool = False
        self.current_frame_index: int = 0
        self._synthetic: bool = False
        self._synthetic_frames: list[np.ndarray] = []
        self._cap: cv2.VideoCapture | None = None
        self.total_frames: int = 0
        self._cached_surface: pygame.Surface | None = None
        self._cache_index: int = -1

        self._open_video()

    # ------------------------------------------------------------------
    def _open_video(self) -> None:
        if os.path.isfile(self.video_path):
            self._cap = cv2.VideoCapture(self.video_path)
            self.total_frames = int(self._cap.get(cv2.CAP_PROP_FRAME_COUNT))
            if self.total_frames <= 0:
                self._cap.release()
                self._cap = None
        
        if self._cap is None:
            # Fall back to synthetic frames
            print(f"[VideoPlayer] '{self.video_path}' not found — using synthetic frames.")
            self._synthetic = True
            self._synthetic_frames = _generate_synthetic_frames()
            self.total_frames = len(self._synthetic_frames)

    # ------------------------------------------------------------------
    def _read_frame(self, index: int) -> np.ndarray:
        """Return BGR numpy array for a given frame index."""
        if self._synthetic:
            idx = index % self.total_frames
            return self._synthetic_frames[idx]

        # Seek the OpenCV capture to the requested frame
        self._cap.set(cv2.CAP_PROP_POS_FRAMES, index)
        ret, frame = self._cap.read()
        if not ret:
            # End of video — return last frame if available
            return np.zeros((360, 640, 3), dtype=np.uint8)
        return frame

    # ------------------------------------------------------------------
    def get_surface(self, target_size: tuple[int, int]) -> pygame.Surface:
        """Convert the current frame to a pygame Surface at target_size."""
        if self._cache_index != self.current_frame_index:
            bgr = self._read_frame(self.current_frame_index)
            self._cached_surface = bgr_array_to_surface(bgr, target_size)
            self._cache_index = self.current_frame_index
        elif self._cached_surface and self._cached_surface.get_size() != target_size:
            self._cached_surface = pygame.transform.scale(self._cached_surface, target_size)
        return self._cached_surface

    def get_raw_frame(self) -> np.ndarray:
        """Return current frame as BGR numpy array (for zoom sub-region)."""
        return self._read_frame(self.current_frame_index)

    # ------------------------------------------------------------------
    def advance(self) -> None:
        """Advance one frame forward (call once per game tick)."""
        if self.is_playing:
            self.current_frame_index += 1
            if self.current_frame_index >= self.total_frames:
                self.current_frame_index = 0   # loop

    def seek(self, frame_index: int) -> None:
        """Jump directly to frame_index (used by slider scrubbing)."""
        self.current_frame_index = max(0, min(frame_index, self.total_frames - 1))

    def toggle_play_pause(self) -> None:
        self.is_playing = not self.is_playing

    def rewind(self) -> None:
        self.current_frame_index = 0
        self.is_playing = False

    def __del__(self):
        if self._cap is not None:
            self._cap.release()
