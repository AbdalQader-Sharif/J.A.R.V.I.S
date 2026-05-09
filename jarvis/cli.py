from __future__ import annotations

import argparse
import json
import shlex
import sys
from typing import Any, Sequence

from .core import JarvisCore
from .models import AutomationRule, CommandResult, Event
from .security import UnsafeCommandError


DEMO_DEFAULTS = {
    "event_name": "double_clap",
    "event_source": "cli",
    "rule_name": "demo-rule",
    "action_command": "echo lights_on",
    "payload": {},
}


def _parse_payload(raw: str) -> dict[str, Any]:
    if not raw:
        return {}
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise argparse.ArgumentTypeError("Payload must be valid JSON.") from exc
    if not isinstance(payload, dict):
        raise argparse.ArgumentTypeError("Payload must be a JSON object.")
    return payload


def _print_result(result: CommandResult) -> None:
    print(f"Command: {result.command}")
    print(f"Return code: {result.returncode}")
    if result.stdout:
        print("Stdout:")
        print(result.stdout, end="" if result.stdout.endswith("\n") else "\n")
    if result.stderr:
        print("Stderr:", file=sys.stderr)
        print(result.stderr, file=sys.stderr, end="" if result.stderr.endswith("\n") else "\n")


def _exit_code(results: Sequence[CommandResult]) -> int:
    return 0 if all(result.returncode == 0 for result in results) else 1


def _run_demo(args: argparse.Namespace) -> int:
    core = JarvisCore()
    rule = AutomationRule(
        name=args.rule_name,
        event_name=args.event_name,
        action_command=args.action_command,
    )
    core.add_automation_rule(rule)
    event = Event(name=args.event_name, source=args.event_source, payload=args.payload)
    results = core.publish_event(event)
    if not results:
        print("No automation actions matched the event.")
        return 0
    for result in results:
        _print_result(result)
    return _exit_code(results)


def _run_command(args: argparse.Namespace) -> int:
    command = shlex.join(args.command).strip()
    if not command:
        print("Command cannot be empty.", file=sys.stderr)
        return 2
    core = JarvisCore()
    try:
        result = core.execute_command(command)
    except UnsafeCommandError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    _print_result(result)
    return 0 if result.returncode == 0 else 1


def _run_event(args: argparse.Namespace) -> int:
    core = JarvisCore()
    if args.action_command:
        core.add_automation_rule(
            AutomationRule(
                name=args.rule_name,
                event_name=args.event_name,
                action_command=args.action_command,
            )
        )
    event = Event(name=args.event_name, source=args.event_source, payload=args.payload)
    results = core.publish_event(event)
    if not results:
        print("No automation actions matched the event.")
        return 0
    for result in results:
        _print_result(result)
    return _exit_code(results)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run Jarvis automation demos, commands, and events.",
    )
    subparsers = parser.add_subparsers(dest="command")

    demo = subparsers.add_parser("demo", help="Run the built-in automation demo.")
    demo.add_argument(
        "--event-name",
        default=DEMO_DEFAULTS["event_name"],
        help="Event name to publish.",
    )
    demo.add_argument(
        "--event-source",
        default=DEMO_DEFAULTS["event_source"],
        help="Source label for the event.",
    )
    demo.add_argument(
        "--rule-name",
        default=DEMO_DEFAULTS["rule_name"],
        help="Automation rule name to register.",
    )
    demo.add_argument(
        "--action-command",
        default=DEMO_DEFAULTS["action_command"],
        help="Command to execute when the demo event matches.",
    )
    demo.add_argument(
        "--payload",
        type=_parse_payload,
        default=DEMO_DEFAULTS["payload"],
        help="Optional JSON object payload.",
    )
    demo.set_defaults(handler=_run_demo)

    run_command = subparsers.add_parser("command", help="Run a command via policy.")
    run_command.add_argument(
        "command",
        nargs=argparse.REMAINDER,
        help="Command to run (subject to the security policy).",
    )
    run_command.set_defaults(handler=_run_command)

    event = subparsers.add_parser(
        "event", help="Publish an event (optionally with an inline rule)."
    )
    event.add_argument("--event-name", required=True, help="Event name to publish.")
    event.add_argument(
        "--event-source", default="cli", help="Source label for the event."
    )
    event.add_argument(
        "--rule-name", default="cli-rule", help="Automation rule name to register."
    )
    event.add_argument(
        "--action-command",
        help="Optional command to execute when the event matches.",
    )
    event.add_argument(
        "--payload", type=_parse_payload, default={}, help="Optional JSON object payload."
    )
    event.set_defaults(handler=_run_event)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    if not argv:
        argv = ["demo"]
    parser = build_parser()
    args = parser.parse_args(list(argv))
    return args.handler(args)


__all__ = ["build_parser", "main"]
