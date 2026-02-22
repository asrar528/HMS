"""
Base Window – common helpers shared by all HMS windows.
"""

from __future__ import annotations

import customtkinter as ctk


# ---------------------------------------------------------------------------
# Application-wide theme configuration
# ---------------------------------------------------------------------------

APP_COLOR_THEME = "blue"        # or "green" / "dark-blue"
APP_APPEARANCE   = "light"      # or "dark" / "system"

FONT_TITLE  = ("Segoe UI", 22, "bold")
FONT_HEADER = ("Segoe UI", 14, "bold")
FONT_LABEL  = ("Segoe UI", 12)
FONT_INPUT  = ("Segoe UI", 12)
FONT_BUTTON = ("Segoe UI", 12, "bold")
FONT_SMALL  = ("Segoe UI", 10)

COLOR_HEADER_BG  = "#1565C0"      # deep blue header bar
COLOR_HEADER_FG  = "#FFFFFF"
COLOR_ACCENT     = "#1976D2"
COLOR_SUCCESS    = "#2E7D32"
COLOR_ERROR      = "#C62828"
COLOR_WARN       = "#E65100"
COLOR_SECTION_BG = "#E3F2FD"      # light-blue section strip
COLOR_CARD_BG    = "#F5F5F5"


def apply_theme() -> None:
    ctk.set_appearance_mode(APP_APPEARANCE)
    ctk.set_default_color_theme(APP_COLOR_THEME)


class BaseWindow(ctk.CTk):
    """
    Top-level window base class.

    Provides:
    - Centred-on-screen placement
    - Standard icon / title helpers
    - Reusable widget factory methods
    """

    def __init__(self, title: str = "HMS", width: int = 1200, height: int = 750) -> None:
        super().__init__()
        self.title(title)
        self._centre(width, height)
        self.resizable(True, True)
        self.minsize(900, 600)

    # ------------------------------------------------------------------
    # Layout helpers
    # ------------------------------------------------------------------

    def _centre(self, w: int, h: int) -> None:
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    # ------------------------------------------------------------------
    # Widget factories
    # ------------------------------------------------------------------

    @staticmethod
    def make_section_label(parent, text: str) -> ctk.CTkLabel:
        """Renders a horizontal section-header strip."""
        return ctk.CTkLabel(
            parent,
            text=f"  {text}",
            font=FONT_HEADER,
            fg_color=COLOR_SECTION_BG,
            text_color=COLOR_ACCENT,
            anchor="w",
            corner_radius=4,
            height=32,
        )

    @staticmethod
    def make_label(parent, text: str, required: bool = False) -> ctk.CTkLabel:
        lbl = f"{text} *" if required else text
        return ctk.CTkLabel(parent, text=lbl, font=FONT_LABEL, anchor="w")

    @staticmethod
    def make_entry(parent, placeholder: str = "", width: int = 260) -> ctk.CTkEntry:
        return ctk.CTkEntry(
            parent,
            placeholder_text=placeholder,
            font=FONT_INPUT,
            width=width,
            height=36,
            corner_radius=6,
        )

    @staticmethod
    def make_combo(parent, values: list, width: int = 260) -> ctk.CTkComboBox:
        return ctk.CTkComboBox(
            parent,
            values=values,
            font=FONT_INPUT,
            width=width,
            height=36,
            corner_radius=6,
            state="readonly",
        )

    @staticmethod
    def make_button(
        parent,
        text: str,
        command,
        color: str = COLOR_ACCENT,
        width: int = 140,
    ) -> ctk.CTkButton:
        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            font=FONT_BUTTON,
            fg_color=color,
            hover_color=_darken(color),
            width=width,
            height=40,
            corner_radius=8,
        )


class TopHeaderBar(ctk.CTkFrame):
    """A branded header strip displayed at the top of every window."""

    def __init__(self, parent, title: str, subtitle: str = "") -> None:
        super().__init__(parent, fg_color=COLOR_HEADER_BG, height=72, corner_radius=0)
        self.pack_propagate(False)

        ctk.CTkLabel(
            self,
            text="🏥  " + title,
            font=FONT_TITLE,
            text_color=COLOR_HEADER_FG,
        ).pack(side="left", padx=20, pady=10)

        if subtitle:
            ctk.CTkLabel(
                self,
                text=subtitle,
                font=FONT_SMALL,
                text_color="#BBDEFB",
            ).pack(side="left", padx=6)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _darken(hex_color: str) -> str:
    """Return a slightly darker shade of the given hex colour."""
    try:
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        factor = 0.80
        return f"#{int(r*factor):02X}{int(g*factor):02X}{int(b*factor):02X}"
    except Exception:
        return hex_color
