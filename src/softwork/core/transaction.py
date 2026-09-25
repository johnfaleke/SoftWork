"""
Undo, Redo, and AI Transaction boundaries.
"""
from __future__ import annotations
import uuid
import datetime
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable


@dataclass
class TransactionChange:
    description: str
    undo_action: Callable[[], None]
    redo_action: Callable[[], None]


@dataclass
class AITransaction:
    """
    Encapsulates all changes performed during a single AI prompt or user operation.
    Supports preview, validation, auditability, and atomic rollback.
    """
    id: str = field(default_factory=lambda: f"tx_{uuid.uuid4().hex[:8]}")
    title: str = "CAD Operation"
    prompt: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.datetime.now().isoformat())
    changes: List[TransactionChange] = field(default_factory=list)
    affected_features: List[str] = field(default_factory=list)
    preserved_features: List[str] = field(default_factory=list)
    validation_status: str = "pending"
    is_committed: bool = False

    def rollback(self) -> None:
        for change in reversed(self.changes):
            change.undo_action()
        self.is_committed = False

    def apply(self) -> None:
        for change in self.changes:
            change.redo_action()
        self.is_committed = True


class HistoryManager:
    """
    Manages document undo/redo stacks.
    """

    def __init__(self) -> None:
        self._undo_stack: List[AITransaction] = []
        self._redo_stack: List[AITransaction] = []

    @property
    def can_undo(self) -> bool:
        return len(self._undo_stack) > 0

    @property
    def can_redo(self) -> bool:
        return len(self._redo_stack) > 0

    def push_transaction(self, transaction: AITransaction) -> None:
        self._undo_stack.append(transaction)
        self._redo_stack.clear()

    def undo(self) -> Optional[AITransaction]:
        if not self.can_undo:
            return None
        tx = self._undo_stack.pop()
        tx.rollback()
        self._redo_stack.append(tx)
        return tx

    def redo(self) -> Optional[AITransaction]:
        if not self.can_redo:
            return None
        tx = self._redo_stack.pop()
        tx.apply()
        self._undo_stack.append(tx)
        return tx
