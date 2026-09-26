"""
Unit tests for SoftWork PySide6 / Qt6 Modern CAD IDE components.
"""
from __future__ import annotations
import unittest

from softwork.core.document import Document
from softwork.ai.agent import CADAgent
from softwork.qt.styles import DARK_IDE_STYLE


class TestQtIDEComponents(unittest.TestCase):
    """
    Validates PySide6 CAD styles, document integration, and Qt component architecture.
    """

    def test_qss_style_presence(self) -> None:
        self.assertIn("QMainWindow", DARK_IDE_STYLE)
        self.assertIn("#00F0FF", DARK_IDE_STYLE)
        self.assertIn("border-radius", DARK_IDE_STYLE)

    def test_qt_document_and_agent_binding(self) -> None:
        doc = Document(name="TestPart.softwork")
        agent = CADAgent(doc)
        self.assertEqual(doc.name, "TestPart.softwork")
        self.assertEqual(len(doc.active_part.features), 0)


if __name__ == "__main__":
    unittest.main()
