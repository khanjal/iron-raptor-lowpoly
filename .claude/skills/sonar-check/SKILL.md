---
name: sonar-check
description: How a change is held to SonarCloud's "no new issues" rule in khanjal/iron-raptor-lowpoly — a PR may not add open Sonar issues, the existing backlog (about 800, mostly Python style rules) is worked down separately and never inside an unrelated PR. Use this before pushing any change to art/scripts, tools, tests or site, when the Sonar check on a PR is red, when working through the backlog, or when deciding whether a reported issue is worth fixing.
---

# Sonar: a PR must not add issues

SonarCloud (project `khanjal_iron-raptor-lowpoly`, public) analyses every PR itself and reports the issues on **new code only**. The `Sonar` workflow
(`.github/workflows/sonar.yml`) waits for that analysis of the PR's head commit and fails the PR while it has any open issue. The backlog on `main` is not
counted, so the rule stops the count growing without making every PR clear old debt. The quality gate is not what is read (it weighs coverage, which this
project does not measure).

## Before pushing

Write new code so it would not be flagged. The rules that account for most of the backlog are the ones most easily repeated:

- `S7498`/`S7496`/`S7500`/`S7504`: write `{}` / `[]` / literals, not `dict()`/`list()` calls, redundant constructor wrappers or copy-only comprehensions; no `list()` around something already iterable.
- `S3776`: keep a function's cognitive complexity at 15 or under; split it instead of nesting.
- `S1481`/`S1172`: no unused locals (`_` for an unpacked value you do not use) or unused parameters.
- `S1192`: a string literal repeated three times becomes a constant.
- `S1515`: a lambda inside a loop takes the loop variable as a default argument.
- `S1244`: do not compare floats with `==`; use `math.isclose` or a tolerance.
- `S117`: names in `snake_case`.
- Path rules (`pythonsecurity:S8707`, `S2083`) on command-line paths in `tools/`: resolve the path and check it is inside the project before reading or writing.

## After pushing

Sonar takes a few minutes to analyse the head. Then:

```bash
python tools/sonar_issues.py <pr-number>          # the PR's issues, whether Sonar analysed the head, and main's total by rule
python tools/sonar_issues.py <pr-number> --wait   # the same, polling until Sonar has analysed the head (what CI runs)
python tools/sonar_issues.py                      # main only, after a merge
```

It exits 1 when the PR has an open issue or Sonar has not analysed the current head (a stale count reads as current). Report the real count. Fix each issue on
the PR, or, when one is a false positive, mark it **Accept**/**False positive** in SonarCloud with the reason and say so in the PR description. Do not silence
a rule with `# NOSONAR` to make the check green without that reason.

A PR from a fork is not analysed by the workflow (it is skipped): check `main` after the merge instead.

## Working the backlog

The backlog gets its own PRs, one rule or one file at a time, never mixed into a PR about a model or the site. Take `python tools/sonar_issues.py` for the
rule list and `https://sonarcloud.io/project/issues?id=khanjal_iron-raptor-lowpoly&resolved=false&rules=<rule>` for the sites. Rebuilding a Blender script
changes models, so a refactor of `art/scripts/` must prove the output is unchanged: rebuild and compare the GLB (`tools/glbinfo.py`) before and after, and
say which models you compared. Read each `S3776` refactor with the script open; cognitive complexity is where a reshape silently changes behaviour.
Counts in this file are not kept: regenerate them from the script.
