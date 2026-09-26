"""
Professional CAD QSS Stylesheets and Design Tokens for SoftWork (PTC Creo & SolidWorks aesthetic).
"""
from __future__ import annotations


DARK_IDE_STYLE = """
/* Global Reset & Base (SolidWorks Dark / PTC Creo Dark Slate) */
QWidget {
    background-color: #1E2227;
    color: #DCE1E8;
    font-family: "Segoe UI", "Segoe UI Variable", -apple-system, BlinkMacSystemFont, "Tahoma", sans-serif;
    font-size: 12px;
    selection-background-color: #007ACC;
    selection-color: #FFFFFF;
}

/* Main Window & Central Container */
QMainWindow {
    background-color: #181A1F;
}

/* Menubar */
QMenuBar {
    background-color: #21252B;
    color: #DCE1E8;
    border-bottom: 1px solid #2C313A;
    padding: 1px 4px;
    font-size: 12px;
}
QMenuBar::item {
    background: transparent;
    padding: 4px 8px;
    border-radius: 2px;
}
QMenuBar::item:selected {
    background-color: #2C313A;
    color: #00A8FF;
}
QMenu {
    background-color: #21252B;
    color: #DCE1E8;
    border: 1px solid #3E4451;
    border-radius: 2px;
    padding: 3px 0px;
}
QMenu::item {
    padding: 5px 24px 5px 12px;
}
QMenu::item:selected {
    background-color: #007ACC;
    color: #FFFFFF;
}
QMenu::separator {
    height: 1px;
    background-color: #2C313A;
    margin: 3px 6px;
}

/* Ribbon Tab Bar & CommandManager */
QTabWidget::pane {
    border: 1px solid #2C313A;
    background-color: #21252B;
    top: -1px;
}
QTabBar::tab {
    background-color: #1E2227;
    color: #9DA5B4;
    border: 1px solid #2C313A;
    border-bottom: none;
    padding: 6px 14px;
    margin-right: 2px;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
}
QTabBar::tab:selected {
    background-color: #21252B;
    color: #00A8FF;
    border-top: 2px solid #00A8FF;
    border-bottom: 1px solid #21252B;
}
QTabBar::tab:hover:!selected {
    background-color: #282C34;
    color: #DCE1E8;
}

/* CAD Toolbars & Ribbon Panels */
QToolBar {
    background-color: #21252B;
    border-bottom: 1px solid #2C313A;
    spacing: 4px;
    padding: 3px 6px;
}
QToolButton {
    background-color: #282C34;
    color: #DCE1E8;
    border: 1px solid #3E4451;
    border-radius: 3px;
    padding: 4px 8px;
    font-size: 11px;
    font-weight: 500;
}
QToolButton:hover {
    background-color: #353B45;
    border-color: #00A8FF;
    color: #00A8FF;
}
QToolButton:pressed {
    background-color: #007ACC;
    border-color: #007ACC;
    color: #FFFFFF;
}
QToolButton:checked {
    background-color: #007ACC;
    border-color: #00A8FF;
    color: #FFFFFF;
}

/* Push Buttons */
QPushButton {
    background-color: #282C34;
    color: #DCE1E8;
    border: 1px solid #3E4451;
    border-radius: 3px;
    padding: 5px 12px;
    font-size: 11px;
    font-weight: 500;
}
QPushButton:hover {
    background-color: #353B45;
    border-color: #00A8FF;
    color: #00A8FF;
}
QPushButton:pressed {
    background-color: #007ACC;
    color: #FFFFFF;
}
QPushButton#PrimaryButton {
    background-color: #007ACC;
    color: #FFFFFF;
    border: 1px solid #00A8FF;
    font-weight: 600;
}
QPushButton#PrimaryButton:hover {
    background-color: #0088DD;
}
QPushButton#PrimaryButton:pressed {
    background-color: #0060A0;
}

/* Input Fields & Textboxes */
QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #181A1F;
    color: #DCE1E8;
    border: 1px solid #3E4451;
    border-radius: 2px;
    padding: 4px 6px;
    font-size: 11px;
}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border: 1px solid #00A8FF;
    background-color: #1E2227;
}

/* FeatureManager Design Tree (Model Tree) */
QTreeWidget, QTreeView, QListWidget {
    background-color: #1E2227;
    color: #DCE1E8;
    border: 1px solid #2C313A;
    border-radius: 2px;
    outline: none;
    padding: 2px;
    font-size: 11px;
}
QTreeWidget::item {
    height: 24px;
    border-radius: 2px;
    padding-left: 2px;
}
QTreeWidget::item:hover {
    background-color: #282C34;
    color: #00A8FF;
}
QTreeWidget::item:selected {
    background-color: #007ACC;
    color: #FFFFFF;
    font-weight: 600;
}
QHeaderView::section {
    background-color: #21252B;
    color: #8B949E;
    border: none;
    border-bottom: 1px solid #2C313A;
    padding: 3px 6px;
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
}

/* Dock Widgets & Panels */
QDockWidget {
    color: #DCE1E8;
    font-weight: 600;
    titlebar-close-icon: url(none);
    titlebar-normal-icon: url(none);
}
QDockWidget::title {
    background-color: #21252B;
    border-bottom: 1px solid #2C313A;
    padding: 5px 8px;
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
    color: #8B949E;
}

/* Scrollbars (Compact CAD style) */
QScrollBar:vertical {
    background: #181A1F;
    width: 8px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background: #3E4451;
    min-height: 20px;
    border-radius: 2px;
}
QScrollBar::handle:vertical:hover {
    background: #00A8FF;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
QScrollBar:horizontal {
    background: #181A1F;
    height: 8px;
    margin: 0px;
}
QScrollBar::handle:horizontal {
    background: #3E4451;
    min-width: 20px;
    border-radius: 2px;
}
QScrollBar::handle:horizontal:hover {
    background: #00A8FF;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* Status Bar (SolidWorks / Creo standard) */
QStatusBar {
    background-color: #21252B;
    color: #8B949E;
    border-top: 1px solid #2C313A;
    font-size: 11px;
    padding: 2px 6px;
}

/* Splitters */
QSplitter::handle {
    background-color: #2C313A;
}
QSplitter::handle:hover {
    background-color: #00A8FF;
}
"""

# Alias for backward-compatibility with test suite
DARK_THEME_STYLE = DARK_IDE_STYLE
