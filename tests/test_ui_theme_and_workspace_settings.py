"""
Unit tests for UI Theme System, Dark/Light Modes, and Custom Workspace Settings.
"""
from __future__ import annotations
import unittest
import tempfile
from pathlib import Path

from softwork.ui.theme import (
    ThemePalette,
    ThemeManager,
    DARK_THEME,
    LIGHT_THEME,
    OBSIDIAN_PITCH,
    MONOCHROME_CHARCOAL,
    STUDIO_LIGHT,
    CYBERPUNK_NEON,
    INDUSTRIAL_TITANIUM,
    FOREST_SAGE,
    SOLARIZED_DARK,
)
from softwork.ui.workspace_settings import WorkspaceSettings, WorkspaceSettingsManager


class TestUIThemeAndWorkspaceSettings(unittest.TestCase):
    """
    Validates theme management, 8 theme presets, high-contrast drawing colors, and workspace settings persistence.
    """

    def test_theme_palettes_tokens(self) -> None:
        self.assertTrue(OBSIDIAN_PITCH.is_dark)
        self.assertTrue(MONOCHROME_CHARCOAL.is_dark)
        self.assertFalse(STUDIO_LIGHT.is_dark)
        
        # Verify OLED black & neutral grey tokens
        self.assertEqual(OBSIDIAN_PITCH.bg_app, "#000000")
        self.assertEqual(OBSIDIAN_PITCH.bg_panel, "#0C0C0C")
        self.assertEqual(OBSIDIAN_PITCH.viewport_sketch_line, "#00FF66")
        self.assertEqual(OBSIDIAN_PITCH.viewport_solid, "#00F0FF")

        self.assertEqual(MONOCHROME_CHARCOAL.bg_app, "#121212")
        self.assertEqual(MONOCHROME_CHARCOAL.viewport_edge, "#FFFFFF")

        self.assertEqual(CYBERPUNK_NEON.fg_accent, "#EC4899")
        self.assertEqual(INDUSTRIAL_TITANIUM.viewport_edge, "#FB923C")

    def test_custom_theme_registration_and_switching(self) -> None:
        manager = ThemeManager()
        self.assertEqual(len(manager.themes), 8)
        self.assertIn("Obsidian Pitch (OLED Black)", manager.themes)
        self.assertIn("Monochrome Charcoal", manager.themes)
        self.assertIn("Forest Sage", manager.themes)
        self.assertIn("Solarized Dark", manager.themes)

        custom_palette = ThemePalette(
            name="Emerald Studio",
            is_dark=True,
            bg_app="#000000",
            bg_panel="#0A0A0A",
            fg_accent="#00FF66",
        )
        manager.register_theme(custom_palette)
        self.assertIn("Emerald Studio", manager.themes)

        notified_palettes = []
        manager.add_listener(lambda p: notified_palettes.append(p.name))

        success = manager.set_theme("Emerald Studio")
        self.assertTrue(success)
        self.assertEqual(manager.current_theme.name, "Emerald Studio")
        self.assertEqual(notified_palettes, ["Emerald Studio"])

    def test_theme_switching_across_presets(self) -> None:
        manager = ThemeManager()
        manager.set_theme("Monochrome Charcoal")
        self.assertEqual(manager.current_theme.name, "Monochrome Charcoal")
        self.assertEqual(manager.current_theme.bg_app, "#121212")

        manager.set_theme("Studio Light")
        self.assertFalse(manager.current_theme.is_dark)
        self.assertEqual(manager.current_theme.bg_app, "#F4F4F5")

        manager.set_theme("Obsidian Pitch (OLED Black)")
        self.assertTrue(manager.current_theme.is_dark)
        self.assertEqual(manager.current_theme.bg_app, "#000000")

    def test_workspace_settings_serialization(self) -> None:
        settings = WorkspaceSettings(
            theme_name="Monochrome Charcoal",
            default_unit="in",
            show_grid=True,
            grid_step=50.0,
            shading_mode="wireframe",
            orbit_sensitivity=0.8,
        )
        d = settings.to_dict()
        self.assertEqual(d["theme_name"], "Monochrome Charcoal")
        self.assertEqual(d["default_unit"], "in")
        self.assertEqual(d["grid_step"], 50.0)
        self.assertEqual(d["shading_mode"], "wireframe")

        restored = WorkspaceSettings.from_dict(d)
        self.assertEqual(restored.theme_name, "Monochrome Charcoal")
        self.assertEqual(restored.default_unit, "in")
        self.assertEqual(restored.grid_step, 50.0)
        self.assertEqual(restored.shading_mode, "wireframe")
        self.assertEqual(restored.orbit_sensitivity, 0.8)

    def test_workspace_settings_file_persistence(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            cfg_dir = Path(tmpdir)
            mgr = WorkspaceSettingsManager(config_dir=cfg_dir)
            self.assertEqual(mgr.settings.theme_name, "Obsidian Pitch (OLED Black)")

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
