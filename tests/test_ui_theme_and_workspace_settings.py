"""
Unit tests for UI Theme System, Dark/Light Modes, and Custom Workspace Settings.
"""
from __future__ import annotations
import unittest
import tempfile
from pathlib import Path

from softwork.ui.theme import ThemePalette, ThemeManager, DARK_THEME, LIGHT_THEME, CYBERPUNK_THEME, TITANIUM_THEME
from softwork.ui.workspace_settings import WorkspaceSettings, WorkspaceSettingsManager


class TestUIThemeAndWorkspaceSettings(unittest.TestCase):
    """
    Validates theme management, dark/light switching, custom palettes, and workspace settings persistence.
    """

    def test_theme_palettes_tokens(self) -> None:
        self.assertTrue(DARK_THEME.is_dark)
        self.assertFalse(LIGHT_THEME.is_dark)
        self.assertEqual(DARK_THEME.bg_app, "#0B0F19")
        self.assertEqual(LIGHT_THEME.bg_app, "#F1F5F9")
        self.assertEqual(CYBERPUNK_THEME.fg_accent, "#EC4899")
        self.assertEqual(TITANIUM_THEME.viewport_solid, "#94A3B8")

    def test_custom_theme_registration_and_switching(self) -> None:
        manager = ThemeManager()
        custom_palette = ThemePalette(
            name="Emerald Studio",
            is_dark=True,
            bg_app="#022c22",
            bg_panel="#064e3b",
            fg_accent="#10b981",
        )
        manager.register_theme(custom_palette)
        self.assertIn("Emerald Studio", manager.themes)

        notified_palettes = []
        manager.add_listener(lambda p: notified_palettes.append(p.name))

        success = manager.set_theme("Emerald Studio")
        self.assertTrue(success)
        self.assertEqual(manager.current_theme.name, "Emerald Studio")
        self.assertEqual(notified_palettes, ["Emerald Studio"])

    def test_theme_dark_light_toggle(self) -> None:
        manager = ThemeManager()
        manager.set_theme("Studio Dark")
        self.assertTrue(manager.current_theme.is_dark)

        toggled_1 = manager.toggle_dark_light()
        self.assertEqual(toggled_1, "Studio Light")
        self.assertFalse(manager.current_theme.is_dark)

        toggled_2 = manager.toggle_dark_light()
        self.assertEqual(toggled_2, "Studio Dark")
        self.assertTrue(manager.current_theme.is_dark)

    def test_workspace_settings_serialization(self) -> None:
        settings = WorkspaceSettings(
            theme_name="Cyberpunk Neon",
            default_unit="in",
            show_grid=True,
            grid_step=50.0,
            shading_mode="wireframe",
            orbit_sensitivity=0.8,
        )
        d = settings.to_dict()
        self.assertEqual(d["theme_name"], "Cyberpunk Neon")
        self.assertEqual(d["default_unit"], "in")
        self.assertEqual(d["grid_step"], 50.0)
        self.assertEqual(d["shading_mode"], "wireframe")

        restored = WorkspaceSettings.from_dict(d)
        self.assertEqual(restored.theme_name, "Cyberpunk Neon")
        self.assertEqual(restored.default_unit, "in")
        self.assertEqual(restored.grid_step, 50.0)
        self.assertEqual(restored.shading_mode, "wireframe")
        self.assertEqual(restored.orbit_sensitivity, 0.8)

    def test_workspace_settings_file_persistence(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            cfg_dir = Path(tmpdir)
            mgr = WorkspaceSettingsManager(config_dir=cfg_dir)
            self.assertEqual(mgr.settings.theme_name, "Studio Dark")

            custom_cfg = WorkspaceSettings(
                theme_name="Industrial Titanium",
                default_unit="cm",
                grid_step=10.0,
                shading_mode="shaded",
            )
            mgr.save_settings(custom_cfg)

            # Re-read from disk
            mgr2 = WorkspaceSettingsManager(config_dir=cfg_dir)
            self.assertEqual(mgr2.settings.theme_name, "Industrial Titanium")
            self.assertEqual(mgr2.settings.default_unit, "cm")
            self.assertEqual(mgr2.settings.grid_step, 10.0)
            self.assertEqual(mgr2.settings.shading_mode, "shaded")


if __name__ == "__main__":
    unittest.main()
