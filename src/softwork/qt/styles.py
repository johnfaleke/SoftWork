"""
Modern QSS Stylesheets and Design Tokens for SoftWork PySide6 / Qt6 CAD IDE.
"""
from __future__ import annotations


DARK_IDE_STYLE = """
/* Global Reset & Base */
QWidget {
    background-color: #0A0A0A;
    color: #FFFFFF;
    font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, "Roboto", sans-serif;
    font-size: 13px;
    selection-background-color: #00F0FF;
    selection-color: #000000;
}

/* Main Window & Central Container */
QMainWindow {
    background-color: #000000;
}

/* Menubar */
QMenuBar {
    background-color: #0C0C0C;
    color: #E2E8F0;
    border-bottom: 1px solid #1E1E1E;
    padding: 2px 6px;
}
QMenuBar::item {
    background: transparent;
    padding: 4px 8px;
    border-radius: 4px;
}
QMenuBar::item:selected {
    background-color: #1F1F1F;
    color: #00F0FF;
}
QMenu {
    background-color: #121212;
    color: #FFFFFF;
    border: 1px solid #282828;
    border-radius: 6px;
    padding: 4px 0px;
}
QMenu::item {
    padding: 6px 24px 6px 12px;
}
QMenu::item:selected {
    background-color: #00F0FF;
    color: #000000;
    font-weight: bold;
}
QMenu::separator {
    height: 1px;
    background-color: #242424;
    margin: 4px 8px;
}

/* Toolbars & Ribbon */
QToolBar {
    background-color: #0C0C0C;
    border-bottom: 1px solid #1E1E1E;
    spacing: 6px;
    padding: 4px 8px;
}
QToolButton {
    background-color: #181818;
    color: #F1F5F9;
    border: 1px solid #282828;
    border-radius: 6px;
    padding: 5px 10px;
    font-size: 12px;
    font-weight: 500;
}
QToolButton:hover {
    background-color: #242424;
    border-color: #00F0FF;
    color: #00F0FF;
}
QToolButton:pressed {
    background-color: #00F0FF;
    color: #000000;
}

/* Push Buttons */
QPushButton {
    background-color: #181818;
    color: #FFFFFF;
    border: 1px solid #2A2A2A;
    border-radius: 6px;
    padding: 6px 14px;
    font-size: 12px;
    font-weight: 500;
}
QPushButton:hover {
    background-color: #262626;
    border-color: #00F0FF;
    color: #00F0FF;
}
QPushButton:pressed {
    background-color: #00F0FF;
    color: #000000;
    font-weight: bold;
}
QPushButton#AccentButton {
    background-color: #00F0FF;
    color: #000000;
    border: none;
    font-weight: bold;
}
QPushButton#AccentButton:hover {
    background-color: #33F3FF;
}
QPushButton#AccentButton:pressed {
    background-color: #00B8C4;
}

/* Input Fields & Textboxes */
QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #141414;
    color: #FFFFFF;
    border: 1px solid #262626;
    border-radius: 6px;
    padding: 6px 8px;
    font-size: 12px;
}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border: 1px solid #00F0FF;
    background-color: #181818;
}

/* Tree & List Views (Model Tree) */
QTreeWidget, QTreeView, QListWidget {
    background-color: #0E0E0E;
    color: #F8FAFC;
    border: 1px solid #1F1F1F;
    border-radius: 6px;
    outline: none;
    padding: 4px;
}
QTreeWidget::item {
    height: 28px;
    border-radius: 4px;
    padding-left: 4px;
}
QTreeWidget::item:hover {
    background-color: #1A1A1A;
    color: #00F0FF;
}
QTreeWidget::item:selected {
    background-color: #00F0FF;
    color: #000000;
    font-weight: bold;
}
QHeaderView::section {
    background-color: #121212;
    color: #A1A1AA;
    border: none;
    border-bottom: 1px solid #222222;
    padding: 4px 8px;
    font-size: 11px;
    font-weight: bold;
    text-transform: uppercase;
}

/* Dock Widgets & Panels */
QDockWidget {
    color: #00F0FF;
    font-weight: bold;
    titlebar-close-icon: url(none);
    titlebar-normal-icon: url(none);
}
QDockWidget::title {
    background-color: #121212;
    border-bottom: 1px solid #1E1E1E;
    padding: 6px 10px;
    font-size: 11px;
    font-weight: bold;
    text-transform: uppercase;
    color: #A1A1AA;
}

/* Scrollbars */
QScrollBar:vertical {
    background: #0C0C0C;
    width: 8px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background: #282828;
    min-height: 20px;
    border-radius: 4px;
}
QScrollBar::handle:vertical:hover {
    background: #00F0FF;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
QScrollBar:horizontal {
    background: #0C0C0C;
    height: 8px;
    margin: 0px;
}
QScrollBar::handle:horizontal {
    background: #282828;
    min-width: 20px;
    border-radius: 4px;
}
QScrollBar::handle:horizontal:hover {
    background: #00F0FF;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* Status Bar */
QStatusBar {
    background-color: #0C0C0C;
    color: #94A3B8;
    border-top: 1px solid #1E1E1E;
    font-size: 11px;
    padding: 2px 8px;
}

/* Splitters */
QSplitter::handle {
    background-color: #161616;
}
QSplitter::handle:hover {
    background-color: #00F0FF;
}
"""
