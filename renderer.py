"""
renderer.py — Bresenham line drawing algorithm
"""
import pygame

def bresenham(surface: pygame.Surface, p1, p2, color, thickness=2):
    x0,y0 = int(p1[0]),int(p1[1])
    x1,y1 = int(p2[0]),int(p2[1])
    dx,dy  = abs(x1-x0),abs(y1-y0)
    sx     = 1 if x0<x1 else -1
    sy     = 1 if y0<y1 else -1
    if dx >= dy:
        err = 2*dy-dx
        while x0 != x1:
            pygame.draw.circle(surface,color,(x0,y0),thickness)
            if err>=0: y0+=sy; err-=2*dx
            err+=2*dy; x0+=sx
    else:
        err = 2*dx-dy
        while y0 != y1:
            pygame.draw.circle(surface,color,(x0,y0),thickness)
            if err>=0: x0+=sx; err-=2*dy
            err+=2*dx; y0+=sy
    pygame.draw.circle(surface,color,(x1,y1),thickness)
