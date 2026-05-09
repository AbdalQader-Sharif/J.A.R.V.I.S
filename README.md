# J.A.R.V.I.S.

Production-oriented foundation for a modular, local-first J.A.R.V.I.S. platform.

## Current Baseline (Implemented)

- **Core orchestration engine** (`JarvisCore`) to coordinate events, memory, automation, and command execution.
- **Event bus** for decoupled, real-time signaling between subsystems.
- **Automation engine** with event-driven rule matching.
- **Secure command execution layer** with allowlist + token-block policy.
- **Memory store** for searchable context records.
- **Focused tests** for security policy, automation behavior, and memory flow.

## Architecture Direction

This repository is now structured to grow into a production J.A.R.V.I.S. system with the following incremental modules:

1. Voice pipeline service (wake word, STT, TTS, interruption handling).
2. Vision service (object/face/gesture/screen understanding).
3. Device integration service (MQTT, Home Assistant, OPC UA/Modbus adapters).
4. AI brain service (LLM routing, planning, tools, memory/RAG).
5. Desktop/Web/Mobile UI shell.
6. Security and policy service (RBAC, audit logs, encrypted state).

## Quick Start

```bash
python -m unittest discover -v
```

## Example Usage

```python
from jarvis import JarvisCore, Event, AutomationRule

core = JarvisCore()
core.add_automation_rule(
    AutomationRule(name="double-clap-lights", event_name="double_clap", action_command="echo lights_on")
)

core.publish_event(Event(name="double_clap", source="sound"))
```
