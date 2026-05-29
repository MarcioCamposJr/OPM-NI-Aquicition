"""Application-wide visual theme, QSS styles, and colour constants.

Implements a premium dark theme with a medical-grade aesthetic suitable
for a clinical ECG monitoring application.
"""

from __future__ import annotations

# ── Colour Palette ───────────────────────────────────────────────────────── #

# Primary surface colours (dark mode)
BG_DARKEST = "#0D0F14"       # Window / main background
BG_DARK = "#141821"          # Panel / sidebar background
BG_CARD = "#1A1F2E"          # Card / widget background
BG_HOVER = "#232A3A"         # Hover state
BG_INPUT = "#1E2433"         # Input field background
BORDER = "#2A3144"           # Subtle borders
BORDER_FOCUS = "#4A7DFF"     # Focus ring

# Accent colours
ACCENT_PRIMARY = "#4A7DFF"   # Primary blue accent
ACCENT_SUCCESS = "#22C55E"   # Green — recording / active
ACCENT_WARNING = "#F59E0B"   # Amber — caution
ACCENT_DANGER = "#EF4444"    # Red — stop / error
ACCENT_INFO = "#38BDF8"      # Light blue — info

# Text colours
TEXT_PRIMARY = "#E2E8F0"     # Main text
TEXT_SECONDARY = "#94A3B8"   # Secondary / muted text
TEXT_DISABLED = "#475569"    # Disabled text

# ── Channel colour palette (24 distinct colours) ────────────────────────── #

CHANNEL_COLORS: list[str] = [
    "#FF6B6B",  # 1  – Coral red
    "#4ECDC4",  # 2  – Teal
    "#45B7D1",  # 3  – Sky blue
    "#96CEB4",  # 4  – Sage green
    "#FFEAA7",  # 5  – Pale gold
    "#DDA0DD",  # 6  – Plum
    "#98D8C8",  # 7  – Mint
    "#F7DC6F",  # 8  – Sunflower
    "#BB8FCE",  # 9  – Lavender
    "#85C1E9",  # 10 – Powder blue
    "#F8C471",  # 11 – Sandy
    "#82E0AA",  # 12 – Emerald
    "#F1948A",  # 13 – Salmon
    "#AED6F1",  # 14 – Ice blue
    "#D7BDE2",  # 15 – Lilac
    "#A3E4D7",  # 16 – Aquamarine
    "#FAD7A0",  # 17 – Peach
    "#A9CCE3",  # 18 – Cerulean
    "#D5F5E3",  # 19 – Pale green
    "#FADBD8",  # 20 – Rose
    "#D4E6F1",  # 21 – Periwinkle
    "#E8DAEF",  # 22 – Thistle
    "#D1F2EB",  # 23 – Sea foam
    "#FCF3CF",  # 24 – Cream
]

# ── Fonts ────────────────────────────────────────────────────────────────── #

FONT_FAMILY = "Segoe UI, Inter, Roboto, sans-serif"
FONT_SIZE_SM = "11px"
FONT_SIZE_MD = "13px"
FONT_SIZE_LG = "16px"
FONT_SIZE_XL = "20px"
FONT_SIZE_TITLE = "24px"

# ── Spacing & Radius ────────────────────────────────────────────────────── #

RADIUS_SM = "4px"
RADIUS_MD = "8px"
RADIUS_LG = "12px"
SPACING_SM = "6px"
SPACING_MD = "12px"
SPACING_LG = "20px"

# ── QSS Stylesheet ──────────────────────────────────────────────────────── #

