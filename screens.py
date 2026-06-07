"""screens.py — VAR Simulator (Cartoon 3D VOR Room)"""
import os, random, math, pygame
from constants import *
from video_player import VideoPlayer
from renderer import bresenham

# ══════════════════════════════════════════════════════════════════════════════
#  UTILITY HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def txt(s, t, f, c, cx, cy):
    r = f.render(t, True, c)
    s.blit(r, r.get_rect(center=(cx, cy)))

def txt_left(s, t, f, c, x, cy):
    r = f.render(t, True, c)
    s.blit(r, (x, cy - r.get_height() // 2))

def box(s, r, fill, border=None, rad=6, bw=2):
    if fill is not None:
        pygame.draw.rect(s, fill, r, border_radius=rad)
    if border:
        pygame.draw.rect(s, border, r, bw, border_radius=rad)

def shadow_box(s, r, fill, border, rad=10, sh=5):
    sr = r.move(sh, sh)
    ds = pygame.Surface((sr.w, sr.h), pygame.SRCALPHA)
    pygame.draw.rect(ds, (0, 0, 0, 80), (0, 0, sr.w, sr.h), border_radius=rad)
    s.blit(ds, sr.topleft)
    box(s, r, fill, border, rad)

def scan(s, r):
    sl = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
    for y in range(0, r.h, 3):
        pygame.draw.line(sl, (0, 0, 0, 22), (0, y), (r.w, y))
    s.blit(sl, r.topleft)

def _poly_shadow(s, pts, ox=6, oy=8, alpha=70):
    """Draw a dark shadow polygon offset by (ox, oy)."""
    spts = [(x + ox, y + oy) for x, y in pts]
    sh = pygame.Surface((WIN_W, WIN_H), pygame.SRCALPHA)
    pygame.draw.polygon(sh, (0, 0, 0, alpha), spts)
    s.blit(sh, (0, 0))

# ══════════════════════════════════════════════════════════════════════════════
#  ROOM ENVIRONMENT
# ══════════════════════════════════════════════════════════════════════════════

def draw_room(s):
    """Draw the 3D cartoon room: wall + bookshelf + poster + desk."""
    W, H = WIN_W, WIN_H
    WALL_H = 345

    # Upper wall gradient bands
    pygame.draw.rect(s, WALL_DARK, (0, 0, W, 50))
    pygame.draw.rect(s, WALL_TEAL, (0, 50, W, WALL_H - 50))
    # Subtle wall highlight at top
    pygame.draw.rect(s, WALL_LIGHT, (0, 50, W, 6))

    # ── Bookshelf strip on left ───────────────────────────────────────────────
    shelf_x, shelf_y, shelf_w, shelf_h = 0, 55, 26, WALL_H - 80
    pygame.draw.rect(s, (35, 90, 100), (shelf_x, shelf_y, shelf_w, shelf_h))
    book_cols = [
        (195, 58, 52), (48, 118, 192), (192, 158, 42), (52, 168, 88),
        (155, 72, 192), (192, 108, 42), (42, 148, 148), (192, 52, 125),
        (88, 165, 55), (175, 88, 42),
    ]
    bh_book = 25
    for i, bc in enumerate(book_cols):
        by2 = shelf_y + 6 + i * (bh_book + 3)
        if by2 + bh_book > shelf_y + shelf_h: break
        pygame.draw.rect(s, bc, (shelf_x + 2, by2, shelf_w - 4, bh_book), border_radius=1)
        darker = tuple(max(0, c - 50) for c in bc)
        pygame.draw.rect(s, darker, (shelf_x + 2, by2, shelf_w - 4, bh_book), 1, border_radius=1)
        lighter = tuple(min(255, c + 40) for c in bc)
        pygame.draw.line(s, lighter, (shelf_x + 3, by2 + 2), (shelf_x + 3, by2 + bh_book - 3), 1)

    # ── Poster (right wall) ───────────────────────────────────────────────────
    px, py, pw, ph = W - 138, 58, 118, 148
    pygame.draw.rect(s, (242, 238, 218), (px, py, pw, ph), border_radius=4)
    pygame.draw.rect(s, (145, 132, 108), (px, py, pw, ph), 2, border_radius=4)
    pix, piy, piw, pih = px + 8, py + 12, pw - 16, ph - 32
    pygame.draw.rect(s, (50, 155, 50), (pix, piy, piw, pih))
    pygame.draw.rect(s, WHITE, (pix, piy, piw, pih), 1)
    pygame.draw.line(s, WHITE, (pix + piw // 2, piy), (pix + piw // 2, piy + pih), 1)
    pygame.draw.circle(s, WHITE, (pix + piw // 2, piy + pih // 2), pih // 5, 1)
    pygame.draw.rect(s, WHITE, (pix, piy + pih // 3, piw // 5, pih // 3), 1)
    pygame.draw.rect(s, WHITE, (pix + piw - piw // 5, piy + pih // 3, piw // 5, pih // 3), 1)
    try:
        lf = pygame.font.SysFont("couriernew,monospace", 9)
        lr = lf.render("TAKTIK VAR", True, (80, 60, 40))
        s.blit(lr, lr.get_rect(center=(px + pw // 2, py + ph - 12)))
    except: pass

    # ── Wall/desk divider ─────────────────────────────────────────────────────
    pygame.draw.line(s, DESK_SHADOW, (0, WALL_H), (W, WALL_H), 5)
    pygame.draw.line(s, (50, 115, 128), (0, WALL_H + 5), (W, WALL_H + 5), 2)

    # ── Desk surface (trapezoid for perspective) ──────────────────────────────
    margin = 55
    desk_pts = [
        (margin, WALL_H),
        (W - margin, WALL_H),
        (W, H),
        (0, H),
    ]
    pygame.draw.polygon(s, DESK_BLUE, desk_pts)

    # Front lip of desk (darker strip)
    lip_pts = [
        (margin,     WALL_H),
        (W - margin, WALL_H),
        (W - margin, WALL_H + 22),
        (margin,     WALL_H + 22),
    ]
    pygame.draw.polygon(s, DESK_FRONT, lip_pts)
    pygame.draw.line(s, DESK_SHADOW, (margin, WALL_H + 22), (W - margin, WALL_H + 22), 2)

    # Perspective grid lines on desk
    vx, vy = W // 2, WALL_H
    line_col = (82, 158, 172)
    for gx in range(0, W + 1, 110):
        pygame.draw.line(s, line_col, (gx, H), (vx, vy), 1)
    for gy in range(WALL_H + 30, H, 55):
        t = (gy - WALL_H) / (H - WALL_H)
        lx = int(margin * (1 - t))
        rx = W - lx
        pygame.draw.line(s, line_col, (lx, gy), (rx, gy), 1)


# ══════════════════════════════════════════════════════════════════════════════
#  3D CARTOON CRT — CENTRE (straight-on, largest)
# ══════════════════════════════════════════════════════════════════════════════

def draw_crt_3d(s, rect, inner_w, inner_h):
    """
    Draw chunky straight-on 3D CRT.  Returns inner screen Rect.
    """
    r = rect
    D = 20     # depth offset for back-face
    TOP = 16   # top face height
    SIDE = 18  # right face width

    # ── Drop shadow ───────────────────────────────────────────────────────────
    sh = pygame.Surface((r.w + 30, 22), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (0, 0, 0, 70), sh.get_rect())
    s.blit(sh, (r.x - 8, r.bottom + 4))

    # ── Back of CRT (bulge) ───────────────────────────────────────────────────
    back_pts = [
        (r.x + D,     r.y - TOP),
        (r.right + D, r.y - TOP),
        (r.right + D, r.bottom - TOP // 2),
        (r.right,     r.bottom),
        (r.x,         r.bottom),
        (r.x,         r.y),
    ]
    pygame.draw.polygon(s, MONITOR_BACK, back_pts)

    # ── Top face ──────────────────────────────────────────────────────────────
    top_pts = [
        (r.x,         r.y),
        (r.x + D,     r.y - TOP),
        (r.right + D, r.y - TOP),
        (r.right,     r.y),
    ]
    pygame.draw.polygon(s, MONITOR_LIGHT, top_pts)
    pygame.draw.polygon(s, MONITOR_SHADOW, top_pts, 1)

    # ── Right face ────────────────────────────────────────────────────────────
    right_pts = [
        (r.right,         r.y),
        (r.right + D,     r.y - TOP),
        (r.right + D,     r.bottom - TOP // 2),
        (r.right,         r.bottom),
    ]
    pygame.draw.polygon(s, MONITOR_SHADOW, right_pts)
    pygame.draw.polygon(s, tuple(max(0,c-25) for c in MONITOR_SHADOW), right_pts, 1)

    # ── Main front face ───────────────────────────────────────────────────────
    pygame.draw.rect(s, MONITOR_BEIGE, r, border_radius=16)
    # Bevel highlights
    pygame.draw.line(s, MONITOR_LIGHT, (r.x+10, r.y+5),    (r.right-10, r.y+5),    3)
    pygame.draw.line(s, MONITOR_LIGHT, (r.x+5,  r.y+10),   (r.x+5, r.bottom-10),   3)
    pygame.draw.line(s, MONITOR_SHADOW,(r.x+10, r.bottom-5),(r.right-10,r.bottom-5),3)
    pygame.draw.line(s, MONITOR_SHADOW,(r.right-5, r.y+10),(r.right-5, r.bottom-10),3)

    # ── Screen bezel & inner ──────────────────────────────────────────────────
    ix = r.centerx - inner_w // 2
    iy = r.y + 24
    inner = pygame.Rect(ix, iy, inner_w, inner_h)
    bz = inner.inflate(14, 14)
    pygame.draw.rect(s, BEZEL_DARK, bz, border_radius=10)
    pygame.draw.rect(s, (6, 12, 10), inner, border_radius=4)

    # ── Button row ────────────────────────────────────────────────────────────
    btn_y = r.bottom - 22
    pygame.draw.circle(s, (55, 200, 55), (r.x + 20, btn_y), 6)
    pygame.draw.circle(s, (110, 255, 110), (r.x + 20, btn_y), 3)
    for bx_off in [40, 58, 76, 94]:
        br = pygame.Rect(r.x + bx_off, btn_y - 5, 13, 9)
        pygame.draw.rect(s, MONITOR_SHADOW, br, border_radius=2)
        pygame.draw.rect(s, MONITOR_LIGHT, br.move(0, -1), 1, border_radius=2)
    try:
        bf = pygame.font.SysFont("couriernew,monospace", 9, bold=True)
        bl = bf.render("VARTECH", True, MONITOR_SHADOW)
        s.blit(bl, bl.get_rect(center=(r.centerx, r.bottom - 10)))
    except: pass

    return inner


# ══════════════════════════════════════════════════════════════════════════════
#  3D CARTOON CRT — ANGLED SIDE MONITORS (LEFT / RIGHT)
# ══════════════════════════════════════════════════════════════════════════════

def draw_crt_angled(s, rect, inner_w, inner_h, lean):
    """
    Draw a side CRT monitor with 3-quarter perspective tilt.

    lean = -1 → LEFT  monitor: LEFT outer side panel visible, screen faces INWARD (right)
    lean = +1 → RIGHT monitor: RIGHT outer side panel visible, screen faces INWARD (left)

    Returns the Rect of the inner screen area.
    """
    r = rect
    SK   = 22   # horizontal skew — subtle, matches reference angle
    VC   = 8    # vertical compression on far edge
    SD   = 22   # side-panel depth
    TD   = 18   # top-panel height
    BEV  = 3    # bevel thickness

    if lean == -1:
        # ── LEFT MONITOR: left outer side visible, screen faces right/inward ──
        # Left edge is the "near" edge (closer to viewer)
        # Right edge is the "far" edge (pushed back)
        face = [
            (r.x,          r.y),              # TL  near (left edge)
            (r.right - SK, r.y + VC),         # TR  far  (right edge pushed back)
            (r.right - SK, r.bottom - VC),    # BR  far
            (r.x,          r.bottom),         # BL  near
        ]
        # LEFT outer side panel (faces left wall)
        side = [
            (r.x,       r.y),
            (r.x - SD,  r.y - TD),
            (r.x - SD,  r.bottom - TD),
            (r.x,       r.bottom),
        ]
        # Top panel
        top_p = [
            (r.x,              r.y),
            (r.x - SD,         r.y - TD),
            (r.right - SK - SD, r.y + VC - TD),
            (r.right - SK,     r.y + VC),
        ]
        # Inner screen — padded inside the face polygon
        ix = r.x + 14
        iy = r.y + 20
        iw = (r.right - SK - 14) - ix
        ih = (r.bottom - VC - 18) - iy
        led_x    = r.x + 14
        btn_cy   = r.bottom - VC - 14
        brand_cx = r.x + (r.right - SK - r.x) // 2

    else:
        # ── RIGHT MONITOR: right outer side visible, screen faces left/inward ──
        face = [
            (r.x + SK,  r.y + VC),        # TL  far  (left edge pushed back)
            (r.right,   r.y),              # TR  near (right edge)
            (r.right,   r.bottom),         # BR  near
            (r.x + SK,  r.bottom - VC),   # BL  far
        ]
        # RIGHT outer side panel (faces right wall)
        side = [
            (r.right,      r.y),
            (r.right + SD, r.y - TD),
            (r.right + SD, r.bottom - TD),
            (r.right,      r.bottom),
        ]
        # Top panel
        top_p = [
            (r.x + SK,      r.y + VC),
            (r.x + SK + SD, r.y + VC - TD),
            (r.right + SD,  r.y - TD),
            (r.right,       r.y),
        ]
        ix = r.x + SK + 14
        iy = r.y + VC + 20
        iw = (r.right - 14) - ix
        ih = (r.bottom - VC - 18) - iy
        led_x    = r.x + SK + 14
        btn_cy   = r.bottom - VC - 14
        brand_cx = r.x + SK + (r.right - r.x - SK) // 2

    # ── Drop shadow ───────────────────────────────────────────────────────────
    extra = SD if lean == -1 else SD
    shw = pygame.Surface((r.w + extra + 30, 20), pygame.SRCALPHA)
    pygame.draw.ellipse(shw, (0, 0, 0, 65), shw.get_rect())
    sx_off = -8 if lean == +1 else -8
    s.blit(shw, (r.x + sx_off, r.bottom + 5))

    # ── Side panel (depth face) ───────────────────────────────────────────────
    _poly_shadow(s, side, 4, 6, 55)
    pygame.draw.polygon(s, MONITOR_SHADOW, side)
    # Rivets / vents on side
    sv_x = side[0][0] + (side[1][0] - side[0][0]) // 2
    for vi in range(3):
        vy = side[0][1] + (side[3][1] - side[0][1]) // 4 * (vi + 1)
        vy2 = (vy + (side[1][1] + (side[2][1]-side[1][1])//4*(vi+1))) // 2
        pygame.draw.circle(s, MONITOR_BACK, (sv_x, int(vy2)), 3)
    pygame.draw.polygon(s, tuple(max(0,c-30) for c in MONITOR_SHADOW), side, 1)

    # ── Top panel ─────────────────────────────────────────────────────────────
    pygame.draw.polygon(s, MONITOR_LIGHT, top_p)
    pygame.draw.polygon(s, MONITOR_SHADOW, top_p, 1)

    # ── Face polygon fill ─────────────────────────────────────────────────────
    _poly_shadow(s, face, 5, 7, 50)
    pygame.draw.polygon(s, MONITOR_BEIGE, face)

    # Bevel shading: near edge = shadow (catching less light), far edge = highlight
    if lean == -1:
        # LEFT monitor: left=near, right=far
        pygame.draw.line(s, MONITOR_LIGHT,  face[0], face[1], BEV)   # top
        pygame.draw.line(s, MONITOR_SHADOW, face[0], face[3], BEV)   # left  (near) — slight shadow
        pygame.draw.line(s, MONITOR_SHADOW, face[2], face[3], BEV)   # bottom
        pygame.draw.line(s, MONITOR_LIGHT,  face[1], face[2], BEV)   # right (far)  — lighter
    else:
        # RIGHT monitor: right=near, left=far
        pygame.draw.line(s, MONITOR_LIGHT,  face[0], face[1], BEV)   # top
        pygame.draw.line(s, MONITOR_LIGHT,  face[0], face[3], BEV)   # left  (far)  — lighter
        pygame.draw.line(s, MONITOR_SHADOW, face[2], face[3], BEV)   # bottom
        pygame.draw.line(s, MONITOR_SHADOW, face[1], face[2], BEV)   # right (near) — shadow

    pygame.draw.polygon(s, MONITOR_SHADOW, face, 1)

    # ── Screen bezel & inner area ─────────────────────────────────────────────
    inner = pygame.Rect(ix, iy, iw, ih)
    bz = inner.inflate(12, 12)
    pygame.draw.rect(s, BEZEL_DARK, bz, border_radius=8)
    pygame.draw.rect(s, (6, 12, 10), inner, border_radius=3)

    # Subtle reflection line in bezel
    pygame.draw.line(s, (50, 55, 50), (bz.x+6, bz.y+3), (bz.right-6, bz.y+3), 1)

    # ── LED + button row ──────────────────────────────────────────────────────
    pygame.draw.circle(s, (50, 200, 50), (int(led_x), int(btn_cy)), 5)
    pygame.draw.circle(s, (110, 255, 110), (int(led_x), int(btn_cy)), 2)
    for bi in range(3):
        bx2 = int(led_x) + 14 + bi * 12
        br2 = pygame.Rect(bx2, int(btn_cy) - 4, 9, 7)
        pygame.draw.rect(s, MONITOR_SHADOW, br2, border_radius=2)

    try:
        bf = pygame.font.SysFont("couriernew,monospace", 8, bold=True)
        bl = bf.render("VARTECH", True, MONITOR_SHADOW)
        s.blit(bl, bl.get_rect(center=(int(brand_cx), int(btn_cy))))
    except: pass

    return inner


# ══════════════════════════════════════════════════════════════════════════════
#  CONTROL PANEL
# ══════════════════════════════════════════════════════════════════════════════

def draw_control_panel(s, rect):
    r = rect
    D, SD = 12, 8

    # Bottom depth face
    bot = [
        (r.x,        r.bottom),
        (r.right,    r.bottom),
        (r.right + D, r.bottom + SD),
        (r.x - D,    r.bottom + SD),
    ]
    pygame.draw.polygon(s, CTRL_SHADOW, bot)

    # Right depth face
    rface = [
        (r.right,       r.y),
        (r.right + D,   r.y + SD),
        (r.right + D,   r.bottom + SD),
        (r.right,       r.bottom),
    ]
    pygame.draw.polygon(s, tuple(max(0,c-20) for c in CTRL_SHADOW), rface)

    # Drop shadow
    shw = pygame.Surface((r.w + 30, 18), pygame.SRCALPHA)
    pygame.draw.ellipse(shw, (0, 0, 0, 60), shw.get_rect())
    s.blit(shw, (r.x - 10, r.bottom + SD + 3))

    # Main face
    pygame.draw.rect(s, CTRL_BEIGE, r, border_radius=14)
    pygame.draw.line(s, CTRL_LIGHT,  (r.x+12, r.y+5),    (r.right-12, r.y+5),    2)
    pygame.draw.line(s, CTRL_SHADOW, (r.x+12, r.bottom-5),(r.right-12, r.bottom-5),2)
    pygame.draw.rect(s, CTRL_SHADOW, r, 2, border_radius=14)


def draw_slider_3d(s, rect, ratio):
    r = rect
    groove = pygame.Rect(r.x, r.centery - 6, r.w, 12)
    # Recessed groove
    pygame.draw.rect(s, MONITOR_SHADOW, groove, border_radius=6)
    pygame.draw.rect(s, (44, 50, 46), groove.inflate(-2, -2), border_radius=5)
    # Inner highlight
    pygame.draw.line(s, (30, 35, 32), (groove.x+4, groove.centery-2),
                     (groove.right-4, groove.centery-2), 1)
    # Green fill
    fw = int(r.w * ratio)
    if fw > 6:
        pygame.draw.rect(s, BTN_GREEN, (r.x, r.centery - 5, fw, 10), border_radius=5)
        hi = (min(255, BTN_GREEN[0]+40), min(255, BTN_GREEN[1]+40), min(255, BTN_GREEN[2]+40))
        pygame.draw.line(s, hi, (r.x+3, r.centery-3), (r.x+fw-3, r.centery-3), 1)
    # Knob
    kx = r.x + fw
    knob = pygame.Rect(kx - 11, r.centery - 18, 22, 36)
    shadow_box(s, knob, CTRL_LIGHT, CTRL_SHADOW, 7, 4)
    for li in range(-4, 5, 4):
        pygame.draw.line(s, CTRL_SHADOW,
                         (kx + li, r.centery - 10),
                         (kx + li, r.centery + 10), 1)
    return knob


def draw_round_btn(s, rect, col, label, font, active=False):
    """Generic chunky round button."""
    hi = tuple(min(255, c + 45) for c in col)
    sh_col = tuple(max(0, c - 55) for c in col)
    shadow_box(s, rect, col if not active else hi, sh_col, 8, 4)
    if active:
        pygame.draw.rect(s, hi, rect.inflate(-4, -4), border_radius=6)
    txt(s, label, font, WHITE, rect.centerx, rect.centery)


def draw_tooltip(s, text, tip_x, tip_y, font):
    """Dark speech-bubble tooltip pointing down."""
    lines = []
    words = text.split()
    cur = ""
    MAX_W = 320
    for w in words:
        test = (cur + " " + w).strip()
        if font.size(test)[0] <= MAX_W:
            cur = test
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)

    pad = 16
    line_h = font.get_height() + 4
    bw = max(font.size(ln)[0] for ln in lines) + pad * 2
    bh = len(lines) * line_h + pad
    bx = tip_x - bw // 2
    by = tip_y - bh - 20

    # Shadow
    shb = pygame.Surface((bw + 8, bh + 8), pygame.SRCALPHA)
    pygame.draw.rect(shb, (0, 0, 0, 60), (4, 4, bw, bh), border_radius=14)
    s.blit(shb, (bx - 2, by - 2))

    bubble = pygame.Rect(bx, by, bw, bh)
    pygame.draw.rect(s, (18, 18, 18), bubble, border_radius=14)
    pygame.draw.rect(s, (60, 60, 60), bubble, 2, border_radius=14)

    # Triangle pointer
    tri = [(tip_x - 12, by + bh), (tip_x + 12, by + bh), (tip_x, tip_y)]
    pygame.draw.polygon(s, (18, 18, 18), tri)
    pygame.draw.line(s, (18, 18, 18), (tip_x - 12, by + bh), (tip_x + 12, by + bh), 4)

    for i, ln in enumerate(lines):
        tr = font.render(ln, True, WHITE)
        s.blit(tr, tr.get_rect(center=(tip_x, by + pad // 2 + line_h // 2 + i * line_h)))


# ══════════════════════════════════════════════════════════════════════════════
#  LIVE FEED SILHOUETTE
# ══════════════════════════════════════════════════════════════════════════════

def draw_live_feed(s, inner, t):
    surf = pygame.Surface((inner.w, inner.h), pygame.SRCALPHA)
    surf.fill((10, 14, 12))
    for y in range(0, inner.h, 3):
        pygame.draw.line(surf, (0, 0, 0, 18), (0, y), (inner.w, y))

    cx, cy = inner.w // 2, inner.h // 2 + 5
    bob = int(math.sin(t * 0.04) * 3)
    body = (52, 56, 52)

    # Shadow
    sh2 = pygame.Surface((inner.w, inner.h), pygame.SRCALPHA)
    pygame.draw.circle(sh2, (0, 0, 0, 40), (cx + 6, cy + 44 + bob), 24)
    surf.blit(sh2, (0, 0))

    # Legs
    for side in [-1, 1]:
        pygame.draw.line(surf, body, (cx + side * 12, cy + 14 + bob),
                         (cx + side * 18, cy + 44 + bob), 10)
    # Torso
    pygame.draw.rect(surf, body, (cx - 16, cy - 26 + bob, 32, 42), border_radius=5)
    # Arms
    for side in [-1, 1]:
        pygame.draw.line(surf, body, (cx + side * 14, cy - 16 + bob),
                         (cx + side * 30, cy - 2 + bob), 9)
    # Head
    pygame.draw.circle(surf, body, (cx, cy - 44 + bob), 17)

    # LIVE badge
    pygame.draw.rect(surf, (200, 30, 30), (6, 6, 40, 17), border_radius=3)
    try:
        lf = pygame.font.SysFont("couriernew,monospace", 10, bold=True)
        lr = lf.render("● LIVE", True, WHITE)
        surf.blit(lr, lr.get_rect(center=(26, 15)))
    except: pass

    # Signal bars
    for bi in range(4):
        bh = 4 + bi * 4
        bc = (55, 200, 55) if bi < 3 else (190, 190, 190)
        pygame.draw.rect(surf, bc, (inner.w - 14 - bi * 8, 7 + (12 - bh), 6, bh))

    s.blit(surf, inner.topleft)


# ══════════════════════════════════════════════════════════════════════════════
#  INTRO SCREEN
# ══════════════════════════════════════════════════════════════════════════════

class IntroScreen:
    def __init__(self, F):
        self.F = F
        self.t = 0; self.blink = True; self.bt = 0
        self.btn = pygame.Rect(WIN_W // 2 - 150, 555, 300, 56)

    def handle(self, ev):
        if ev.type == pygame.MOUSEBUTTONDOWN and self.btn.collidepoint(ev.pos): return "levels"
        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_RETURN: return "levels"

    def update(self):
        self.t += 1; self.bt += 1
        if self.bt > 28: self.blink = not self.blink; self.bt = 0

    def draw(self, s):
        draw_room(s)
        F = self.F; cx = WIN_W // 2

        card = pygame.Rect(cx - 310, 115, 620, 400)
        shadow_box(s, card, MONITOR_BEIGE, MONITOR_SHADOW, 20, 10)

        cr = pygame.Rect(cx - 160, 140, 320, 228)
        ic = draw_crt_3d(s, cr, 278, 174)
        self._anim_screen(s, ic)
        scan(s, ic)

        txt(s, "GRAFIKA KOMPUTER  ·  FINAL PROJECT 2025", F["tiny"], (110, 135, 145), cx, 140)
        txt(s, "VAR SIMULATOR", F["press"], (28, 30, 28), cx, 388)
        txt(s, "VIDEO ASSISTANT REFEREE", F["tiny"], (75, 95, 108), cx, 415)
        txt(s, "Jadilah wasit VAR di ruang VOR. Analisis replay & buat keputusan!", F["body"], (65, 80, 88), cx, 452)

        if self.blink:
            shadow_box(s, self.btn, BTN_TEAL, (32, 108, 122), 12, 6)
            txt(s, "► MULAI SEKARANG", F["press"], WHITE, cx, self.btn.centery)

        txt(s, "Kelompok Grafkom · 2025", F["tiny"], (88, 118, 128), cx, 658)

    def _anim_screen(self, s, ic):
        a = pygame.Surface((ic.w, ic.h)); t = self.t
        IW, IH = ic.w, ic.h; a.fill((20, 85, 20))
        for i in range(5):
            sl = pygame.Surface((IW // 5, IH), pygame.SRCALPHA)
            sl.fill((0,0,0,15) if i%2 else (255,255,255,5)); a.blit(sl,(i*(IW//5),0))
        pygame.draw.line(a,(255,255,255,80),(IW//2,0),(IW//2,IH),1)
        pygame.draw.circle(a,(255,255,255,80),(IW//2,IH//2),28,1)
        bx2=IW//2+int(math.sin(t*.04)*70); by2=IH//2+int(math.cos(t*.06)*30)
        pygame.draw.circle(a,WHITE,(bx2,by2),5)
        for col,ox in [((204,34,0),-22),((0,68,187),26)]:
            px=bx2+ox+int(math.sin(t*.03)*4); py=by2+int(math.cos(t*.05)*3)
            pygame.draw.rect(a,col,(px-5,py-4,10,16),border_radius=2)
            pygame.draw.circle(a,(245,192,154),(px,py-8),4)
        s.blit(a, ic.topleft)


# ══════════════════════════════════════════════════════════════════════════════
#  LEVEL SELECT
# ══════════════════════════════════════════════════════════════════════════════

class LevelSelectScreen:
    def __init__(self, F):
        self.F = F; self.hover = -1
        cw, gap = 300, 26
        sx = (WIN_W - (3*cw + 2*gap)) // 2
        self.cards = [pygame.Rect(sx + i*(cw+gap), 150, cw, 270) for i in range(3)]
        self.back = pygame.Rect(18, 14, 95, 32)

    def handle(self, ev):
        if ev.type == pygame.MOUSEMOTION:
            self.hover = next((i for i,r in enumerate(self.cards) if r.collidepoint(ev.pos)), -1)
        if ev.type == pygame.MOUSEBUTTONDOWN:
            if self.back.collidepoint(ev.pos): return "intro"
            for i,r in enumerate(self.cards):
                if r.collidepoint(ev.pos): return i+1

    def update(self): pass

    def draw(self, s):
        draw_room(s); F = self.F; cx = WIN_W//2
        shadow_box(s, self.back, CTRL_BEIGE, CTRL_SHADOW, 6, 3)
        txt(s, "◄ BACK", F["tiny"], (55,55,55), self.back.centerx, self.back.centery)
        txt(s, "PILIH KATEGORI", F["press"], WHITE, cx, 64)
        txt(s, "Program akan memilih video acak dari folder yang dipilih", F["body"], (195,222,228), cx, 100)
        cols = [GREEN, AMBER, RED]
        for i,(r,lid) in enumerate(zip(self.cards,[1,2,3])):
            lv = LEVELS[lid]; col = cols[i]
            rr = r.move(0, -10 if self.hover==i else 0)
            ic = draw_crt_3d(s, rr, 258, 172)
            fy = ic.y + 8
            txt(s, lv["icon"], F["icon"], WHITE, ic.centerx, fy+16)
            txt(s, f"LEVEL 0{lid}", F["body"], col, ic.centerx, fy+48)
            bb = F["tiny"].render(lv["badge"], True, col)
            bx2 = ic.centerx - bb.get_width()//2
            bg = pygame.Surface((bb.get_width()+10,bb.get_height()+4),pygame.SRCALPHA)
            bg.fill((*col,40)); s.blit(bg,(bx2-5,fy+60)); s.blit(bb,(bx2,fy+62))
            txt(s, lv["name"], F["body"], WHITE, ic.centerx, fy+92)
            words=lv["case"].split(); lines=[]; cur=""
            for w in words:
                test=cur+" "+w if cur else w
                cur=test if F["tiny"].size(test)[0]<ic.w-10 else (lines.append(cur) or w)
            if cur: lines.append(cur)
            for j,ln in enumerate(lines[:2]):
                txt(s,ln,F["tiny"],(170,185,185),ic.centerx,fy+114+j*16)
            scan(s,ic)


# ══════════════════════════════════════════════════════════════════════════════
#  GAME SCREEN
# ══════════════════════════════════════════════════════════════════════════════

class GameScreen:
    def __init__(self, F):
        self.F = F; self.video = None; self.lv_id = 1
        self.score_ok = 0; self.score_tot = 0
        self._reset(); self._build()

    # ── Reset ─────────────────────────────────────────────────────────────────
    def _reset(self):
        self.zoom_idx = 0; self.zoom = ZOOM_LEVELS[0]
        self.draw_mode = False; self.user_line = None
        self.drag_start = None; self.dragging = False
        self.decided = False; self.result = None; self.cam_sel = 1
        self._next_btn = None; self._restart_btn = None
        self.vid_file = "Belum Ada Video"
        self.inner_c = pygame.Rect(415, 65, 448, 308)   # fallback
        self.dyn_dec = []; self.cam_rects = []; self._t = 0

    # ── Build button layout ───────────────────────────────────────────────────
    def _build(self):
        bx, by = CTRL_PANEL.x, CTRL_PANEL.y
        # Slider: centre-left of panel
        self.slider = pygame.Rect(bx + 110, by + 48, 196, 14)
        self.slider_drag = False
        self.btns = {
            "back": pygame.Rect(18, 14, 95, 32),
            # Playback
            "play": pygame.Rect(bx + 12,  by + 22, 48, 58),
            "m5":   pygame.Rect(bx + 66,  by + 22, 36, 26),
            "p5":   pygame.Rect(bx + 66,  by + 54, 36, 26),
            # Zoom
            "zm":   pygame.Rect(bx + 318, by + 22, 36, 50),
            "zp":   pygame.Rect(bx + 360, by + 22, 36, 50),
            # Line draw tool (all levels — only shown in level 3)
            "line": pygame.Rect(bx + 318, by + 78, 78, 22),
        }
        self.dec_meta = [
            {"key":d["key"],"label":d["label"],"bg":d["bg"],"fg":d["fg"]}
            for d in DECISIONS
        ]

    # ── Boot level ────────────────────────────────────────────────────────────
    def boot(self, lid):
        self.lv_id = lid; self._reset()
        vdir = LEVELS[lid].get("video_dir", "")
        path = "assets/placeholder.mp4"
        if os.path.exists(vdir):
            vids = [f for f in os.listdir(vdir)
                    if f.lower().endswith(('.mp4','.avi','.mov'))]
            if vids:
                cf = random.choice(vids); path = os.path.join(vdir, cf); self.vid_file = cf
            else: self.vid_file = "[Folder Kosong]"
        else: self.vid_file = "[Folder Tidak Ada]"
        self.video = VideoPlayer(path)

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _to_vid(self, sx, sy):
        ic = self.inner_c
        return (sx - ic.x) / ic.w, (sy - ic.y) / ic.h

    # ── Input handling ────────────────────────────────────────────────────────
    def handle(self, ev):
        B = self.btns
        if ev.type == pygame.MOUSEBUTTONDOWN:
            p = ev.pos
            if B["back"].collidepoint(p):  return "levels"
            if B["play"].collidepoint(p) and self.video: self.video.toggle_play_pause()
            if B["m5"].collidepoint(p):    self._jump(-5)
            if B["p5"].collidepoint(p):    self._jump(5)
            if B["zm"].collidepoint(p):    self._zoom(-1)
            if B["zp"].collidepoint(p):    self._zoom(1)
            # Line tool toggle (level 3 only)
            if LEVELS[self.lv_id]["show_line"] and B["line"].collidepoint(p):
                self.draw_mode = not self.draw_mode
                if not self.draw_mode: self.user_line = None
            if self.slider.collidepoint(p): self.slider_drag = True; self._seek(p[0])
            for i, r in enumerate(self.cam_rects):
                if r.collidepoint(p): self.cam_sel = i + 1
            # Line drawing on video
            if self.draw_mode and self.inner_c.collidepoint(p):
                vx, vy = self._to_vid(*p)
                self.drag_start = (vx, vy)
                self.user_line = (vx, vy, vx, vy)
                self.dragging = True
            # Decision buttons
            if not self.decided:
                for d in self.dyn_dec:
                    if d["rect"].collidepoint(p): self._decide(d["key"])

        if ev.type == pygame.MOUSEMOTION:
            if self.slider_drag: self._seek(ev.pos[0])
            if self.dragging and self.drag_start:
                vx, vy = self._to_vid(*ev.pos)
                x1, y1 = self.drag_start
                self.user_line = (x1, y1, vx, vy)

        if ev.type == pygame.MOUSEBUTTONUP:
            self.slider_drag = False; self.dragging = False

        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_SPACE and self.video: self.video.toggle_play_pause()
            if ev.key == pygame.K_LEFT:  self._jump(-3)
            if ev.key == pygame.K_RIGHT: self._jump(3)

    def _seek(self, mx):
        if not self.video: return
        r = max(0., min(1., (mx - self.slider.x) / self.slider.w))
        self.video.seek(int(r * self.video.total_frames)); self.video.is_playing = False

    def _jump(self, d):
        if self.video: self.video.seek(self.video.current_frame_index + d); self.video.is_playing = False

    def _zoom(self, d):
        self.zoom_idx = max(0, min(len(ZOOM_LEVELS)-1, self.zoom_idx+d))
        self.zoom = ZOOM_LEVELS[self.zoom_idx]

    def _decide(self, key):
        if not self.video: return
        self.decided = True; self.video.is_playing = False
        lv = LEVELS[self.lv_id]; ok = key == lv["ans"]
        if ok: self.score_ok += 1
        self.score_tot += 1
        self.result = {"ok":ok,"key":key,"lv":lv,"next_lv":self.lv_id<3}

    def update(self, dt):
        self._t += 1
        if self.video and not self.decided: self.video.advance()

    # ── DRAW ─────────────────────────────────────────────────────────────────
    def draw(self, s):
        F = self.F; lv = LEVELS[self.lv_id]

        # 1. Room background
        draw_room(s)

        # 2. TOP BAR
        shadow_box(s, self.btns["back"], CTRL_BEIGE, CTRL_SHADOW, 6, 3)
        txt(s, "◄ EXIT", F["tiny"], (55,55,55), self.btns["back"].centerx, self.btns["back"].centery)
        score_r = pygame.Rect(WIN_W - 148, 10, 134, 32)
        shadow_box(s, score_r, CTRL_BEIGE, CTRL_SHADOW, 8, 3)
        txt(s, f"SKOR  {self.score_ok} / {self.score_tot}", F["tiny"], (45,55,65), score_r.centerx, score_r.centery)

        # 3. LEFT monitor — angled, LIVE feed
        il = draw_crt_angled(s, L_MON, 245, 172, -1)   # lean=-1: left outer panel visible
        draw_live_feed(s, il, self._t)
        # Camera tabs below inner screen
        clbls = ["CAM1","CAM2","GOAL"]; self.cam_rects = []
        tab_w = il.w // 3
        for i, lb in enumerate(clbls):
            r = pygame.Rect(il.x + i*tab_w, il.bottom + 2, tab_w, 17)
            self.cam_rects.append(r)
            act = (i+1 == self.cam_sel)
            pygame.draw.rect(s, BTN_TEAL if act else MONITOR_SHADOW, r, border_radius=3)
            pygame.draw.rect(s, MONITOR_SHADOW, r, 1, border_radius=3)
            txt(s, lb, F["tiny"], WHITE if act else (155,160,150), r.centerx, r.centery)

        # 4. RIGHT monitor — angled, decision system
        ir = draw_crt_angled(s, R_MON, 245, 172, +1)   # lean=+1: right outer panel visible
        txt(s, "DISCIPLINARY", F["tiny"], (90, 228, 90), ir.centerx, ir.y + 14)
        txt(s, "ACTION SYSTEM", F["tiny"], (90, 228, 90), ir.centerx, ir.y + 28)
        pygame.draw.line(s, (45, 95, 45), (ir.x+6, ir.y+38), (ir.right-6, ir.y+38), 1)
        self.dyn_dec = []
        for i, d in enumerate(self.dec_meta):
            r = pygame.Rect(ir.x+5, ir.y+44+i*28, ir.w-10, 24)
            self.dyn_dec.append({"rect":r,"key":d["key"]})
            dim = self.decided and not (self.result and self.result["key"]==d["key"])
            a = 60 if dim else 255
            ds = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
            pygame.draw.rect(ds, (*d["bg"],a), (0,0,r.w,r.h), border_radius=4)
            s.blit(ds, r.topleft)
            ts = F["tiny"].render(d["label"], True, (*d["fg"],a))
            s.blit(ts, ts.get_rect(center=r.center))
            if not self.decided:
                mx,my = pygame.mouse.get_pos()
                if r.collidepoint(mx,my):
                    gl = pygame.Surface((r.w,r.h),pygame.SRCALPHA)
                    pygame.draw.rect(gl,(255,255,255,30),(0,0,r.w,r.h),border_radius=4)
                    s.blit(gl,r.topleft)
        scan(s, ir)

        # 5. CENTRE monitor (drawn LAST to appear in front)
        self.inner_c = draw_crt_3d(s, C_MON, 450, 308)
        ic = self.inner_c
        if self.video:
            raw = self.video.get_surface((ic.w, ic.h))
            if self.zoom > 1.0:
                cw2=int(ic.w/self.zoom); ch2=int(ic.h/self.zoom)
                crop=pygame.Rect(ic.w//2-cw2//2,ic.h//2-ch2//2,cw2,ch2).clip(raw.get_rect())
                if crop.w>0 and crop.h>0:
                    raw=pygame.transform.scale(raw.subsurface(crop),(ic.w,ic.h))
            s.blit(raw, ic.topleft)
            # VAR line drawing overlay
            if self.user_line:
                x1r,y1r,x2r,y2r = self.user_line
                p1=(int(ic.x+x1r*ic.w), int(ic.y+y1r*ic.h))
                p2=(int(ic.x+x2r*ic.w), int(ic.y+y2r*ic.h))
                # Glow effect
                for thickness in [6, 4, 2]:
                    alpha = 60 if thickness == 6 else (120 if thickness == 4 else 255)
                    glow_col = (*AMBER[:3],) if thickness == 2 else (255, 230, 50)
                    bresenham(s, p1, p2, glow_col, thickness)
                pygame.draw.circle(s, AMBER, p1, 7)
                pygame.draw.circle(s, WHITE,  p1, 3)
                pygame.draw.circle(s, AMBER, p2, 7)
                pygame.draw.circle(s, WHITE,  p2, 3)
        else:
            txt(s, "Tidak ada video", F["body"], GREY, ic.centerx, ic.centery)
        scan(s, ic)

        # HUD on centre monitor
        prog = self.video.current_frame_index if self.video else 0
        tot  = self.video.total_frames        if self.video else 1
        hud_t = pygame.Surface((ic.w, 22), pygame.SRCALPHA); hud_t.fill((0,0,0,130))
        s.blit(hud_t, ic.topleft)
        txt(s, f"FRAME {prog:04d}/{tot:04d}", F["tiny"], (165,212,255), ic.x+65, ic.y+11)
        txt(s, f"ZOOM ×{self.zoom:.1f}",      F["tiny"], AMBER,         ic.right-42, ic.y+11)
        hud_b = pygame.Surface((ic.w, 20), pygame.SRCALPHA); hud_b.fill((0,0,0,110))
        s.blit(hud_b, (ic.x, ic.bottom-20))
        fname = self.vid_file if len(self.vid_file)<46 else self.vid_file[:44]+"…"
        txt(s, f"▶ {fname}", F["tiny"], (155,178,188), ic.centerx, ic.bottom-10)

        # 6. CONTROL PANEL
        draw_control_panel(s, CTRL_PANEL)
        B = self.btns
        ratio = prog/tot if tot>0 else 0
        draw_slider_3d(s, self.slider, ratio)

        # Play/Pause button
        playing = self.video.is_playing if self.video else False
        play_col = BTN_GREEN if playing else (65, 170, 88)
        shadow_box(s, B["play"], play_col, (28,115,48), 10, 5)
        play_lbl = "▐▐" if playing else "►"
        txt(s, play_lbl, F["body"], WHITE, B["play"].centerx, B["play"].centery)

        # ◄◄ / ►► frame jump buttons
        for key, lbl in [("m5","◄◄"), ("p5","►►")]:
            r = B[key]
            shadow_box(s, r, BTN_TEAL, (32,108,122), 6, 3)
            txt(s, lbl, F["tiny"], WHITE, r.centerx, r.centery)

        # ZOOM buttons
        for key, lbl in [("zm","Z−"), ("zp","Z+")]:
            r = B[key]
            shadow_box(s, r, BTN_TEAL, (32,108,122), 8, 4)
            txt(s, lbl, F["body"], WHITE, r.centerx, r.centery)

        # Labels
        txt(s, "TIMELINE", F["tiny"], (95,115,125),
            self.slider.centerx, self.slider.bottom + 14)
        txt(s, "ZOOM",     F["tiny"], (95,115,125),
            (B["zm"].centerx + B["zp"].centerx) // 2, CTRL_PANEL.y + 86)

        # ✏ LINE TOOL button — level 3 only, clearly visible
        if lv["show_line"]:
            r = B["line"]
            act = self.draw_mode
            btn_col = (175, 50, 50) if act else BTN_TEAL
            btn_brd = (90, 18, 18) if act else (32, 108, 122)
            shadow_box(s, r, btn_col, btn_brd, 6, 3)
            lbl_line = "✏ AKTIF" if act else "✏ GARIS"
            txt(s, lbl_line, F["tiny"], WHITE, r.centerx, r.centery)
            # Blinking indicator when active
            if act and (self._t // 15) % 2 == 0:
                glow = pygame.Surface((r.w+6, r.h+6), pygame.SRCALPHA)
                pygame.draw.rect(glow, (255,200,100,80), (0,0,r.w+6,r.h+6), border_radius=8)
                s.blit(glow, (r.x-3, r.y-3))

        # 7. TOOLTIP
        draw_tooltip(s, lv["hint"], C_MON.centerx, CTRL_PANEL.y - 6, F["body"])

        # 8. DESK PROPS
        # Red rule book
        bk = pygame.Rect(48, 508, 138, 130)
        sh_bk = pygame.Surface((bk.w+10, 14), pygame.SRCALPHA)
        pygame.draw.ellipse(sh_bk, (0,0,0,55), sh_bk.get_rect())
        s.blit(sh_bk, (bk.x-3, bk.bottom+3))
        # Spine
        pygame.draw.rect(s, (138,22,22), (bk.x, bk.y, 13, bk.h), border_radius=3)
        # Pages (white strip on right)
        pygame.draw.rect(s, (232,230,220), (bk.right-7, bk.y+4, 7, bk.h-8))
        # Cover
        cov = pygame.Rect(bk.x+11, bk.y, bk.w-18, bk.h)
        pygame.draw.rect(s, (198,38,38), cov, border_radius=3)
        pygame.draw.rect(s, (218,62,62), cov.inflate(-6,-6), 1, border_radius=2)
        txt(s, "RULES", F["tiny"], (255,188,188), cov.centerx, cov.centery-10)
        txt(s, "VAR",   F["tiny"], (255,188,188), cov.centerx, cov.centery+8)

        # Grey notepad
        np_r = pygame.Rect(WIN_W-192, 520, 155, 72)
        sh_np = pygame.Surface((np_r.w+8, 12), pygame.SRCALPHA)
        pygame.draw.ellipse(sh_np, (0,0,0,50), sh_np.get_rect())
        s.blit(sh_np, (np_r.x-3, np_r.bottom+3))
        pygame.draw.rect(s, (198,204,192), np_r, border_radius=5)
        pygame.draw.rect(s, (168,174,162), np_r, 2, border_radius=5)
        for row in range(3):
            pygame.draw.line(s, (152,158,146),
                             (np_r.x+10, np_r.y+15+row*16),
                             (np_r.right-10, np_r.y+15+row*16), 1)
        try:
            nf = pygame.font.SysFont("couriernew,monospace", 9)
            nr = nf.render("NOTES", True, (128,134,122))
            s.blit(nr, nr.get_rect(center=(np_r.centerx, np_r.y+8)))
        except: pass

        if self.result: self._result_overlay(s)

    # ── Result overlay ────────────────────────────────────────────────────────
    def _result_overlay(self, s):
        F = self.F; res = self.result; ok = res["ok"]
        ov = pygame.Surface((WIN_W,WIN_H),pygame.SRCALPHA); ov.fill((0,0,0,215)); s.blit(ov,(0,0))
        cx = WIN_W//2; bw,bh = 500,345; bx,by = cx-bw//2, WIN_H//2-bh//2
        shadow_box(s, pygame.Rect(bx,by,bw,bh), MONITOR_BEIGE, MONITOR_SHADOW, 16, 10)
        stripe_col = (38,158,68) if ok else (185,36,36)
        pygame.draw.rect(s, stripe_col, pygame.Rect(bx,by,bw,54), border_radius=16)
        pygame.draw.rect(s, stripe_col, pygame.Rect(bx,by+30,bw,24))
        txt(s, "KEPUTUSAN BENAR!" if ok else "KEPUTUSAN SALAH!", F["press"], WHITE, cx, by+27)
        txt(s, "✅" if ok else "❌", F["icon"], (30,30,30), cx, by+92)
        txt(s, res["lv"]["explain"],         F["tiny"], (58,58,58), cx, by+148)
        txt(s, "Jawaban: "+res["lv"]["ans_label"], F["tiny"], (88,88,88), cx, by+174)
        txt(s, f"Skor: {self.score_ok} / {self.score_tot}", F["mono"], (48,48,48), cx, by+208)
        nb = pygame.Rect(cx-125, by+258, 250, 52)
        shadow_box(s, nb, BTN_TEAL, (32,108,122), 12, 5)
        lbl = "LEVEL BERIKUTNYA ►" if res["next_lv"] else "LIHAT HASIL ►"
        txt(s, lbl, F["tiny"], WHITE, cx, nb.centery); self._next_btn = nb

    def handle_result_click(self, pos):
        if self.result and self._next_btn and self._next_btn.collidepoint(pos):
            return "next" if self.result["next_lv"] else "final"

    # ── Final screen ──────────────────────────────────────────────────────────
    def draw_final(self, s):
        F=self.F; c=self.score_ok; t=self.score_tot; cx=WIN_W//2
        ov=pygame.Surface((WIN_W,WIN_H),pygame.SRCALPHA); ov.fill((0,0,0,222)); s.blit(ov,(0,0))
        bw,bh=520,395; bx,by=cx-bw//2,WIN_H//2-bh//2
        shadow_box(s,pygame.Rect(bx,by,bw,bh),MONITOR_BEIGE,MONITOR_SHADOW,16,10)
        sc=(190,148,18)
        pygame.draw.rect(s,sc,pygame.Rect(bx,by,bw,54),border_radius=16)
        pygame.draw.rect(s,sc,pygame.Rect(bx,by+30,bw,24))
        txt(s,"⚽ GAME SELESAI!",F["press"],WHITE,cx,by+27)
        txt(s,"⭐"*c if c>0 else "—",F["big"],AMBER,cx,by+112)
        txt(s,f"{c} / {t}",F["big"],(48,48,48),cx,by+198)
        txt(s,SCORE_MSGS[c],F["mono"],(78,78,78),cx,by+264)
        rb=pygame.Rect(cx-125,by+308,250,52)
        shadow_box(s,rb,BTN_TEAL,(32,108,122),12,5)
        txt(s,"↺ MAIN LAGI",F["tiny"],WHITE,cx,rb.centery); self._restart_btn=rb
