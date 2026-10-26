"""The worktree-location hook (.claude/hooks/worktree_location.py) refuses `git worktree add` outside .claude/worktrees/."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".claude" / "hooks"))
import worktree_location as H


class WorktreeLocation(unittest.TestCase):
    def refused(self, command):
        return H.check(command, ROOT) is not None

    def test_inside_is_allowed(self):
        self.assertFalse(self.refused("git worktree add .claude/worktrees/x -b art/x origin/main"))
        self.assertFalse(self.refused(f"git worktree add -b art/x {ROOT}/.claude/worktrees/x"))

    def test_outside_is_refused(self):
        self.assertTrue(self.refused("git worktree add ../lowpoly-assets-x -b art/x"))
        self.assertTrue(self.refused("git worktree add -b art/x ../elsewhere origin/main"))
        self.assertTrue(self.refused("git status && git worktree add /tmp/x"))
        self.assertTrue(self.refused("git worktree add .claude/worktrees/../../x"))

    def test_other_commands_are_left_alone(self):
        self.assertFalse(self.refused("git worktree list"))
        self.assertFalse(self.refused("git worktree remove ../x"))
        self.assertFalse(self.refused("git status"))
        self.assertFalse(self.refused('git commit -m "docs: git worktree add goes under .claude"'))


if __name__ == "__main__":
    unittest.main()
