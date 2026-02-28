from typing import Any, List, Optional, Set, Tuple
from collections import defaultdict

from .models import Edge, CheckResult


class EdgeChecker:
    """Validates edges in directed or undirected graphs."""

    def __init__(self, directed: bool = True, allow_self_loops: bool = False):
        self.directed = directed
        self.allow_self_loops = allow_self_loops
        self._edges: List[Edge] = []

    def add_edge(self, source: Any, target: Any, weight: Optional[float] = None) -> None:
        self._edges.append(Edge(source, target, weight))

    def add_edges(self, edges: List[Tuple]) -> None:
        for edge in edges:
            if len(edge) == 2:
                self.add_edge(edge[0], edge[1])
            elif len(edge) == 3:
                self.add_edge(edge[0], edge[1], edge[2])
            else:
                raise ValueError(f"Edge tuple must have 2 or 3 elements, got {len(edge)}")

    def clear(self) -> None:
        self._edges = []

    @property
    def edges(self) -> List[Edge]:
        return list(self._edges)

    def check(self) -> CheckResult:
        errors: List[str] = []
        warnings: List[str] = []

        self._check_self_loops(errors, warnings)
        self._check_duplicates(errors, warnings)
        if self.directed:
            self._check_cycles(warnings)

        valid = len(errors) == 0
        return CheckResult(valid=valid, errors=errors, warnings=warnings)

    def _check_self_loops(self, errors: List[str], warnings: List[str]) -> None:
        for edge in self._edges:
            if edge.source == edge.target:
                msg = f"Self-loop detected at node {edge.source!r}"
                if self.allow_self_loops:
                    warnings.append(msg)
                else:
                    errors.append(msg)

    def _check_duplicates(self, errors: List[str], warnings: List[str]) -> None:
        seen: Set[Tuple] = set()
        for edge in self._edges:
            key = (edge.source, edge.target)
            reverse_key = (edge.target, edge.source)

            if key in seen:
                errors.append(f"Duplicate edge: {edge.source!r} -> {edge.target!r}")
            elif not self.directed and reverse_key in seen:
                errors.append(
                    f"Duplicate undirected edge: {edge.source!r} -- {edge.target!r}"
                )
            else:
                seen.add(key)

    def _check_cycles(self, warnings: List[str]) -> None:
        adjacency: dict = defaultdict(list)
        for edge in self._edges:
            adjacency[edge.source].append(edge.target)

        visited: Set = set()
        in_stack: Set = set()

        def dfs(node: Any) -> bool:
            visited.add(node)
            in_stack.add(node)
            for neighbor in adjacency[node]:
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in in_stack:
                    return True
            in_stack.discard(node)
            return False

        all_nodes = {e.source for e in self._edges} | {e.target for e in self._edges}
        for node in all_nodes:
            if node not in visited:
                if dfs(node):
                    warnings.append("Cycle detected in directed graph")
                    break

    @classmethod
    def from_edge_list(
        cls,
        edges: List[Tuple],
        directed: bool = True,
        allow_self_loops: bool = False,
    ) -> "EdgeChecker":
        checker = cls(directed=directed, allow_self_loops=allow_self_loops)
        checker.add_edges(edges)
        return checker

    @classmethod
    def from_dict(cls, data: dict) -> "EdgeChecker":
        directed = data.get("directed", True)
        allow_self_loops = data.get("allow_self_loops", False)
        checker = cls(directed=directed, allow_self_loops=allow_self_loops)
        for item in data.get("edges", []):
            source = item.get("from") or item.get("source")
            target = item.get("to") or item.get("target")
            weight = item.get("weight")
            checker.add_edge(source, target, weight)
        return checker
