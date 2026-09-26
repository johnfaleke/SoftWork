"""
Modern Theme & Design System for SoftWork Desktop CAD.
Provides ThemePalette dataclass, built-in themes (Dark, Light, Cyberpunk, Titanium), and ThemeManager.
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
    
    # App & Surface Backgrounds
    bg_app: str = "#0B0F19"
    bg_panel: str = "#0F172A"
    bg_card: str = "#1E293B"
    bg_input: str = "#1E293B"
    bg_hover: str = "#334155"
    
    # Borders & Separators
    border: str = "#334155"
    border_focus: str = "#38BDF8"
    
    # Typography & Foreground
    fg_primary: str = "#F8FAFC"
    fg_secondary: str = "#94A3B8"
    fg_muted: str = "#64748B"
    fg_accent: str = "#38BDF8"
    
    # Action & Button Accents
    accent_btn_bg: str = "#0284C7"
    accent_btn_hover: str = "#0369A1"
    accent_btn_fg: str = "#FFFFFF"
    
    # 3D Viewport Specific Colors
    viewport_bg: str = "#0F172A"
    viewport_grid: str = "#1E293B"
    viewport_grid_major: str = "#334155"
    viewport_solid: str = "#38BDF8"
    viewport_solid_outline: str = "#0284C7"
    viewport_edge: str = "#38BDF8"
    viewport_selected_face: str = "#F59E0B"
    viewport_selected_outline: str = "#FBBF24"
    viewport_ghost_mesh: str = "#F59E0B"
    viewport_sketch_line: str = "#10B981"
    viewport_sketch_point: str = "#34D399"
    viewport_hud_bg: str = "#1E293B"
    viewport_hud_border: str = "#F59E0B"
    
    # Status Indicators
    color_success: str = "#10B981"
    color_warning: str = "#F59E0B"
    color_error: str = "#EF4444"
    color_info: str = "#38BDF8"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ThemePalette:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


DARK_THEME = ThemePalette(
    name="Studio Dark",
    is_dark=True,
    bg_app="#0B0F19",
    bg_panel="#0F172A",
    bg_card="#1E293B",
    bg_input="#1E293B",
    bg_hover="#334155",
    border="#334155",
    border_focus="#38BDF8",
    fg_primary="#F8FAFC",
    fg_secondary="#94A3B8",
    fg_muted="#64748B",
    fg_accent="#38BDF8",
    accent_btn_bg="#0284C7",
    accent_btn_hover="#0369A1",
    accent_btn_fg="#FFFFFF",
    viewport_bg="#0F172A",
    viewport_grid="#1E293B",
    viewport_grid_major="#334155",
    viewport_solid="#38BDF8",
    viewport_solid_outline="#0284C7",
    viewport_edge="#38BDF8",
    viewport_selected_face="#F59E0B",
    viewport_selected_outline="#FBBF24",
    viewport_ghost_mesh="#F59E0B",
    viewport_sketch_line="#10B981",
    viewport_sketch_point="#34D399",
    viewport_hud_bg="#1E293B",
    viewport_hud_border="#F59E0B",
)

LIGHT_THEME = ThemePalette(
    name="Studio Light",
    is_dark=False,
    bg_app="#F1F5F9",
    bg_panel="#FFFFFF",
    bg_card="#F8FAFC",
    bg_input="#FFFFFF",
    bg_hover="#E2E8F0",
    border="#CBD5E1",
    border_focus="#0284C7",
    fg_primary="#0F172A",
    fg_secondary="#475569",
    fg_muted="#94A3B8",
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

CYBERPUNK_THEME = ThemePalette(
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
    accent_btn_bg="#D946EF",
    accent_btn_hover="#C026D3",
    accent_btn_fg="#FFFFFF",
    viewport_bg="#070814",
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

TITANIUM_THEME = ThemePalette(
    name="Industrial Titanium",
    is_dark=True,
    bg_app="#18181B",
    bg_panel="#27272A",
    bg_card="#3F3F46",
    bg_input="#27272A",
    bg_hover="#52525B",
    border="#52525B",
    border_focus="#FB923C",
    fg_primary="#FAFAFA",
    fg_secondary="#D4D4D8",
    fg_muted="#A1A1AA",
    fg_accent="#FB923C",
    accent_btn_bg="#EA580C",
    accent_btn_hover="#C2410C",
    accent_btn_fg="#FFFFFF",
    viewport_bg="#18181B",
    viewport_grid="#27272A",
    viewport_grid_major="#3F3F46",
    viewport_solid="#94A3B8",
    viewport_solid_outline="#64748B",
    viewport_edge="#FB923C",
    viewport_selected_face="#F97316",
    viewport_selected_outline="#EA580C",
    viewport_ghost_mesh="#EAB308",
    viewport_sketch_line="#38BDF8",
    viewport_sketch_point="#7DD3FC",
    viewport_hud_bg="#27272A",
    viewport_hud_border="#FB923C",
)


class ThemeManager:
    """
    Manages active application theme, custom themes, and notifies UI listeners of theme switches.
    """
    _instance: Optional[ThemeManager] = None

    def __init__(self) -> None:
        self.themes: Dict[str, ThemePalette] = {
            "Studio Dark": DARK_THEME,
            "Studio Light": LIGHT_THEME,
            "Cyberpunk Neon": CYBERPUNK_THEME,
            "Industrial Titanium": TITANIUM_THEME,
        }
        self.active_theme_name: str = "Studio Dark"
        self._listeners: List[Callable[[ThemePalette], None]] = []

    @classmethod
    def get_instance(cls) -> ThemeManager:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @property
    def current_theme(self) -> ThemePalette:
        return self.themes.get(self.active_theme_name, DARK_THEME)

    def register_theme(self, palette: ThemePalette) -> None:
        self.themes[palette.name] = palette

    def set_theme(self, theme_name: str) -> bool:
        if theme_name in self.themes:
            self.active_theme_name = theme_name
            self._notify_listeners()
            return True
        return False

    def toggle_dark_light(self) -> str:
        """Toggles between Studio Dark and Studio Light."""
        if self.current_theme.is_dark:
            self.set_theme("Studio Light")
        else:
            self.set_theme("Studio Dark")
        return self.active_theme_name

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
