from __future__ import annotations

import os
import shlex
import subprocess
import sys
from datetime import datetime, timezone
from dataclasses import dataclass

from .models import CommandResult


class UnsafeCommandError(ValueError):
    """Raised when a command violates security policy."""


@dataclass(frozen=True)
class CommandPolicy:
    allowed_prefixes: tuple[str, ...] = (
        "echo",
        "python --version",
        "pwd",
        "date",
    )
    forbidden_tokens: tuple[str, ...] = (
        "&&",
        "||",
        "&",
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
        trimmed = command.strip()
        if os.name == "nt":
            builtin_result = self._run_windows_builtin(trimmed, timeout_seconds)
            if builtin_result is not None:
                return builtin_result
        return self._run_subprocess(shlex.split(command), command, timeout_seconds)

    def _run_windows_builtin(
        self, command: str, timeout_seconds: int
    ) -> CommandResult | None:
        tokens = shlex.split(command)
        if not tokens:
            return None
        action = tokens[0]
        if action == "echo":
            output = " ".join(tokens[1:])
            return CommandResult(
                command=command,
                returncode=0,
                stdout=f"{output}\n",
                stderr="",
            )
        if action == "pwd" and len(tokens) == 1:
            return CommandResult(
                command=command,
                returncode=0,
                stdout=f"{os.getcwd()}\n",
                stderr="",
            )
        if action == "date" and len(tokens) == 1:
            now = datetime.now(timezone.utc).isoformat()
            return CommandResult(
                command=command,
                returncode=0,
                stdout=f"{now}\n",
                stderr="",
            )
        if action == "python" and len(tokens) >= 2 and tokens[1] == "--version":
            return self._run_subprocess(
                [sys.executable, "--version", *tokens[2:]], command, timeout_seconds
            )
        return None

    def _run_subprocess(
        self, args: list[str], command: str, timeout_seconds: int
    ) -> CommandResult:
        try:
            process = subprocess.run(
                args,
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
        except subprocess.TimeoutExpired:
            return CommandResult(
                command=command,
                returncode=124,
                stdout="",
                stderr=f"Command timed out after {timeout_seconds}s.",
            )
