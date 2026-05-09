from __future__ import annotations

from .models import AutomationRule, Event


class AutomationEngine:
    def __init__(self) -> None:
        self._rules: dict[str, AutomationRule] = {}

    def add_rule(self, rule: AutomationRule) -> None:
        self._rules[rule.name] = rule

    def list_rules(self) -> list[AutomationRule]:
        return list(self._rules.values())

    def resolve_actions(self, event: Event) -> list[str]:
        actions: list[str] = []
        for rule in self._rules.values():
            if rule.enabled and rule.event_name == event.name:
                actions.append(rule.action_command)
        return actions
