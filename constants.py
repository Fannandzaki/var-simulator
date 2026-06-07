"""
constants.py — Global constants + level definitions
"""
import pygame

WIN_W, WIN_H = 1280, 720
FPS          = 30

# ── Colour Palette (Cartoon 3D Room) ─────────────────────────────────────────
INK          = (10,  10,  20)
WHITE        = (255, 255, 255)
GREY         = (80,  80, 100)
DARK         = (7,   7,  15)
BORDER       = (30,  30,  48)

# Signals / feedback
GREEN  = (60,  210, 100)
AMBER  = (255, 208,   0)
BLUE   = (51,  170, 255)
RED    = (255,  51,  51)

# Room environment
WALL_TEAL    = (62,  138, 148)   # main wall colour
WALL_DARK    = (42,  108, 118)   # upper wall / shadow
WALL_LIGHT   = (80,  158, 168)   # wall highlight
DESK_BLUE    = (100, 182, 196)   # desk surface
DESK_FRONT   = (78,  155, 168)   # desk front face (darker)
DESK_SHADOW  = (58,  128, 142)   # desk shadow / edge

# CRT Monitor
MONITOR_BEIGE  = (218, 214, 198)   # main casing
MONITOR_LIGHT  = (235, 232, 218)   # highlight edge
MONITOR_SHADOW = (168, 164, 148)   # shadow edge
MONITOR_BACK   = (185, 182, 166)   # back bulge of CRT
BEZEL_DARK     = (28,  32,  30)    # inner screen bezel

# Control panel
CTRL_BEIGE  = (212, 208, 192)
CTRL_LIGHT  = (230, 227, 212)
CTRL_SHADOW = (162, 158, 142)
BTN_TEAL    = (70,  155, 168)    # D-pad / action buttons
BTN_TEAL_LT = (95,  180, 193)   # button highlight
BTN_GREEN   = (88,  185,  88)   # slider / play button
BTN_RED     = (210,  55,  55)

# Legacy aliases (kept for compatibility)
PANEL      = (13, 13, 28)
BEZEL      = (28, 28, 46)
CRT_BEIGE  = MONITOR_BEIGE
CRT_SHADOW = MONITOR_SHADOW
CRT_BEZEL  = BEZEL_DARK
CRT_BLUE   = BTN_TEAL

# ── Zoom levels ───────────────────────────────────────────────────────────────
ZOOM_LEVELS = [1.0, 1.6, 2.4, 3.2]

# ── Game-screen layout (1280×720 canvas) ─────────────────────────────────────
# These are the *outer casing* rects for each monitor
C_MON  = pygame.Rect(390,  40, 500, 380)   # centre — largest
L_MON  = pygame.Rect( 48, 142, 295, 260)   # left  — more forward, slightly inward
R_MON  = pygame.Rect(937, 142, 295, 260)   # right — more forward, slightly inward

# Physical control panel below centre monitor
CTRL_PANEL = pygame.Rect(440, 435, 400, 105)

# Scrubber / slider inside the control panel
BOARD = CTRL_PANEL   # alias kept for old code paths

# ── Level definitions ─────────────────────────────────────────────────────────
LEVELS = {
    1: {
        "name":       "PEMANASAN",
        "badge":      "MUDAH",
        "badge_col":  GREEN,
        "icon":       "⚽",
        "hint":       "Putar ulang — apakah ini pelanggaran keras?",
        "case":       "Tackle brutal dari belakang. Langsung terlihat jelas.",
        "video_dir":  "assets/pelanggaran_keras",
        "ans":        "red",
        "ans_label":  "KARTU MERAH LANGSUNG",
        "explain":    "Tackle dari belakang, kaki terangkat — bahaya nyata → Kartu Merah.",
        "rules":      ["Tackle keras dari belakang",
                       "Kaki terangkat → bahaya",
                       "Tidak ada usaha ke bola",
                       "→ Kartu Merah Langsung"],
        "show_line":  False,
    },
    2: {
        "name":       "INVESTIGASI",
        "badge":      "MENENGAH",
        "badge_col":  AMBER,
        "icon":       "🔍",
        "hint":       "Zoom ke area tangan — handball di kotak penalti?",
        "case":       "Handball di kotak penalti — perlu zoom untuk memastikan kontak.",
        "video_dir":  "assets/handball",
        "ans":        "pen",
        "ans_label":  "PENALTI",
        "explain":    "Bola menyentuh tangan, posisi tidak alami di kotak penalti → Penalti.",
        "rules":      ["Handball = posisi tangan tdk alami",
                       "Terjadi di dalam kotak penalti",
                       "Menambah besar tubuh?",
                       "→ Penalti"],
        "show_line":  False,
    },
    3: {
        "name":       "PRESISI TINGGI",
        "badge":      "SULIT",
        "badge_col":  RED,
        "icon":       "📐",
        "hint":       "Gunakan GARIS untuk menentukan offside!",
        "case":       "Offside super tipis — tarik garis VAR dengan presisi.",
        "video_dir":  "assets/offside",
        "ans":        "foul",
        "ans_label":  "OFFSIDE (PELANGGARAN)",
        "explain":    "Penyerang melampaui bek terakhir saat bola diumpan → Offside.",
        "rules":      ["Offside: bagian tubuh manapun",
                       "Melampaui bek terakhir",
                       "Diukur saat bola diumpan",
                       "→ Offside = Pelanggaran"],
        "show_line":  True,
    },
}

DECISIONS = [
    {"key":"foul","label":"⚠ PELANGGARAN",      "bg":(138,34,0),  "fg":(255,187,170)},
    {"key":"no",  "label":"✓ TIDAK PELANGGARAN", "bg":(0,77,26),   "fg":(170,255,204)},
    {"key":"pen", "label":"🎯 PENALTI",           "bg":(136,102,0), "fg":(255,238,187)},
    {"key":"red", "label":"🟥 KARTU MERAH",       "bg":(102,0,0),   "fg":(255,170,170)},
]

SCORE_MSGS = [
    "😔 Perlu Banyak Belajar!",
    "📚 Coba Lagi!",
    "⭐ Wasit VAR yang Baik!",
    "🏆 Wasit VAR Sempurna!",
]
