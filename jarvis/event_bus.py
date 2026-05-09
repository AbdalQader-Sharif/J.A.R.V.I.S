from __future__ import annotations

from collections import defaultdict
import logging
from threading import Lock
from typing import Callable

from .models import Event

EventHandler = Callable[[Event], None]
LOGGER = logging.getLogger(__name__)


class EventBus:
    def __init__(self) -> None:
        self._handlers: dict[str, list[EventHandler]] = defaultdict(list)
        self._lock = Lock()

    def subscribe(self, event_name: str, handler: EventHandler) -> None:
        with self._lock:
            self._handlers[event_name].append(handler)

    def publish(self, event: Event) -> None:
        with self._lock:
            handlers = list(self._handlers.get(event.name, ()))
        for handler in handlers:
            try:
                handler(event)
            except Exception:
                LOGGER.exception("Event handler failed for event '%s'.", event.name)
