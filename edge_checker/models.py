from dataclasses import dataclass, field
from typing import Any, List, Optional


@dataclass
class Edge:
    source: Any
    target: Any
    weight: Optional[float] = None

    def __eq__(self, other):
        if not isinstance(other, Edge):
            return False
        return self.source == other.source and self.target == other.target

    def __hash__(self):
        return hash((self.source, self.target))

    def __repr__(self):
        if self.weight is not None:
            return f"Edge({self.source!r} -> {self.target!r}, weight={self.weight})"
        return f"Edge({self.source!r} -> {self.target!r})"


@dataclass
class CheckResult:
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def __bool__(self):
        return self.valid

    def summary(self) -> str:
        status = "VALID" if self.valid else "INVALID"
        lines = [f"Graph is {status}"]
        if self.errors:
            lines.append(f"Errors ({len(self.errors)}):")
            lines.extend(f"  - {e}" for e in self.errors)
        if self.warnings:
            lines.append(f"Warnings ({len(self.warnings)}):")
            lines.extend(f"  - {w}" for w in self.warnings)
        return "\n".join(lines)
