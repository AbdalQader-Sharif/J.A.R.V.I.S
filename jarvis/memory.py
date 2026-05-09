from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Sequence


@dataclass(frozen=True)
class MemoryEntry:
    text: str
    tags: tuple[str, ...] = field(default_factory=tuple)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class MemoryStore:
    def __init__(self) -> None:
        self._entries: list[MemoryEntry] = []

    def add(self, text: str, tags: Sequence[str] | None = None) -> MemoryEntry:
        entry = MemoryEntry(text=text, tags=tuple(tags or ()))
        self._entries.append(entry)
        return entry

    def search(self, query: str, *, limit: int = 10) -> list[MemoryEntry]:
        needle = query.strip().lower()
        if not needle:
            return []

        def matches(entry: MemoryEntry) -> bool:
            in_text = needle in entry.text.lower()
            in_tags = any(needle in tag.lower() for tag in entry.tags)
            return in_text or in_tags

        results: list[MemoryEntry] = []
        for entry in reversed(self._entries):
            if matches(entry):
                results.append(entry)
                if len(results) >= limit:
                    break
        return results
