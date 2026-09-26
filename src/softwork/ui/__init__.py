"""
SoftWork UI Module.
"""
from softwork.ui.theme import ThemePalette, ThemeManager, DARK_THEME, LIGHT_THEME
from softwork.ui.workspace_settings import WorkspaceSettings, WorkspaceSettingsManager
from softwork.ui.workspace_dialog import WorkspaceSettingsDialog
from softwork.ui.viewport import CAD3DCanvas
from softwork.ui.activity_bar import ActivityBar
from softwork.ui.floating_copilot import FloatingAICopilot
from softwork.ui.main_window import MainWindow

__all__ = [
    "ThemePalette",
    "ThemeManager",
    "DARK_THEME",
    "LIGHT_THEME",
    "WorkspaceSettings",
    "WorkspaceSettingsManager",
    "WorkspaceSettingsDialog",
    "CAD3DCanvas",
    "ActivityBar",
    "FloatingAICopilot",
    "MainWindow",
]
