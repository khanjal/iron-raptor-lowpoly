"""The worktree-location hook (.claude/hooks/worktree_location.py) refuses `git worktree add` outside .claude/worktrees/."""

import json
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".claude" / "hooks"))
import worktree_location

ALLOWED = ROOT / ".claude" / "worktrees"


class WorktreeLocation(unittest.TestCase):
    def refused(self, command):
        return worktree_location.check(command, ROOT, ALLOWED) is not None

    def test_inside_is_allowed(self):
        self.assertFalse(self.refused("git worktree add .claude/worktrees/x -b art/x origin/main"))
        self.assertFalse(self.refused(f"git worktree add -b art/x {ROOT.as_posix()}/.claude/worktrees/x"))
        self.assertFalse(self.refused('git worktree add ".claude/worktrees/with space"'))

    def test_outside_is_refused(self):
        self.assertTrue(self.refused("git worktree add ../lowpoly-assets-x -b art/x"))
        self.assertTrue(self.refused("git worktree add -b art/x ../elsewhere origin/main"))
        self.assertTrue(self.refused("git status && git worktree add /tmp/x"))
        self.assertTrue(self.refused("git worktree add .claude/worktrees/../../x"))
        self.assertTrue(self.refused("git worktree add .claude/worktrees"))

    def test_other_commands_are_left_alone(self):
        self.assertFalse(self.refused("git worktree list"))
        self.assertFalse(self.refused("git worktree remove ../x"))
        self.assertFalse(self.refused("git status"))

    def test_text_that_only_mentions_the_command_is_left_alone(self):
        self.assertFalse(self.refused('git commit -m "docs: git worktree add goes under .claude"'))
        self.assertFalse(self.refused('git commit -m "a; git worktree add ../y"'))

    def test_msys_drive_paths_are_read_as_windows_paths(self):
        if sys.platform != "win32":
            self.skipTest("only Windows reads /c/... as a drive")
        drive = ROOT.drive[0].lower()
        self.assertFalse(self.refused(f"git worktree add /{drive}{ALLOWED.as_posix()[2:]}/x"))

    def run_main(self, text):
        with mock.patch.object(sys, "stdin", mock.Mock(read=lambda: text)), mock.patch.object(
            worktree_location, "main_checkout", return_value=ROOT
        ):
            return worktree_location.main()

    def test_main_blocks_with_exit_code_2(self):
        event = {"tool_input": {"command": "git worktree add ../x"}, "cwd": str(ROOT)}
        self.assertEqual(self.run_main(json.dumps(event)), 2)

    def test_main_lets_unreadable_input_through(self):
        for text in ("not json", "null", '{"tool_input": null}', '{"tool_input": {"command": null}}', "{}"):
            with self.subTest(text=text):
                self.assertEqual(self.run_main(text), 0)


if __name__ == "__main__":
    unittest.main()
