"""Open SonarCloud issues for a pull request and for main, so a PR can be checked for what it adds.

    python tools/sonar_issues.py <pr-number>   the PR's issues, whether Sonar analysed its head, and main's total
    python tools/sonar_issues.py               main's issues only (use after a merge)
    python tools/sonar_issues.py <pr> --wait   keep polling (up to 10 minutes) until Sonar has analysed the PR's head
    python tools/sonar_issues.py <pr> --head <sha>   check that commit instead of asking GitHub for the PR's current head (CI does this)

Exits 1 when the PR has open issues or Sonar has not analysed the PR's current head (a stale count reads as current), 2 when a call fails.
Standard library only; the project is public, so no token is needed. Main's older issues are never counted against a PR: Sonar reports a PR's
issues on its new code only. Used by .github/workflows/sonar.yml and described in .claude/skills/sonar-check.
"""

import argparse
import json
import sys
import time
import urllib.parse
import urllib.request

PROJECT = "khanjal_iron-raptor-lowpoly"
API = "https://sonarcloud.io/api"
PAGE = 500


def fetch(url):
    """Read JSON from a URL, trying three times: one blip from either API must not fail a PR that has nothing wrong with it."""
    for attempt in range(3):
        try:
            with urllib.request.urlopen(url, timeout=30) as response:
                return json.load(response)
        except OSError:
            if attempt == 2:
                raise
            time.sleep(5 * (attempt + 1))


def get(path, **params):
    return fetch(f"{API}/{path}?{urllib.parse.urlencode(params)}")


def analysed_head(pr):
    """The commit Sonar last analysed for this PR, or '' when it has not analysed it at all."""
    for p in get("project_pull_requests/list", project=PROJECT)["pullRequests"]:
        if p["key"] == str(pr):
            return p.get("commit", {}).get("sha", "")
    return ""


def issues(pr=None):
    """(total, [issue, ...], {rule: count}) of the open issues on main, or on the PR's new code. Sonar pages at 500."""
    params = {"componentKeys": PROJECT, "resolved": "false", "ps": PAGE, "facets": "rules"}
    if pr is not None:
        params["pullRequest"] = pr
    data = get("issues/search", **params)
    rules = next(f["values"] for f in data["facets"] if f["property"] == "rules")
    return data["total"], data["issues"], {v["val"]: v["count"] for v in rules}


def by_rule(counts):
    return ", ".join(f"{rule} x{n}" for rule, n in sorted(counts.items(), key=lambda kv: -kv[1])) or "none"


def describe(i):
    name = i["component"].split(":", 1)[-1]
    return f"  {i['rule']} {i['severity']} {name}:{i.get('line')} | {i['message'][:100]}"


def wait_for_head(pr, head, minutes=10):
    """Poll until Sonar has analysed `head`; True when it has, False when the time ran out."""
    deadline = time.monotonic() + minutes * 60
    while True:
        if analysed_head(pr) == head:
            return True
        if time.monotonic() > deadline:
            return False
        time.sleep(15)


def pr_head(pr):
    """The PR's head commit, from GitHub (public repository, no token)."""
    url = f"https://api.github.com/repos/khanjal/iron-raptor-lowpoly/pulls/{pr}"
    return fetch(url)["head"]["sha"]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("pr", nargs="?", type=int)
    parser.add_argument("--head", help="the commit to check (default: the PR's current head, from GitHub)")
    parser.add_argument("--wait", action="store_true", help="wait for Sonar to analyse the PR's head")
    args = parser.parse_args(argv)
    status = 0
    try:
        if args.pr is not None:
            head = args.head or pr_head(args.pr)
            if args.wait:
                wait_for_head(args.pr, head)
            seen = analysed_head(args.pr)
            if seen == head:
                print(f"PR #{args.pr}: Sonar analysed the head ({head[:8]})")
            else:
                print(f"PR #{args.pr}: Sonar has NOT analysed the head yet (head {head[:8]}, analysed {seen[:8] or 'nothing'}); wait and rerun, and if it never does, check that Sonar's analysis of pull requests is on")
                status = 1
            total, found, rules = issues(args.pr)
            print(f"PR #{args.pr} open issues: {total}")
            print(f"  by rule: {by_rule(rules)}")
            for i in found:
                print(describe(i))
            if total:
                status = 1
    except (OSError, KeyError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    try:
        total, _, rules = issues()
        print(f"main open issues: {total} (a rise since the last look is for the rule and file list, not the bare count)")
        print(f"  by rule: {by_rule(rules)}")
    except (OSError, KeyError, ValueError) as error:
        # Informational: a failure here says nothing about the PR.
        print(f"main's issues could not be read: {error}", file=sys.stderr)
        if args.pr is None:
            return 2
    return status


if __name__ == "__main__":
    sys.exit(main())
