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

Reading a diff, a syntax-tree comparison and a test with stand-ins are good evidence, but with Blender connected (the Blender MCP; check `get_scene_info` first: the
build removes only what it made, so the default scene is fine, a scene with someone's work is not) the real proof is cheap: rebuild every model from the old and the
new code and compare the files. It takes about four minutes a tree for all 89 groups (481 models).

1. **Two scratch worktrees under `.claude/worktrees/`** (the hook refuses other places): `verify-old` (the base, or `main` with the change reverted) and `verify-new`
   (the branch). Delete `site/models/*.glb` in both, so every file compared was built from that tree's scripts. They are scratch: `git worktree remove --force` them
   afterwards.
2. **Build every group of `tools/catalog.py` in each tree** with `tools/build_site_assets.py` (it writes into its own tree's `site/models/` and `out/meta/`, never into
   your checkout). One group per `runpy` call, a time budget per Blender call (a call that runs about two minutes loses its reply, though Blender carries on: ask for
   the progress with a short call), and clear the other tree's modules from `sys.path` and `sys.modules` before each group, or one tree's code leaks into the other's
   build. Forward slashes work in the paths on Windows:

   ```python
   import sys, runpy, time, bpy, io, contextlib
   LABEL, TREE = "new", "C:/path/to/repo/.claude/worktrees/verify-new"
   def switch_tree(tree):
       for p in list(sys.path):
           if "lowpoly-assets" in p and (p.endswith("scripts") or p.endswith("tools")):
               sys.path.remove(p)
       for name, m in list(sys.modules.items()):
           f = (getattr(m, "__file__", None) or "").replace("\\", "/")
           if "lowpoly-assets" in f and ("/art/scripts/" in f or "/tools/" in f):
               del sys.modules[name]
       sys.path.insert(0, tree + "/tools")
       sys.path.insert(0, tree + "/art/scripts")
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
   print(state["idx"], "of", len(state["names"]), state["failed"])
   ```

3. **Compare**: `python tools/compare_builds.py .claude/worktrees/verify-old .claude/worktrees/verify-new` (byte-identical, same geometry, different, in one build
   only; exit 1 if anything differs). Expect 477 of 481 byte-identical: `GP_Grey_01`, `GP_Nordic_01`, `GP_Reptilian_01` and `GP_Shadow_01` come out with their index
   buffer in a different order between any two builds, even from the same code, so the tool counts the same JSON structure and the same set of triangles (by vertex
   positions) as the same geometry. Every other model, and every `out/meta` file, should be byte-identical. Rebuild the base twice the first time, to see that for
   yourself.
4. **Say it in the PR**: that you rebuilt every group, how many models were byte-identical, and which differed (and why that is order only). Models built outside
   `tools/catalog.py` (the FBX-only builds of `build_all.py`) are not covered.

If a build stops with `expected sequence size 0`, a folder the palette image pointed to was deleted during the session: remove the `GlobalPalette.png` image
datablock (`bpy.data.images.remove`) and run again. After the builds the scene should be back to what it was (`get_scene_info`).

## Working the backlog

The backlog gets its own PRs, one rule or one file at a time, never mixed into a PR about a model or the site. Take `python tools/sonar_issues.py` for the
rule list and `https://sonarcloud.io/project/issues?id=khanjal_iron-raptor-lowpoly&resolved=false&rules=<rule>` for the sites. Rebuilding a Blender script
changes models, so a refactor of `art/scripts/` must prove the output is unchanged: rebuild and compare the models before and after, as the next section
describes (`tools/glbinfo.py` shows only sizes, nodes and clips, so matching output from it proves little about geometry or colour), and say which models you compared. Read each `S3776` refactor with the script open; cognitive complexity is where a reshape silently changes behaviour.
Counts in this file are not kept: regenerate them from the script.
