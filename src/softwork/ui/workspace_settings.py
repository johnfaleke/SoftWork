"""
Workspace Settings and Preferences for SoftWork CAD.
Handles units, grid configuration, viewport rendering options, camera sensitivity, and JSON persistence.
"""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional
import json
import os
from pathlib import Path


@dataclass
class WorkspaceSettings:
    """
    User customizable workspace settings and preferences.
    """
    theme_name: str = "Studio Dark"
    default_unit: str = "mm"
    
    # Viewport & Grid Settings
    show_grid: bool = True
    grid_step: float = 20.0
    grid_size: float = 140.0
    show_axes: bool = True
    axes_position: str = "bottom_left"  # "bottom_left", "top_right", "none"
    shading_mode: str = "shaded_edges"  # "shaded_edges", "shaded", "wireframe"
    show_ghost_preview: bool = True
    
    # Camera & Interaction
    orbit_sensitivity: float = 0.5
    zoom_sensitivity: float = 1.1
    default_view: str = "isometric"     # "isometric", "front", "top", "right"
    
    # Export & Performance
    stl_binary: bool = True
    auto_recompute: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> WorkspaceSettings:
        valid_keys = cls.__dataclass_fields__.keys()
        filtered = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered)


class WorkspaceSettingsManager:
    """
    Manages loading, saving, and querying persistent workspace preferences.
    """
    _instance: Optional[WorkspaceSettingsManager] = None

    def __init__(self, config_dir: Optional[Path] = None) -> None:
        if config_dir is None:
            config_dir = Path.home() / ".softwork"
        self.config_dir: Path = Path(config_dir)
        self.config_file: Path = self.config_dir / "workspace_settings.json"
        self.settings: WorkspaceSettings = self.load_settings()

    @classmethod
    def get_instance(cls) -> WorkspaceSettingsManager:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def load_settings(self) -> WorkspaceSettings:
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return WorkspaceSettings.from_dict(data)
            except Exception:
                pass
        return WorkspaceSettings()

    def save_settings(self, settings: Optional[WorkspaceSettings] = None) -> None:
        if settings is not None:
            self.settings = settings
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.settings.to_dict(), f, indent=2)
        except Exception:
            pass
