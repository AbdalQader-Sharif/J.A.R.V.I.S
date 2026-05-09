import unittest

from jarvis import AutomationRule, Event, JarvisCore
from jarvis.security import CommandExecutor, UnsafeCommandError


class CommandExecutorTests(unittest.TestCase):
    def test_rejects_chained_command(self) -> None:
        executor = CommandExecutor()
        with self.assertRaises(UnsafeCommandError):
            executor.run("echo hello && whoami")

    def test_allows_safe_echo_command(self) -> None:
        executor = CommandExecutor()
        result = executor.run("echo jarvis")
        self.assertEqual(result.returncode, 0)
        self.assertIn("jarvis", result.stdout)


class JarvisCoreTests(unittest.TestCase):
    def test_duplicate_rule_name_is_rejected(self) -> None:
        core = JarvisCore()
        rule = AutomationRule(name="same", event_name="double_clap", action_command="echo 1")
        core.add_automation_rule(rule)
        with self.assertRaises(ValueError):
            core.add_automation_rule(rule)

    def test_event_bus_continues_when_handler_raises(self) -> None:
        core = JarvisCore()
        seen: list[str] = []

        def bad_handler(_event: Event) -> None:
            raise RuntimeError("boom")

        def good_handler(_event: Event) -> None:
            seen.append("ok")

        core.event_bus.subscribe("presence", bad_handler)
        core.event_bus.subscribe("presence", good_handler)
        core.publish_event(Event(name="presence", source="vision"))
        self.assertEqual(seen, ["ok"])

    def test_event_triggers_automation_action(self) -> None:
        core = JarvisCore()
        core.add_automation_rule(
            AutomationRule(
                name="double-clap-lights-on",
                event_name="double_clap",
                action_command="echo lights_on",
            )
        )

        outputs = core.publish_event(Event(name="double_clap", source="sound"))
        self.assertEqual(len(outputs), 1)
        self.assertIn("lights_on", outputs[0].stdout)

    def test_event_automation_collects_failures_without_stopping(self) -> None:
        core = JarvisCore()
        core.add_automation_rule(
            AutomationRule(name="bad", event_name="double_clap", action_command="rm -rf /")
        )
        core.add_automation_rule(
            AutomationRule(name="good", event_name="double_clap", action_command="echo safe")
        )
        outputs = core.publish_event(Event(name="double_clap", source="sound"))
        self.assertEqual(len(outputs), 2)
        self.assertEqual(outputs[0].returncode, 1)
        self.assertIn("safe", outputs[1].stdout)

    def test_memory_search_finds_recorded_actions(self) -> None:
        core = JarvisCore()
        core.execute_command("echo status")
        matches = core.memory.search("status")
        self.assertEqual(len(matches), 1)
        self.assertIn("cmd:echo status", matches[0].text)
        self.assertIn("command", matches[0].tags)


if __name__ == "__main__":
    unittest.main()
