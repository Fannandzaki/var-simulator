"""
constants.py — Global constants + level definitions (Randomized Video Folder Version)
"""

WIN_W, WIN_H = 1100, 680
FPS          = 30

# Colours
INK    = (10,  10,  20)
GREEN  = (26, 223, 85)
AMBER  = (255, 208, 0)
BLUE   = (51, 170, 255)
RED    = (255, 51,  51)
PANEL  = (13,  13,  28)
BEZEL  = (28,  28,  46)
DESK   = (126, 174, 186)   # Retro light blue-grey desk
CRT_BEIGE = (215, 218, 205) # Off-white retro monitor casing
CRT_SHADOW = (180, 185, 175) # Darker beige for shading
CRT_BEZEL = (35, 40, 42)    # Dark grey inner monitor bezel
CRT_BLUE = (45, 95, 155)    # Chunky blue buttons
BORDER = (30,  30,  48)
WHITE  = (255, 255, 255)
GREY   = (80,  80, 100)
DARK   = (7,   7,  15)

ZOOM_LEVELS = [1.0, 1.6, 2.4, 3.2]

# ── Level definitions ─────────────────────────────────────────────────────────
LEVELS = {
    1: {
        "name":       "PEMANASAN",
        "badge":      "MUDAH",
        "badge_col":  GREEN,
        "icon":       "⚽",
        "hint":       "Putar ulang — apakah ini pelanggaran keras?",
        "case":       "Tackle brutal dari belakang. Langsung terlihat jelas.",
        "video_dir":  "assets/pelanggaran_keras",  # Folder kategori
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
        "video_dir":  "assets/handball",  # Folder kategori
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
        "video_dir":  "assets/offside",  # Folder kategori
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
