import platform

import customtkinter as ctk

if platform.system() == "Windows":
    FONT_FAMILY = "Segoe UI"
    MONO_FAMILY = "Consolas"
elif platform.system() == "Darwin":
    FONT_FAMILY = "SF Pro"
    MONO_FAMILY = "Menlo"
else:
    FONT_FAMILY = "Ubuntu"
    MONO_FAMILY = "Liberation Mono"

FONTS = {
    "title": (FONT_FAMILY, 22, "bold"),
    "heading": (FONT_FAMILY, 16, "bold"),
    "body": (FONT_FAMILY, 13),
    "small": (FONT_FAMILY, 11),
    "mono": (MONO_FAMILY, 12),
}

COLORS = {
    "dark": {
        "bg": "#1a1a2e",
        "card": "#16213e",
        "card_border": "#0f3460",
        "accent": "#e94560",
        "accent_hover": "#ff6b81",
        "text": "#e0e0e0",
        "text_secondary": "#a0a0a0",
        "success": "#2ecc71",
        "warning": "#f39c12",
        "danger": "#e74c3c",
    },
    "light": {
        "bg": "#f0f2f5",
        "card": "#ffffff",
        "card_border": "#dcdde1",
        "accent": "#e94560",
        "accent_hover": "#d63031",
        "text": "#2d3436",
        "text_secondary": "#636e72",
        "success": "#27ae60",
        "warning": "#e67e22",
        "danger": "#c0392b",
    },
}


def apply_theme(theme_name: str):
    if theme_name == "dark":
        ctk.set_appearance_mode("dark")
    else:
        ctk.set_appearance_mode("light")
