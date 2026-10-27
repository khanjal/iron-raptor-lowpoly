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

## Proving an `art/scripts/` change did not change the models

Reading a diff, a syntax-tree comparison and a test with stand-ins are good evidence, but with Blender connected (the Blender MCP; check `get_scene_info` first: a build
removes only what it made, so the default scene is fine, a scene with someone's work is not) the real proof is cheap: rebuild every model from the old and the new code
and compare the files. It takes a few minutes a tree for all 89 catalog groups (481 models).

1. **Two scratch worktrees under `.claude/worktrees/`** (the hook refuses other places), made with `git worktree add --detach` so there is no branch to delete:
   `verify-old` (the base, or `main` with the change reverted) and `verify-new` (the branch). Delete `site/models/*.glb` and `art/data/interactions.json` in both (the build
   merges into an existing file), so every file compared was built from that tree's scripts. **Never do this in your own checkout**: the builds delete and rewrite the tracked `site/models/*.glb` and write `art/data/interactions.json`.
2. **Build every group of `tools/catalog.py` in each tree** with `tools/build_site_assets.py` (it writes into its own tree's `site/models/`, `out/meta/` and
   `art/data/`). One group per `runpy` call, a time budget per Blender call (a call that runs a minute or more can lose its reply while Blender carries on, see
   `blender-assets`: ask for the progress with a short call, do not start it again), and drop every module loaded from the repository's `art/scripts` or `tools` before each
   group, or one tree's code leaks into the other's build (the build reloads `common` and `catalog`, which would find the first tree's files). Forward slashes work in the
   paths on Windows. Start each run with a clean state, or the second run does nothing and says "89 of 89":

   ```python
   import sys, runpy, time, bpy, io, contextlib
   REPO, LABEL = "C:/path/to/repo", "new"                       # LABEL: one per build; the tree is REPO/.claude/worktrees/verify-<LABEL>
   TREE = REPO + "/.claude/worktrees/verify-" + LABEL
   def switch_tree(tree):
       for p in list(sys.path):
           if p.replace("\\", "/").startswith(REPO) and p.replace("\\", "/").endswith(("/art/scripts", "/tools")):
               sys.path.remove(p)
       for name, m in list(sys.modules.items()):
           f = (getattr(m, "__file__", None) or "").replace("\\", "/")
           if f.startswith(REPO) and ("/art/scripts/" in f or "/tools/" in f):
               del sys.modules[name]
       sys.path.insert(0, tree + "/tools")
       sys.path.insert(0, tree + "/art/scripts")
   # bpy.app.driver_namespace.pop("verify_" + LABEL, None)      # <- uncomment for the first call of a run only, then comment it out again
   state = bpy.app.driver_namespace.setdefault("verify_" + LABEL, {"idx": 0, "failed": {}, "names": None})
   switch_tree(TREE)
   if state["names"] is None:
       import catalog
       state["names"] = list(catalog.BUILD)
   t0 = time.time()
   while state["idx"] < len(state["names"]) and time.time() - t0 < 40:     # call again until idx reaches len(names)
       group = state["names"][state["idx"]]
       try:
           with contextlib.redirect_stdout(io.StringIO()):
               runpy.run_path(TREE + "/tools/build_site_assets.py", init_globals={"GROUPS": [group]}, run_name="__main__")
       except Exception as error:
           state["failed"][group] = repr(error)[:200]
       state["idx"] += 1
       switch_tree(TREE)
   print(state["idx"], "of", len(state["names"]), state["failed"])    # done when idx equals len(names); failed must be {}
   ```

3. **Compare**: `python tools/compare_builds.py .claude/worktrees/verify-old .claude/worktrees/verify-new` (from the checkout that holds both). It reports byte-identical,
   same data in another order, different, and in one build only for `site/models/*.glb` and `out/meta/*.json`, and compares `art/data/interactions.json` (hinge pivots,
   axes and limits, which are not in a GLB). Exit 1 if anything differs (or `interactions.json` is missing), 2 if a build's GLBs or meta files are missing or empty (nothing built is not a pass); `failed` in the driver's state must be `{}` before the `interactions.json` line means anything. Expect 477 of 481 GLBs
   byte-identical: `GP_Grey_01`, `GP_Nordic_01`, `GP_Reptilian_01` and `GP_Shadow_01` come out with their vertices and index buffer in another order between any two
   builds, even from the same code, so the tool counts the same JSON, the same triangles (winding included) with the same full attributes at each corner (position,
   normal, UV, joints, weights), the same animation and inverse-bind data and the same embedded images as the same. To see that the noise is real the first time, build the
   base a second time into another worktree (`verify-old2`, its own `LABEL`) and compare the two bases: the same four, order only.
4. **Say it in the PR**: that you rebuilt every group, how many models were byte-identical, which differed and that it was order only. Models built outside
   `tools/catalog.py` (the FBX-only builds of `build_all.py`) are not covered.
5. **Clean up** in this order: `git worktree remove --force` the scratch trees, then in Blender remove the `GlobalPalette.png` image datablock
   (`bpy.data.images.remove`), which still points into the deleted folder and makes the next ordinary build stop with `expected sequence size 0`, and check
   `get_scene_info`. If a build failed halfway, remove only the objects and collections it made by name, never Blender's own `Collection` (with the Cube, Light and
   Camera), and make the Cube the active object again.

## Suppressing what we will not fix

Our analysis is SonarCloud's automatic analysis, which ignores `sonar-project.properties` (`.sonarcloud.properties` takes only source, test, exclusion, encoding and language-version keys, none that ignores an issue), so there is no ignore file for issues. In this order:

1. **On the line**: `# NOSONAR` in Python, bare, with the reason on the line above (what the repository does throughout), and `// NOSONAR: reason` in JS files. Inside an HTML file it did not take effect: `tools/thumbs.html` had a NOSONAR on each of its three `S9382` lines (PR #182) and `main`'s three issues stayed open through three analyses (a PR's own check cannot show this, since it counts only issues new to the PR). Its script now lives in `tools/thumbs.js`, where the same comments raised nothing (PR #190), so keep a script that needs a mark in a `.js` file. A bare NOSONAR hides every rule on its line, so on a `def` line it also hides `S3776` for that function: split the function first, then mark only what is left (the `S107` of `door` and `dome` is the example). The Python analyzer also documents `# NOSONAR(S107)`, which hides one rule only; it has not been tried here, so try it on one line before relying on it.
2. **In SonarCloud**, with the owner's login: the issue's status control, Accept or False positive, with a comment; or, for a rule in a file pattern, Administration > General Settings > Analysis Scope > Issues > "Ignore Issues on Multiple Criteria" (both the rule pattern and the file pattern are required: a blank one fails the analysis). Nothing in the repository records it, so say it in the PR description; then re-run the `Sonar` job.
3. To stop analysing a file altogether (a dev-only helper), `sonar.exclusions` in a `.sonarcloud.properties` at the repository root is read by automatic analysis. That also hides real findings in the file, so it is the last resort.

## Working the backlog

The backlog gets its own PRs, one rule or one file at a time, never mixed into a PR about a model or the site. Take `python tools/sonar_issues.py` for the
rule list and `https://sonarcloud.io/project/issues?id=khanjal_iron-raptor-lowpoly&resolved=false&rules=<rule>` for the sites. Rebuilding a Blender script
changes models, so a refactor of `art/scripts/` must prove the output is unchanged: rebuild and compare the models before and after, as the section above
describes (`tools/glbinfo.py` shows only sizes, nodes and clips, so matching output from it proves little about geometry or colour), and say which models you compared. Read each `S3776` refactor with the script open; cognitive complexity is where a reshape silently changes behaviour.
Counts in this file are not kept: regenerate them from the script.
