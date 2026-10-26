"""PreToolUse hook for Bash: `git worktree add` may only create worktrees under .claude/worktrees/ of this repo (CLAUDE.md, Rules)."""

import json
import re
import shlex
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ALLOWED = ROOT / ".claude" / "worktrees"
QUOTES = "'\""
OPTIONS_WITH_VALUE = {"-b", "-B", "--reason"}
ADD = re.compile(r"(?:^|[;&|(\n])[ \t]*git\s+(?:-C\s+\S+\s+)?worktree\s+add\b(?P<args>[^;&|\n]*)")


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


def check(command, cwd):
    """The refusal message when `command` adds a worktree outside .claude/worktrees/, else None."""
    for found in ADD.finditer(command):
        path = worktree_path(found.group("args"))
        if path is None:
            continue
        target = (Path(cwd) / path).resolve()
        if not target.is_relative_to(ALLOWED.resolve()):
            return f"Worktrees go under {ALLOWED} (CLAUDE.md); {path} is outside it. Use .claude/worktrees/<name>."
    return None


def main():
    event = json.load(sys.stdin)
    message = check(event.get("tool_input", {}).get("command", ""), event.get("cwd", "."))
    if message:
        print(message, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
