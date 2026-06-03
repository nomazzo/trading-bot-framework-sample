from __future__ import annotations

from dataclasses import dataclass, field
from queue import SimpleQueue
from typing import Any


@dataclass
class EventBus:
    market_ticks: SimpleQueue[Any] = field(default_factory=SimpleQueue)
    orders: SimpleQueue[Any] = field(default_factory=SimpleQueue)
    fills: SimpleQueue[Any] = field(default_factory=SimpleQueue)
