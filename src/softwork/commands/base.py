"""
Base Command abstraction for SoftWork.
Both manual UI actions and AI tools execute through these command classes.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional

from softwork.core.document import Document
from softwork.core.transaction import AITransaction


class Command(ABC):
    """
    Abstract command interface supporting execution, undo, redo, and transaction logging.
    """

    @abstractmethod
    def execute(self, document: Document) -> AITransaction:
        """Executes command on the document and returns a record of the transaction."""
        pass
