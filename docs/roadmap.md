# J.A.R.V.I.S. Phased Roadmap

## Phase 1: Foundation Stabilization
- Harden event bus, memory, automation, and command policy interfaces.
- Introduce API gateway skeleton and contract definitions.
- Establish baseline observability and health checks.
- Build initial Docker compose stack for core services.

## Phase 2: Multimodal Core Services
- Voice service: wake word, streaming STT, TTS, interruption.
- Vision service: presence detection, tracking, OCR, gestures.
- AI brain: planner/executor, tool registry, hybrid LLM routing.

## Phase 3: Automation & IoT Expansion
- Device capability registry and adapter framework.
- MQTT + Home Assistant bridge; initial industrial protocol adapters.
- AI-assisted automation builder with guardrails.

## Phase 4: UI Polish & Experience
- Desktop HUD prototype with telemetry and voice visualizer.
- Web dashboard for configuration and automation.
- Mobile companion for alerts and quick controls.

## Phase 5: Enterprise Hardening & Scale
- Security hardening (RBAC, audit logs, secrets).
- High-availability event bus and telemetry pipeline.
- Optional Kubernetes deployment and multi-device orchestration.

## Definition of Done (per phase)
- Contract tests passing.
- Performance baselines met (latency, CPU usage, memory).
- Security checks and audit logs validated.
- Documentation and deployment guides updated.
