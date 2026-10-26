"""PreToolUse hook for Bash and PowerShell: `git worktree add` may only create worktrees under .claude/worktrees/ of this repo (CLAUDE.md, Rules).

A best-effort guard, not a sandbox: it reads the command text, so a `cd` before it, `git -C`, other global git options, an env prefix, `bash -c "..."` or a path built from a variable are not followed. Anything it cannot read, it lets through.
"""

import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
QUOTES = "'\""
OPTIONS_WITH_VALUE = {"-b", "-B", "--reason"}
QUOTED = re.compile(r"\"[^\"]*\"|'[^']*'")
ADD = re.compile(r"(?:^|[;&|(\n])[ \t]*git\s+worktree\s+add\b(?P<args>[^;&|\n]*)")
MSYS_DRIVE = re.compile(r"^/([a-zA-Z])/")


def main_checkout():
    """The repo's main checkout, even when the hook runs from inside a worktree of it (whose own .claude/ is a second copy)."""
    try:
        common = subprocess.run(
            ["git", "-C", str(HERE), "rev-parse", "--path-format=absolute", "--git-common-dir"],
            capture_output=True, text=True, timeout=10, check=True,
        ).stdout.strip()
        return Path(common).resolve().parent
    except (OSError, subprocess.SubprocessError):
        return HERE.parents[1]


def worktree_path(args):
    """The path argument of a `git worktree add` (the first argument that is not an option or an option's value), or None."""
    try:
        words = [w.strip(QUOTES) for w in shlex.split(args, posix=False)]
    except ValueError:
        return None
    skip = False
    for word in words:
        if skip:
            skip = False
        elif word in OPTIONS_WITH_VALUE:
            skip = True
        elif not word.startswith("-"):
            return word
    return None


def resolve(path, cwd):
    """`path` as an absolute path; Git Bash's /c/Users/... spelling is read as C:/Users/... on Windows."""
    if os.name == "nt":
        path = MSYS_DRIVE.sub(lambda m: m.group(1).upper() + ":/", path)
    return (Path(cwd) / path).resolve()


def check(command, cwd, allowed=None):
    """The refusal message when `command` adds a worktree outside .claude/worktrees/, else None."""
    allowed = (allowed or main_checkout() / ".claude" / "worktrees").resolve()
    # Match on the command with quoted text blanked out (a commit message that mentions the command is not the command), read the arguments from the real text.
    masked = QUOTED.sub(lambda m: "_" * len(m.group()), command)
    for found in ADD.finditer(masked):
        path = worktree_path(command[found.start("args"):found.end("args")])
        if path is None:
            continue
        if allowed not in resolve(path, cwd).parents:
            return f"Worktrees go under {allowed} (CLAUDE.md); {path} is outside it. Use .claude/worktrees/<name>."
    return None


def main():
    try:
        event = json.load(sys.stdin)
        command = event["tool_input"]["command"]
        message = check(command, event.get("cwd") or ".")
    except (ValueError, KeyError, TypeError):
        return 0
    if message:
        print(message, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
