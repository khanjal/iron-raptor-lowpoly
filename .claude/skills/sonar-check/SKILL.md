---
name: sonar-check
description: How a change is held to SonarCloud's "no new issues" rule in khanjal/iron-raptor-lowpoly — a PR may not add open Sonar issues, the existing backlog (about 800, mostly Python style rules) is worked down separately and never inside an unrelated PR. Use this before pushing any change to art/scripts, tools, tests or site, when the Sonar check on a PR is red, when working through the backlog, or when deciding whether a reported issue is worth fixing.
---

# Sonar: a PR must not add issues

SonarCloud (project `khanjal_iron-raptor-lowpoly`, public) analyses every PR itself and reports the issues on **new code only**. The `Sonar` workflow
(`.github/workflows/sonar.yml`) waits for that analysis of the PR's head commit and fails the PR while it has any open issue. The backlog on `main` is not
counted, so the rule stops the count growing without making every PR clear old debt. (Sonar counts a line you edit as new: if a PR touches a line that already carries a backlog issue, that issue shows up on the PR. Fix that line, or mark it Accepted in SonarCloud with the reason.) The check blocks a merge only while it is a required status check in the branch protection settings. The quality gate is not what is read (it weighs coverage, which this
project does not measure).

## Before pushing

Write new code so it would not be flagged. The rules that account for most of the backlog are the ones most easily repeated:

- `S7498`/`S7496`/`S7504`: write `{}` / `[]` and literals, not an empty or keyword `dict()` / `list()` call; no constructor wrapped round a literal or comprehension (`dict({...})`); no `list()` around something already iterable in a `for`.
- `S7500`: a comprehension that only copies (`[x for x in xs]`) becomes `list(xs)`.
- `S3776`: keep a function's cognitive complexity at 15 or under; split it instead of nesting.
- `S1481`/`S1172`: no unused locals (`_` for an unpacked value you do not use) or unused parameters.
- `S1192`: a string literal repeated three times becomes a constant.
- `S1515`: a lambda inside a loop takes the loop variable as a default argument.
- `S1244`: do not compare floats with `==`; use `math.isclose` or a tolerance.
- `S117`: names in `snake_case`.
- Path injection (`pythonsecurity:S8707`, `S2083`): a path taken from the command line or from file content: resolve it and check it is inside the project before reading or writing.

## After pushing

Sonar takes a few minutes to analyse the head. Then:

```bash
python tools/sonar_issues.py <pr-number>          # the PR's issues, whether Sonar analysed the head, and main's total by rule
python tools/sonar_issues.py <pr-number> --wait   # the same, polling until Sonar has analysed the head (what CI runs)
python tools/sonar_issues.py                      # main only, after a merge
```

In CI the job runs once per push. Marking an issue Accepted or False positive in SonarCloud makes no new commit, so the job does not re-run by itself: use "Re-run jobs" on the failed run (the same for a run that gave up waiting for Sonar). It exits 1 when the PR has an open issue or Sonar has not analysed the current head (a stale count reads as current). Report the real count. Fix each issue on
the PR, or, when one is a false positive, mark it **Accept**/**False positive** in SonarCloud with the reason and say so in the PR description. Do not silence
a rule with `# NOSONAR` to make the check green without that reason.

The workflow also runs on a fork's PR. If Sonar does not analyse that PR the job fails saying the head was not analysed; check `main` after the merge instead and say so in the PR.

## Working the backlog

The backlog gets its own PRs, one rule or one file at a time, never mixed into a PR about a model or the site. Take `python tools/sonar_issues.py` for the
rule list and `https://sonarcloud.io/project/issues?id=khanjal_iron-raptor-lowpoly&resolved=false&rules=<rule>` for the sites. Rebuilding a Blender script
changes models, so a refactor of `art/scripts/` must prove the output is unchanged: rebuild and compare the GLB before and after (a hash of the file when the export is
deterministic; `tools/glbinfo.py` shows only sizes, nodes and clips, so matching output from it proves little about geometry or colour), and say which models you compared. Read each `S3776` refactor with the script open; cognitive complexity is where a reshape silently changes behaviour.
Counts in this file are not kept: regenerate them from the script.
