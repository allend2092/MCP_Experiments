from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List

import pexpect


# ---------- Config / Mapping (LLM-facing -> SSH alias) ----------

@dataclass(frozen=True)
class CiscoHost:
    ssh_alias: str
    platform: str = "ios"
    role: str = "switch"
    prompt_re: str = r"(?m)[>#]\s*$"


# LLM-facing host identifier(s). Add more entries as you grow.
HOSTS: Dict[str, CiscoHost] = {
    "Cisco-3560-PoE-switch": CiscoHost(
        ssh_alias="cisco-3560-poe",
        role="access-switch",
        prompt_re=r"(?m)^Cat_3560-PoE[>#]\s*$",
    ),
}


# Repo-scoped SSH config path (portable). You can override via env var if needed.
SSH_CONFIG_PATH: str = os.getenv("MCP_SSH_CONFIG", "./config/ssh_config")

# Optional: password-based login support via env var.
# Prefer SSH keys long-term, but this works for now.
PASSWORD_ENV: str = os.getenv("CISCO_PASSWORD_ENV", "CISCO_PASSWORD")


# ---------- Low-level SSH session driver ----------



class CiscoSSHError(RuntimeError):
    pass


def _strip_trailing_prompt(text: str, prompt_re: str) -> str:
    """
    Remove a trailing prompt line if present, without embedding prompt_re inside
    another regex (prompt_re may contain inline flags like (?m)).
    """
    lines = text.splitlines()
    # Drop trailing blank lines first
    while lines and lines[-1].strip() == "":
        lines.pop()

    # If the last line matches the prompt regex, remove it
    if lines and re.match(prompt_re, lines[-1]):
        lines.pop()

    return "\n".join(lines).rstrip()


def _require_allowed_host(host: str) -> CiscoHost:
    if host not in HOSTS:
        allowed = ", ".join(sorted(HOSTS.keys()))
        raise ValueError(f"Host '{host}' is not allowed. Allowed hosts: {allowed}")
    return HOSTS[host]


def _spawn_ssh(ssh_alias: str, timeout_s: int) -> pexpect.spawn:
    # -tt forces a tty; IOS behaves better for pagination/prompt handling.
    cmd = f"ssh -tt -F {SSH_CONFIG_PATH} {ssh_alias}"
    return pexpect.spawn(cmd, encoding="utf-8", timeout=timeout_s)


def _login(child: pexpect.spawn, host: CiscoHost, timeout_s: int) -> None:
    """
    Handle first-connect prompts and password prompt.
    Supports:
      - StrictHostKeyChecking accept-new (no prompt expected usually)
      - Manual "Are you sure you want to continue connecting (yes/no/[fingerprint])?"
      - Password auth (CISCO_PASSWORD env var)
      - Key-based auth (no password prompt)
    """
    password = os.getenv(PASSWORD_ENV)

    # We loop a bit because SSH can present prompts in different orders.
    for _ in range(4):
        i = child.expect(
            [
                r"(?i)are you sure you want to continue connecting",
                r"(?i)password:",
                host.prompt_re,
                r"(?i)permission denied",
                pexpect.EOF,
                pexpect.TIMEOUT,
            ],
            timeout=timeout_s,
        )

        if i == 0:
            child.sendline("yes")
            continue

        if i == 1:
            if not password:
                raise CiscoSSHError(
                    f"SSH requested a password, but env var '{PASSWORD_ENV}' is not set."
                )
            child.sendline(password)
            # after password, expect prompt or permission denied
            j = child.expect([host.prompt_re, r"(?i)permission denied", pexpect.EOF, pexpect.TIMEOUT], timeout=timeout_s)
            if j == 0:
                return
            if j == 1:
                raise CiscoSSHError("Permission denied (bad username/password).")
            if j == 2:
                raise CiscoSSHError("SSH session ended unexpectedly (EOF) after password entry.")
            raise CiscoSSHError("Timed out waiting for prompt after password entry.")

        if i == 2:
            return

        if i == 3:
            raise CiscoSSHError("Permission denied.")

        if i == 4:
            raise CiscoSSHError("SSH session ended unexpectedly (EOF).")

        # TIMEOUT
        raise CiscoSSHError("Timed out waiting for SSH login/prompt.")

    raise CiscoSSHError("SSH login flow exceeded expected prompt iterations.")


def _run_ios_commands(host: CiscoHost, commands: List[str], timeout_s: int = 25) -> str:
    """
    Run IOS commands in a single interactive session.
    Ensures paging disabled via `terminal length 0`.
    Returns concatenated output of commands (no prompt).
    """
    child = _spawn_ssh(host.ssh_alias, timeout_s=timeout_s)
    try:
        _login(child, host, timeout_s=timeout_s)

        # Disable paging
        child.sendline("terminal length 0")
        child.expect(host.prompt_re)

        outputs: List[str] = []
        for cmd in commands:
            child.sendline(cmd)
            child.expect(host.prompt_re)
            chunk = child.before or ""

            # child.before contains echoed command + output. Drop first line (echo).
            chunk = re.sub(r"(?m)^[^\r\n]*\r?\n", "", chunk, count=1)

            outputs.append(_strip_trailing_prompt(chunk, host.prompt_re))

        child.sendline("exit")
        child.close()

        return "\n\n".join([o for o in outputs if o]).strip()

    finally:
        if child.isalive():
            child.close(force=True)


# ---------- Public tool functions (called by MCP server) ----------

def cisco_show_version(host: str) -> Dict[str, Any]:
    """
    Fetch 'show version' from an allowed Cisco host.
    Returns a structured dict suitable for MCP tool output.
    """
    chost = _require_allowed_host(host)
    raw = _run_ios_commands(chost, ["show version"])

    return {
        "host": host,
        "ssh_alias": chost.ssh_alias,
        "platform": chost.platform,
        "role": chost.role,
        "command": "show version",
        "raw": raw,
    }
