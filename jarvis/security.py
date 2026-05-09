from __future__ import annotations

import shlex
import subprocess
from dataclasses import dataclass

from .models import CommandResult


class UnsafeCommandError(ValueError):
    """Raised when a command violates security policy."""


@dataclass(frozen=True)
class CommandPolicy:
    allowed_prefixes: tuple[str, ...] = (
        "echo",
        "python --version",
        "ls",
        "pwd",
        "date",
    )
    forbidden_tokens: tuple[str, ...] = (
        "&&",
        "||",
        "|",
        ";",
        "`",
        "$(",
        ">",
        "<",
    )


class CommandExecutor:
    def __init__(self, policy: CommandPolicy | None = None) -> None:
        self._policy = policy or CommandPolicy()

    def validate(self, command: str) -> None:
        trimmed = command.strip()
        if not trimmed:
            raise UnsafeCommandError("Command must not be empty.")

        if not any(trimmed.startswith(prefix) for prefix in self._policy.allowed_prefixes):
            raise UnsafeCommandError("Command not allowed by policy.")

        if any(token in trimmed for token in self._policy.forbidden_tokens):
            raise UnsafeCommandError("Command contains forbidden shell token.")

    def run(self, command: str, timeout_seconds: int = 10) -> CommandResult:
        self.validate(command)
        process = subprocess.run(
            shlex.split(command),
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
        return CommandResult(
            command=command,
            returncode=process.returncode,
            stdout=process.stdout,
            stderr=process.stderr,
        )
