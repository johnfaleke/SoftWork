"""
Modern Theme & Design System for SoftWork Desktop CAD.
Provides ThemePalette dataclass, rich built-in theme presets (Obsidian Pitch, Monochrome Charcoal,
Studio Light, Nordic Frost, Cyberpunk Neon, Industrial Titanium, Forest Sage, Solarized Dark),
and ThemeManager.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Dict, Any, Callable, List, Optional


@dataclass
class ThemePalette:
    """
    Design tokens and color palette for modern UI components and 3D Viewport.
    """
    name: str
    is_dark: bool = True
    
    # App & Surface Backgrounds (Deep blacks and neutral greys for dark modes)
    bg_app: str = "#080808"
    bg_panel: str = "#121212"
    bg_card: str = "#1A1A1A"
    bg_input: str = "#181818"
    bg_hover: str = "#2A2A2A"
    
    # Borders & Separators
    border: str = "#2E2E2E"
    border_focus: str = "#00F0FF"
    
    # Typography & Foreground
    fg_primary: str = "#FFFFFF"
    fg_secondary: str = "#A1A1AA"
    fg_muted: str = "#71717A"
    fg_accent: str = "#00F0FF"
    
    # Action & Button Accents
    accent_btn_bg: str = "#00F0FF"
    accent_btn_hover: str = "#00B8C4"
    accent_btn_fg: str = "#000000"
    
    # 3D Viewport Specific Colors (High contrast against black/dark grey)
    viewport_bg: str = "#0A0A0A"
    viewport_grid: str = "#1E1E1E"
    viewport_grid_major: str = "#333333"
    viewport_solid: str = "#00F0FF"
    viewport_solid_outline: str = "#008899"
    viewport_edge: str = "#00F0FF"
    viewport_selected_face: str = "#FFB800"
    viewport_selected_outline: str = "#FFE066"
    viewport_ghost_mesh: str = "#FFB800"
    viewport_sketch_line: str = "#00FF66"
    viewport_sketch_point: str = "#66FFA6"
    viewport_hud_bg: str = "#141414"
    viewport_hud_border: str = "#FFB800"
    
    # Status Indicators
    color_success: str = "#00FF66"
    color_warning: str = "#FFB800"
    color_error: str = "#FF3344"
    color_info: str = "#00F0FF"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ThemePalette:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


# 1. True Deep Black & Greys with High-Contrast Cyan/Green
OBSIDIAN_PITCH = ThemePalette(
    name="Obsidian Pitch (OLED Black)",
    is_dark=True,
    bg_app="#000000",
    bg_panel="#0C0C0C",
    bg_card="#161616",
    bg_input="#121212",
    bg_hover="#262626",
    border="#2E2E2E",
    border_focus="#00F0FF",
    fg_primary="#FFFFFF",
    fg_secondary="#A1A1AA",
    fg_muted="#71717A",
    fg_accent="#00F0FF",
    accent_btn_bg="#00E5FF",
    accent_btn_hover="#00B4D8",
    accent_btn_fg="#000000",
    viewport_bg="#050505",
    viewport_grid="#1A1A1A",
    viewport_grid_major="#2E2E2E",
    viewport_solid="#00F0FF",
    viewport_solid_outline="#007788",
    viewport_edge="#00F0FF",
    viewport_selected_face="#FFB800",
    viewport_selected_outline="#FFE066",
    viewport_ghost_mesh="#FFB800",
    viewport_sketch_line="#00FF66",
    viewport_sketch_point="#66FFA6",
    viewport_hud_bg="#111111",
    viewport_hud_border="#FFB800",
)

# 2. Monochrome Charcoal (Neutral greys with stark pure-white CAD geometry)
MONOCHROME_CHARCOAL = ThemePalette(
    name="Monochrome Charcoal",
    is_dark=True,
    bg_app="#121212",
    bg_panel="#181818",
    bg_card="#222222",
    bg_input="#1A1A1A",
    bg_hover="#333333",
    border="#383838",
    border_focus="#FFFFFF",
    fg_primary="#FFFFFF",
    fg_secondary="#CCCCCC",
    fg_muted="#888888",
    fg_accent="#FFFFFF",
    accent_btn_bg="#FFFFFF",
    accent_btn_hover="#D4D4D4",
    accent_btn_fg="#000000",
    viewport_bg="#0F0F0F",
    viewport_grid="#242424",
    viewport_grid_major="#3E3E3E",
    viewport_solid="#E0E0E0",
    viewport_solid_outline="#888888",
    viewport_edge="#FFFFFF",
    viewport_selected_face="#F59E0B",
    viewport_selected_outline="#FBBF24",
    viewport_ghost_mesh="#F59E0B",
    viewport_sketch_line="#10B981",
    viewport_sketch_point="#34D399",
    viewport_hud_bg="#1A1A1A",
    viewport_hud_border="#FFFFFF",
)

# 3. Clean Studio Light
STUDIO_LIGHT = ThemePalette(
    name="Studio Light",
    is_dark=False,
    bg_app="#F4F4F5",
    bg_panel="#FFFFFF",
    bg_card="#F8FAFC",
    bg_input="#FFFFFF",
    bg_hover="#E4E4E7",
    border="#D4D4D8",
    border_focus="#0284C7",
    fg_primary="#18181B",
    fg_secondary="#52525B",
    fg_muted="#A1A1AA",
    fg_accent="#0284C7",
    accent_btn_bg="#0284C7",
    accent_btn_hover="#0369A1",
    accent_btn_fg="#FFFFFF",
    viewport_bg="#F8FAFC",
    viewport_grid="#E2E8F0",
    viewport_grid_major="#CBD5E1",
    viewport_solid="#0284C7",
    viewport_solid_outline="#0369A1",
    viewport_edge="#0284C7",
    viewport_selected_face="#D97706",
    viewport_selected_outline="#B45309",
    viewport_ghost_mesh="#D97706",
    viewport_sketch_line="#059669",
    viewport_sketch_point="#10B981",
    viewport_hud_bg="#FFFFFF",
    viewport_hud_border="#D97706",
)

# 4. Nordic Frost
NORDIC_FROST = ThemePalette(
    name="Nordic Frost",
    is_dark=True,
    bg_app="#0F141C",
    bg_panel="#161F2C",
    bg_card="#1E2B3D",
    bg_input="#161F2C",
    bg_hover="#2B3C52",
    border="#2A3D54",
    border_focus="#38BDF8",
    fg_primary="#F0F8FF",
    fg_secondary="#93C5FD",
    fg_muted="#60A5FA",
    fg_accent="#38BDF8",
    accent_btn_bg="#38BDF8",
    accent_btn_hover="#0284C7",
    accent_btn_fg="#0F172A",
    viewport_bg="#0B1017",
    viewport_grid="#16202E",
    viewport_grid_major="#24344A",
    viewport_solid="#67E8F9",
    viewport_solid_outline="#06B6D4",
    viewport_edge="#38BDF8",
    viewport_selected_face="#FBBF24",
    viewport_selected_outline="#F59E0B",
    viewport_ghost_mesh="#FBBF24",
    viewport_sketch_line="#34D399",
    viewport_sketch_point="#6EE7B7",
    viewport_hud_bg="#161F2C",
    viewport_hud_border="#38BDF8",
)

# 5. Cyberpunk Neon
CYBERPUNK_NEON = ThemePalette(
    name="Cyberpunk Neon",
    is_dark=True,
    bg_app="#05050D",
    bg_panel="#0D0E1A",
    bg_card="#151728",
    bg_input="#1A1C30",
    bg_hover="#282B48",
    border="#2A2D4F",
    border_focus="#EC4899",
    fg_primary="#F0F4FF",
    fg_secondary="#A5B4FC",
    fg_muted="#6366F1",
    fg_accent="#EC4899",
    accent_btn_bg="#EC4899",
    accent_btn_hover="#DB2777",
    accent_btn_fg="#FFFFFF",
    viewport_bg="#06060F",
    viewport_grid="#15172E",
    viewport_grid_major="#24274C",
    viewport_solid="#06B6D4",
    viewport_solid_outline="#0891B2",
    viewport_edge="#EC4899",
    viewport_selected_face="#F43F5E",
    viewport_selected_outline="#FB7185",
    viewport_ghost_mesh="#F59E0B",
    viewport_sketch_line="#A855F7",
    viewport_sketch_point="#C084FC",
    viewport_hud_bg="#0D0E1A",
    viewport_hud_border="#EC4899",
)

# 6. Industrial Titanium
INDUSTRIAL_TITANIUM = ThemePalette(
    name="Industrial Titanium",
    is_dark=True,
    bg_app="#141416",
    bg_panel="#1F1F23",
    bg_card="#2B2B30",
    bg_input="#1F1F23",
    bg_hover="#3B3B42",
    border="#3B3B42",
    border_focus="#FB923C",
    fg_primary="#FAFAFA",
    fg_secondary="#D4D4D8",
    fg_muted="#A1A1AA",
    fg_accent="#FB923C",
    accent_btn_bg="#EA580C",
    accent_btn_hover="#C2410C",
    accent_btn_fg="#FFFFFF",
    viewport_bg="#101012",
    viewport_grid="#222226",
    viewport_grid_major="#383840",
    viewport_solid="#94A3B8",
    viewport_solid_outline="#64748B",
    viewport_edge="#FB923C",
    viewport_selected_face="#F97316",
    viewport_selected_outline="#EA580C",
    viewport_ghost_mesh="#EAB308",
    viewport_sketch_line="#38BDF8",
    viewport_sketch_point="#7DD3FC",
    viewport_hud_bg="#1F1F23",
    viewport_hud_border="#FB923C",
)

# 7. Forest Sage
FOREST_SAGE = ThemePalette(
    name="Forest Sage",
    is_dark=True,
    bg_app="#08100C",
    bg_panel="#0F1A15",
    bg_card="#172620",
    bg_input="#0F1A15",
    bg_hover="#22382F",
    border="#243D33",
    border_focus="#10B981",
    fg_primary="#F0FDF4",
    fg_secondary="#A7F3D0",
    fg_muted="#6EE7B7",
    fg_accent="#10B981",
    accent_btn_bg="#10B981",
    accent_btn_hover="#059669",
    accent_btn_fg="#064E3B",
    viewport_bg="#060C09",
    viewport_grid="#12201A",
    viewport_grid_major="#1E362C",
    viewport_solid="#34D399",
    viewport_solid_outline="#059669",
    viewport_edge="#10B981",
    viewport_selected_face="#F59E0B",
    viewport_selected_outline="#FBBF24",
    viewport_ghost_mesh="#F59E0B",
    viewport_sketch_line="#6EE7B7",
    viewport_sketch_point="#A7F3D0",
    viewport_hud_bg="#0F1A15",
    viewport_hud_border="#10B981",
)

# 8. Solarized Dark
SOLARIZED_DARK = ThemePalette(
    name="Solarized Dark",
    is_dark=True,
    bg_app="#00212B",
    bg_panel="#073642",
    bg_card="#0A4250",
    bg_input="#073642",
    bg_hover="#125666",
    border="#1B6577",
    border_focus="#2AA198",
    fg_primary="#FDF6E3",
    fg_secondary="#93A1A1",
    fg_muted="#657B83",
    fg_accent="#2AA198",
    accent_btn_bg="#268BD2",
    accent_btn_hover="#1F70A8",
    accent_btn_fg="#FFFFFF",
    viewport_bg="#001B24",
    viewport_grid="#083E4C",
    viewport_grid_major="#0E576B",
    viewport_solid="#2AA198",
    viewport_solid_outline="#1B6577",
    viewport_edge="#268BD2",
    viewport_selected_face="#B58900",
    viewport_selected_outline="#CB4B16",
    viewport_ghost_mesh="#D33682",
    viewport_sketch_line="#859900",
    viewport_sketch_point="#B58900",
    viewport_hud_bg="#073642",
    viewport_hud_border="#2AA198",
)

# Keep DARK_THEME as default alias
DARK_THEME = OBSIDIAN_PITCH
LIGHT_THEME = STUDIO_LIGHT


class ThemeManager:
    """
    Manages active application theme, custom themes, and notifies UI listeners of theme switches.
    """
    _instance: Optional[ThemeManager] = None

    def __init__(self) -> None:
        self.themes: Dict[str, ThemePalette] = {
            "Obsidian Pitch (OLED Black)": OBSIDIAN_PITCH,
            "Monochrome Charcoal": MONOCHROME_CHARCOAL,
            "Studio Light": STUDIO_LIGHT,
            "Nordic Frost": NORDIC_FROST,
            "Cyberpunk Neon": CYBERPUNK_NEON,
            "Industrial Titanium": INDUSTRIAL_TITANIUM,
            "Forest Sage": FOREST_SAGE,
            "Solarized Dark": SOLARIZED_DARK,
        }
        self.active_theme_name: str = "Obsidian Pitch (OLED Black)"
        self._listeners: List[Callable[[ThemePalette], None]] = []

    @classmethod
    def get_instance(cls) -> ThemeManager:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @property
    def current_theme(self) -> ThemePalette:
        return self.themes.get(self.active_theme_name, OBSIDIAN_PITCH)

    def register_theme(self, palette: ThemePalette) -> None:
        self.themes[palette.name] = palette

    def set_theme(self, theme_name: str) -> bool:
        if theme_name in self.themes:
            self.active_theme_name = theme_name
            self._notify_listeners()
            return True
        return False

    def add_listener(self, listener: Callable[[ThemePalette], None]) -> None:
        if listener not in self._listeners:
            self._listeners.append(listener)

    def remove_listener(self, listener: Callable[[ThemePalette], None]) -> None:
        if listener in self._listeners:
            self._listeners.remove(listener)

    def _notify_listeners(self) -> None:
        palette = self.current_theme
        for cb in self._listeners:
            try:
                cb(palette)
            except Exception:
                pass
