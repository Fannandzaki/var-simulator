"""
graphics.py — Computer Graphics primitives
==========================================
Demonstrates two core Grafkom (Computer Graphics) concepts:

  1. BRESENHAM'S LINE ALGORITHM — rasterize a line between two integer
     pixel coordinates without floating-point arithmetic.

  2. SCALING / ZOOM via a 2D Transformation Matrix — map a sub-region of the
     source image onto the full display surface, effectively applying:
         [ sx  0  tx ]
         [  0 sy  ty ]
         [  0  0   1 ]
     where sx = W / crop_w  and  sy = H / crop_h  (uniform scale factors).
"""

from __future__ import annotations
import pygame
import numpy as np


# ---------------------------------------------------------------------------
# Bresenham's Line Drawing
# ---------------------------------------------------------------------------

def bresenham_line(surface: pygame.Surface, p1: tuple[int, int],
                   p2: tuple[int, int], color: tuple[int, int, int],
                   thickness: int = 2) -> None:
    """
    Draw a straight line on *surface* from p1 to p2 using
    Bresenham's incremental algorithm.

    Grafkom note:
      - We track the cumulative 'error' term (2*dy - dx) to decide
        whether to step diagonally or horizontally each iteration.
      - No float arithmetic is needed — all operations are integer adds.
    """
    x0, y0 = p1
    x1, y1 = p2

    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1   # step direction X
    sy = 1 if y0 < y1 else -1   # step direction Y

    # Choose driving axis (the longer dimension)
    if dx >= dy:
        err = 2 * dy - dx
        while x0 != x1:
            # Draw a small filled circle for thickness
            pygame.draw.circle(surface, color, (x0, y0), thickness)
            if err >= 0:
                y0 += sy
                err -= 2 * dx
            err += 2 * dy
            x0 += sx
    else:
        err = 2 * dx - dy
        while y0 != y1:
            pygame.draw.circle(surface, color, (x0, y0), thickness)
            if err >= 0:
                x0 += sx
                err -= 2 * dy
            err += 2 * dx
            y0 += sy

    # Draw the endpoint
    pygame.draw.circle(surface, color, (x1, y1), thickness)


# ---------------------------------------------------------------------------
# Zoom / Scaling via 2D Transformation Matrix
# ---------------------------------------------------------------------------

def apply_zoom(frame_surface: pygame.Surface,
               zoom_rect: pygame.Rect,
               dest_size: tuple[int, int]) -> pygame.Surface:
    """
    Zoom into the sub-region *zoom_rect* of *frame_surface* and scale it
    to *dest_size*, implementing the 2D scaling transformation matrix:

        [sx  0  0]        sx = dest_w / zoom_rect.w
        [ 0 sy  0]   ,    sy = dest_h / zoom_rect.h
        [ 0  0  1]

    Any pixel (x, y) inside zoom_rect maps to output pixel:
        x' = (x - zoom_rect.x) * sx
        y' = (y - zoom_rect.y) * sy

    pygame.transform.scale performs this bilinear-style stretch
    (nearest-neighbour by default in SDL2, configurable).
    """
    # Clamp zoom_rect to the frame boundaries
    clamped = zoom_rect.clip(frame_surface.get_rect())
    if clamped.width <= 0 or clamped.height <= 0:
        return pygame.transform.scale(frame_surface, dest_size)

    # Extract the sub-surface (the region we're zooming into)
    sub = frame_surface.subsurface(clamped)

    # Apply the scaling matrix → stretch to destination size
    zoomed = pygame.transform.scale(sub, dest_size)
    return zoomed


# ---------------------------------------------------------------------------
# Helper: numpy BGR array → pygame Surface (for OpenCV frames)
# ---------------------------------------------------------------------------

def bgr_array_to_surface(bgr_array: np.ndarray,
                          target_size: tuple[int, int]) -> pygame.Surface:
    """
    Convert an OpenCV BGR numpy array to a pygame RGB Surface and resize it.

    Steps:
      1. Flip channel order  BGR → RGB  (in-place view, zero-copy)
      2. Wrap in a pygame Surface using the shared buffer
      3. Scale to target_size with pygame.transform.scale
    """
    rgb = bgr_array[:, :, ::-1]               # BGR → RGB channel swap
    h, w = rgb.shape[:2]
    surf = pygame.Surface((w, h))
    pygame.surfarray.blit_array(surf, rgb.swapaxes(0, 1))  # HWC → WHC
    if (w, h) != target_size:
        surf = pygame.transform.scale(surf, target_size)
    return surf
