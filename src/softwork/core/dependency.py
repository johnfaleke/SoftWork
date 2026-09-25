"""
Parametric feature dependency graph and topological evaluation.
"""
from __future__ import annotations
from typing import Dict, Set, List, Optional


class DependencyGraph:
    """
    Directed Acyclic Graph (DAG) managing dependencies between CAD features.
    """

    def __init__(self) -> None:
        self._adj: Dict[str, Set[str]] = {}  # feature -> set of features it depends on
        self._rev_adj: Dict[str, Set[str]] = {}  # feature -> set of features that depend on it

    def add_node(self, node_id: str) -> None:
        if node_id not in self._adj:
            self._adj[node_id] = set()
        if node_id not in self._rev_adj:
            self._rev_adj[node_id] = set()

    def remove_node(self, node_id: str) -> None:
        if node_id in self._adj:
            for dep in self._adj[node_id]:
                if dep in self._rev_adj:
                    self._rev_adj[dep].discard(node_id)
            del self._adj[node_id]

        if node_id in self._rev_adj:
            for dependent in self._rev_adj[node_id]:
                if dependent in self._adj:
                    self._adj[dependent].discard(node_id)
            del self._rev_adj[node_id]

    def add_dependency(self, child_id: str, parent_id: str) -> None:
        """Indicates child_id depends on parent_id (e.g. Extrude depends on Sketch)."""
        self.add_node(child_id)
        self.add_node(parent_id)

        # Check for cycle before adding
        if self._creates_cycle(child_id, parent_id):
            raise ValueError(f"Adding dependency from '{child_id}' to '{parent_id}' would create a cyclic dependency")

        self._adj[child_id].add(parent_id)
        self._rev_adj[parent_id].add(child_id)

    def remove_dependency(self, child_id: str, parent_id: str) -> None:
        if child_id in self._adj:
            self._adj[child_id].discard(parent_id)
        if parent_id in self._rev_adj:
            self._rev_adj[parent_id].discard(child_id)

    def get_dependencies(self, node_id: str) -> Set[str]:
        """Returns the features that node_id depends on."""
        return set(self._adj.get(node_id, set()))

    def get_dependents(self, node_id: str) -> Set[str]:
        """Returns the features that depend directly or indirectly on node_id."""
        visited: Set[str] = set()
        queue = list(self._rev_adj.get(node_id, set()))
        while queue:
            curr = queue.pop(0)
            if curr not in visited:
                visited.add(curr)
                queue.extend(self._rev_adj.get(curr, set()))
        return visited

    def topological_sort(self) -> List[str]:
        """
        Returns all nodes in topological evaluation order (parents before children).
        """
        in_degree: Dict[str, int] = {node: len(self._adj[node]) for node in self._adj}
        queue = [node for node, deg in in_degree.items() if deg == 0]
        sorted_nodes: List[str] = []

        while queue:
            curr = queue.pop(0)
            sorted_nodes.append(curr)

            for dependent in self._rev_adj.get(curr, set()):
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

        if len(sorted_nodes) != len(self._adj):
            raise ValueError("Dependency graph contains a cycle")

        return sorted_nodes

    def _creates_cycle(self, child_id: str, parent_id: str) -> bool:
        # If parent_id already depends on child_id, adding child_id -> parent_id causes a cycle
        dependents = self.get_dependents(child_id)
        return parent_id in dependents or parent_id == child_id
