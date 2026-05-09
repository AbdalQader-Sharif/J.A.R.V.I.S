from __future__ import annotations

from .automation import AutomationEngine
from .event_bus import EventBus
from .memory import MemoryStore
from .models import AutomationRule, CommandResult, Event
from .security import CommandExecutor


class JarvisCore:
    """Modular J.A.R.V.I.S. core orchestration engine."""

    def __init__(self) -> None:
        self.event_bus = EventBus()
        self.memory = MemoryStore()
        self.automation = AutomationEngine()
        self.commands = CommandExecutor()

    def add_automation_rule(self, rule: AutomationRule) -> None:
        self.automation.add_rule(rule)

    def publish_event(self, event: Event) -> list[CommandResult]:
        self.event_bus.publish(event)
        self.memory.add(f"event:{event.name}", tags=[event.source])
        actions = self.automation.resolve_actions(event)
        return [self.commands.run(command) for command in actions]

    def execute_command(self, command: str) -> CommandResult:
        result = self.commands.run(command)
        self.memory.add(f"cmd:{command}", tags=["command", str(result.returncode)])
        return result