APP_STYLESHEET = f"""
/* ── Global ───────────────────────────────────────────────────────────── */
QWidget {{
    background-color: {BG_DARKEST};
    color: {TEXT_PRIMARY};
    font-family: {FONT_FAMILY};
    font-size: {FONT_SIZE_MD};
}}

QMainWindow {{
    background-color: {BG_DARKEST};
}}

/* ── Labels ───────────────────────────────────────────────────────────── */
QLabel {{
    background: transparent;
    padding: 0px;
}}

QLabel#title {{
    font-size: {FONT_SIZE_TITLE};
    font-weight: 700;
    color: {TEXT_PRIMARY};
}}

QLabel#subtitle {{
    font-size: {FONT_SIZE_MD};
    color: {TEXT_SECONDARY};
}}

QLabel#status {{
    font-size: {FONT_SIZE_LG};
    font-weight: 600;
    padding: 8px 16px;
    border-radius: {RADIUS_MD};
    background-color: {BG_CARD};
    border: 1px solid {BORDER};
}}

/* ── Push Buttons ─────────────────────────────────────────────────────── */
QPushButton {{
    background-color: {BG_CARD};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER};
    border-radius: {RADIUS_MD};
    padding: 10px 20px;
    font-size: {FONT_SIZE_MD};
    font-weight: 600;
    min-height: 20px;
}}

QPushButton:hover {{
    background-color: {BG_HOVER};
    border-color: {ACCENT_PRIMARY};
}}

QPushButton:pressed {{
    background-color: {ACCENT_PRIMARY};
    color: white;
}}

QPushButton:disabled {{
    background-color: {BG_DARK};
    color: {TEXT_DISABLED};
    border-color: {BG_DARK};
}}

QPushButton#btn_start {{
    background-color: {ACCENT_PRIMARY};
    color: white;
    border: none;
}}

QPushButton#btn_start:hover {{
    background-color: #5A8AFF;
}}

QPushButton#btn_stop {{
    background-color: {ACCENT_DANGER};
    color: white;
    border: none;
}}

QPushButton#btn_stop:hover {{
    background-color: #F87171;
}}

QPushButton#btn_record {{
    background-color: {BG_CARD};
    color: {ACCENT_SUCCESS};
    border: 1px solid {ACCENT_SUCCESS};
}}

QPushButton#btn_record:checked {{
    background-color: {ACCENT_SUCCESS};
    color: white;
}}

/* ── Spin Boxes / Line Edits ──────────────────────────────────────────── */
QSpinBox, QDoubleSpinBox, QLineEdit {{
    background-color: {BG_INPUT};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER};
    border-radius: {RADIUS_SM};
    padding: 6px 10px;
    font-size: {FONT_SIZE_MD};
}}

QSpinBox:focus, QDoubleSpinBox:focus, QLineEdit:focus {{
    border-color: {ACCENT_PRIMARY};
}}

/* ── Combo Boxes ──────────────────────────────────────────────────────── */
QComboBox {{
    background-color: {BG_INPUT};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER};
    border-radius: {RADIUS_SM};
    padding: 6px 10px;
    font-size: {FONT_SIZE_MD};
}}

QComboBox:focus {{
    border-color: {ACCENT_PRIMARY};
}}

QComboBox QAbstractItemView {{
    background-color: {BG_CARD};
    color: {TEXT_PRIMARY};
    selection-background-color: {ACCENT_PRIMARY};
    border: 1px solid {BORDER};
}}

/* ── Tab Widget ───────────────────────────────────────────────────────── */
QTabWidget::pane {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: {RADIUS_MD};
    padding: 12px;
}}

QTabBar::tab {{
    background-color: {BG_DARK};
    color: {TEXT_SECONDARY};
    border: 1px solid {BORDER};
    border-bottom: none;
    border-top-left-radius: {RADIUS_SM};
    border-top-right-radius: {RADIUS_SM};
    padding: 8px 18px;
    margin-right: 2px;
    font-weight: 600;
}}

QTabBar::tab:selected {{
    background-color: {BG_CARD};
    color: {ACCENT_PRIMARY};
    border-color: {ACCENT_PRIMARY};
    border-bottom: 2px solid {BG_CARD};
}}

QTabBar::tab:hover:!selected {{
    background-color: {BG_HOVER};
    color: {TEXT_PRIMARY};
}}

/* ── Check Boxes ──────────────────────────────────────────────────────── */
QCheckBox {{
    spacing: 8px;
    background: transparent;
}}

QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border-radius: {RADIUS_SM};
    border: 2px solid {BORDER};
    background-color: {BG_INPUT};
}}

QCheckBox::indicator:checked {{
    background-color: {ACCENT_PRIMARY};
    border-color: {ACCENT_PRIMARY};
}}

/* ── Group Boxes ──────────────────────────────────────────────────────── */
QGroupBox {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: {RADIUS_MD};
    margin-top: 16px;
    padding: 16px;
    padding-top: 28px;
    font-weight: 600;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 4px 12px;
    color: {ACCENT_PRIMARY};
    font-size: {FONT_SIZE_MD};
}}

/* ── Scroll Bars ──────────────────────────────────────────────────────── */
QScrollBar:vertical {{
    background: {BG_DARK};
    width: 8px;
    border-radius: 4px;
}}

QScrollBar::handle:vertical {{
    background: {BORDER};
    border-radius: 4px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background: {TEXT_DISABLED};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

/* ── Dialog ───────────────────────────────────────────────────────────── */
QDialog {{
    background-color: {BG_DARKEST};
}}

/* ── Splitter ─────────────────────────────────────────────────────────── */
QSplitter::handle {{
    background-color: {BORDER};
    width: 2px;
}}

QSplitter::handle:hover {{
    background-color: {ACCENT_PRIMARY};
}}

/* ── Status Bar ───────────────────────────────────────────────────────── */
QStatusBar {{
    background-color: {BG_DARK};
    color: {TEXT_SECONDARY};
    border-top: 1px solid {BORDER};
    font-size: {FONT_SIZE_SM};
    padding: 4px;
}}
"""
