"""
Professional CAD QSS Stylesheets and Design Tokens for SoftWork (PTC Creo & SolidWorks aesthetic).
Text-first, clean engineering layout with high readability and zero icon clutter.
"""
from __future__ import annotations


DARK_IDE_STYLE = """
/* Global Reset & Base (SolidWorks Dark / PTC Creo Dark Slate) */
QWidget {
    background-color: #1E2228;
    color: #E2E6EC;
    font-family: "Segoe UI", "Segoe UI Variable", -apple-system, BlinkMacSystemFont, "Tahoma", sans-serif;
    font-size: 12px;
    selection-background-color: #007ACC;
    selection-color: #FFFFFF;
}

/* Main Window & Central Container */
QMainWindow {
    background-color: #17191D;
}

/* Menubar */
QMenuBar {
    background-color: #21252C;
    color: #E2E6EC;
    border-bottom: 1px solid #2D323C;
    padding: 2px 6px;
    font-size: 12px;
    font-weight: 500;
}
QMenuBar::item {
    background: transparent;
    padding: 4px 10px;
    border-radius: 2px;
}
QMenuBar::item:selected {
    background-color: #2D323C;
    color: #0098FF;
}
QMenu {
    background-color: #21252C;
    color: #E2E6EC;
    border: 1px solid #3E4552;
    border-radius: 2px;
    padding: 4px 0px;
}
QMenu::item {
    padding: 6px 28px 6px 14px;
}
QMenu::item:selected {
    background-color: #007ACC;
    color: #FFFFFF;
}
QMenu::separator {
    height: 1px;
    background-color: #2D323C;
    margin: 4px 6px;
}

/* Ribbon Tab Bar & CommandManager */
QTabWidget::pane {
    border: 1px solid #2D323C;
    background-color: #21252C;
    top: -1px;
}
QTabBar::tab {
    background-color: #1B1E23;
    color: #9BA4B2;
    border: 1px solid #2D323C;
    border-bottom: none;
    padding: 7px 16px;
    margin-right: 2px;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
QTabBar::tab:selected {
    background-color: #21252C;
    color: #0098FF;
    border-top: 2px solid #0098FF;
    border-bottom: 1px solid #21252C;
}
QTabBar::tab:hover:!selected {
    background-color: #282D36;
    color: #E2E6EC;
}

/* CAD Toolbars & Ribbon Panels */
QToolBar {
    background-color: #21252C;
    border-bottom: 1px solid #2D323C;
    spacing: 5px;
    padding: 4px 8px;
}
QToolButton {
    background-color: #272B33;
    color: #E2E6EC;
    border: 1px solid #3B4250;
    border-radius: 2px;
    padding: 5px 10px;
    font-size: 11px;
    font-weight: 600;
}
QToolButton:hover {
    background-color: #333944;
    border-color: #0098FF;
    color: #0098FF;
}
QToolButton:pressed {
    background-color: #007ACC;
    border-color: #007ACC;
    color: #FFFFFF;
}
QToolButton:checked {
    background-color: #007ACC;
    border-color: #0098FF;
    color: #FFFFFF;
}

/* Push Buttons */
QPushButton {
    background-color: #272B33;
    color: #E2E6EC;
    border: 1px solid #3B4250;
    border-radius: 2px;
    padding: 5px 12px;
    font-size: 11px;
    font-weight: 600;
}
QPushButton:hover {
    background-color: #333944;
    border-color: #0098FF;
    color: #0098FF;
}
QPushButton:pressed {
    background-color: #007ACC;
    color: #FFFFFF;
}
QPushButton#PrimaryButton {
    background-color: #007ACC;
    color: #FFFFFF;
    border: 1px solid #0098FF;
    font-weight: 700;
}
QPushButton#PrimaryButton:hover {
    background-color: #008BE6;
}
QPushButton#PrimaryButton:pressed {
    background-color: #0062A3;
}

/* Input Fields & Textboxes */
QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #17191D;
    color: #E2E6EC;
    border: 1px solid #3B4250;
    border-radius: 2px;
    padding: 5px 8px;
    font-size: 11px;
}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border: 1px solid #0098FF;
    background-color: #1B1E23;
}

/* FeatureManager Design Tree (Model Tree) */
QTreeWidget, QTreeView, QListWidget {
    background-color: #1B1E23;
    color: #E2E6EC;
    border: 1px solid #2D323C;
    border-radius: 2px;
    outline: none;
    padding: 4px;
    font-size: 11px;
}
QTreeWidget::item {
    height: 24px;
    border-radius: 2px;
    padding-left: 4px;
}
QTreeWidget::item:hover {
    background-color: #272B33;
    color: #0098FF;
}
QTreeWidget::item:selected {
    background-color: #007ACC;
    color: #FFFFFF;
    font-weight: 600;
}
QHeaderView::section {
    background-color: #21252C;
    color: #9BA4B2;
    border: none;
    border-bottom: 1px solid #2D323C;
    padding: 4px 8px;
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
}

/* Dock Widgets & Panels */
QDockWidget {
    color: #E2E6EC;
    font-weight: 600;
    titlebar-close-icon: url(none);
    titlebar-normal-icon: url(none);
}
QDockWidget::title {
    background-color: #21252C;
    border-bottom: 1px solid #2D323C;
    padding: 6px 10px;
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    color: #9BA4B2;
}

/* Scrollbars (Compact CAD style) */
QScrollBar:vertical {
    background: #17191D;
    width: 8px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background: #3B4250;
    min-height: 20px;
    border-radius: 2px;
}
QScrollBar::handle:vertical:hover {
    background: #0098FF;
}
QScrollBar:horizontal {
    background: #17191D;
    height: 8px;
    margin: 0px;
}
QScrollBar::handle:horizontal {
    background: #3B4250;
    min-width: 20px;
    border-radius: 2px;
}
QScrollBar::handle:horizontal:hover {
    background: #0098FF;
}

/* Status Bar (SolidWorks / Creo standard) */
QStatusBar {
    background-color: #21252C;
    color: #9BA4B2;
    border-top: 1px solid #2D323C;
    font-size: 11px;
    padding: 3px 8px;
}

/* Splitters */
QSplitter::handle {
    background-color: #2D323C;
}
QSplitter::handle:hover {
    background-color: #0098FF;
}
"""

# Alias for backward-compatibility with test suite
DARK_THEME_STYLE = DARK_IDE_STYLE
