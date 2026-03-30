from dataclasses import dataclass, field
from typing import Any


@dataclass
class OutputRecord:
    audience: str
    content: str
    timestamp: float
    message_type: str


@dataclass
class StepResult:
    phase_before: str
    phase_after: str
    emitted_outputs: list[OutputRecord] = field(default_factory=list)
    state_diff: dict[str, tuple[Any, Any]] = field(default_factory=dict)
    persistence_events: list[dict[str, Any]] = field(default_factory=list)
    error: str | None = None
    duration_ms: float = 0.0
