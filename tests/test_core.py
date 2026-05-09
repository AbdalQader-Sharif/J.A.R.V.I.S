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

    def test_memory_search_finds_recorded_actions(self) -> None:
        core = JarvisCore()
        core.execute_command("echo status")
        matches = core.memory.search("status")
        self.assertEqual(len(matches), 1)


if __name__ == "__main__":
    unittest.main()
