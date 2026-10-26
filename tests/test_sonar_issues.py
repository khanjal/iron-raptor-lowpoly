"""tools/sonar_issues.py: exit status and output, with Sonar's answers replaced by canned ones (no network)."""

import io
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import sonar_issues as S

HEAD = "a" * 40
ISSUE = {"rule": "python:S1481", "severity": "MINOR", "component": "k:tools/x.py", "line": 3, "message": "Unused."}


def run(seen, pr_issues):
    def get(path, **params):
        if path == "project_pull_requests/list":
            return {"pullRequests": [{"key": "7", "commit": {"sha": seen}}] if seen else []}
        found = pr_issues if "pullRequest" in params else []
        return {"total": len(found), "issues": found, "facets": [{"property": "rules", "values": [{"val": i["rule"], "count": 1} for i in found]}]}

    out = io.StringIO()
    with mock.patch.object(S, "get", get), mock.patch.object(S, "pr_head", return_value=HEAD), redirect_stdout(out):
        return S.main(["7"]), out.getvalue()


class SonarIssuesTest(unittest.TestCase):
    def test_clean_analysed_head_passes(self):
        status, out = run(HEAD, [])
        self.assertEqual(status, 0)
        self.assertIn("analysed the head", out)

    def test_open_issue_fails_and_is_listed(self):
        status, out = run(HEAD, [ISSUE])
        self.assertEqual(status, 1)
        self.assertIn("python:S1481", out)
        self.assertIn("tools/x.py:3", out)

    def test_unanalysed_head_fails_even_with_no_issues(self):
        for seen in ("", "b" * 40):
            status, out = run(seen, [])
            self.assertEqual(status, 1)
            self.assertIn("NOT analysed", out)


if __name__ == "__main__":
    unittest.main()
