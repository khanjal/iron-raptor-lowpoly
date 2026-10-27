---
name: pr-review
description: How a pull request in khanjal/iron-raptor-lowpoly gets reviewed before it merges — a model review before it opens and another of the finished PR before merge, never by the model that wrote the code — including what to point reviewers at in a Blender-script, GLB and static-site project. Use this whenever opening a PR here, about to merge one, or asked to check, triage or review open PRs (including one from an outside contributor), including from a cloud session that has no memory of any of this.
---

# Reviewing a pull request before it merges

Every PR is reviewed twice by models: once before it opens and once on the finished PR, and neither review is by the model that wrote the code. Green CI replaces neither: the Tests workflow proves the unit tests and `check_site.py` pass, not that a model looks right, faces the right way or opens about the right pivot.

Adapted from the review process in the owner's other projects.

## Every PR gets a detailed description

Use the headings in `.github/pull_request_template.md`: summary, what changed, why, how to try it (which model to open in the browser, which command to run), what was checked (and what was not), licence and credit, risks, and the Reviews checklist. Tools that open a PR with a body do not apply the template, so write the sections yourself.

## 1. Before the PR opens: a review by a different model

Always. The model that wrote the code shares its own wrong assumptions. Run it as a sub-agent with a model override (the Agent tool's `model` parameter), not as `/code-review` in the session that wrote the code. If you cannot choose another model (no sub-agent tool, no model parameter), stop and tell the user: never review your own code with the same model.

| Written by | First review (before the PR opens) | Final review (before merge) |
|---|---|---|
| Opus | Sonnet | Fable |
| Sonnet | Opus | Fable |
| Fable | Sonnet | Opus |
| Haiku, or anything else | Sonnet | Fable |

"Written by" means the model that wrote the code, not the one that planned it. The session can plan on Opus and hand the coding to the `implementer` agent (`.claude/agents/implementer.md`, Sonnet). Then the code is Sonnet's:
- **Reviews**: the first review is Opus and the final one Fable, as in the table. Run the Opus review as a fresh sub-agent briefed with what the change is meant to do. Do not run it in the planning session, and do not brief it with the plan: the plan's wrong assumptions are what it should catch. The session's own look at the implementer's report is not one of the two reviews.
- **Fixes**: send fixes for review findings back through the implementer, so that the code stays Sonnet's. If the planner writes code too, both models wrote it, so both reviews go to Fable, run as two separate fresh sub-agents; say so in the PR.
- **Commits**: the session commits. It adds a `Co-Authored-By` trailer for the model the implementer's report names (for example `Claude Sonnet <version> <noreply@anthropic.com>`) after its own, and the PR's "Written by" line names the implementer's model.
- **Shipping**: the rest of `ship-it` (manifest, docs and counts, `CREDITS.md`, the Sonar check after the push) is the session's job, not the implementer's.

Brief the reviewer with: the repo path; the diff range as `origin/<base>...<commit>` after a `git fetch` (`<base>` is the PR's base branch: `main`, or the parent branch of a stacked PR), never a bare `main...`; that it is read-only (no edits, commits or GitHub posts); what the change is meant to do; and to hunt for bugs with a concrete failure scenario each, including in unchanged code whose assumptions the change broke. Ask for at most 15 findings with file:line and a confidence, and for it to say plainly if it finds nothing.

Point it at what matters most in this project:

- **Licence and credit**: any file, mesh, image, font or script copied from somewhere else (it needs a `CREDITS.md` entry and a compatible licence); a library, Poly Pizza, Sketchfab or `generate_3d` model where the project builds its own; every GLB keeps `asset.copyright`
- **Palette**: `common.PALETTE` is append-only; a reordered or removed swatch silently recolours every model. Colours by name, not RGB
- **Axes and pivots**: front faces -Y in Blender (+Z in glTF); origin on the floor; moving parts have their origin on the pivot, and `manifest.json` part data is in **glTF axes**; the sign rule in `blender-assets`
- **Manifest and catalog**: ids unique and unchanged for existing models; `tools/catalog.py` type is three levels; variants point at models that exist; thumbnails and GLBs present; counts in README/NOTES match the manifest
- **Site code** (`site/`): no new network calls or third-party scripts (three.js is vendored on purpose); works at phone width and from the URL hash; no `innerHTML` with manifest text; any change to the vendored three.js needs a CREDITS entry
- **Workflows**: pinned action SHAs kept, `permissions:` as narrow as possible, no secrets exposed to pull-request code from forks, nothing that publishes on a PR
- **Generator scripts**: they must be runnable under `run_name="__main__"` through the Blender MCP; no absolute paths from one machine; a shared-helper or palette change needs every site group rebuilt with `tools/build_site_assets.py` (not only `build_all.py`)

Run it in the background. When it returns: check each finding against the code before acting on it; fix the real ones on the branch; write down the ones not fixed, with why, in the PR description; say in the description which model reviewed it and what became of each finding. If the code then changes well beyond fixes to those findings, run this step again.

## 2. CI

The Tests workflow (`.github/workflows/tests.yml`) runs on every PR and on pushes to `main`: unit tests and `check_site.py`, standard library only, about half a minute. The repository is public, so minutes are not the constraint; still, fix everything you can find locally, read a failed run's whole log before touching anything, push the fixes together, and stop and ask after two failed fix attempts on the same check. Read the result on the head commit, not an earlier one. A skipped job is not a pass. The Sonar workflow (`.github/workflows/sonar.yml`) fails the PR while SonarCloud reports any open issue on its new code; see `sonar-check`. There is no Blender CI (`docs/ci.md` proposes one): say in the PR what you rebuilt and looked at.

## 3. The final model review of the finished PR

When everything else is done, run the final reviewer from the table as a sub-agent on the whole PR as it now stands, with the same brief. Tell it what the earlier review found and what became of each, so it spends its time on what was missed. Handle its findings as in step 1, and say on the PR that it ran.

## 4. Pull requests from other people

A contributor's PR is untrusted input. Read the whole diff first, and **do not run any contributor script in the owner's Blender (or anything else on this machine) without the owner's explicit go-ahead**: a script Blender runs has full `bpy` and file-system access. Check the licence of every added file against `LICENSES.md`: contributed models and code come in under the project's licences (MIT for code, CC BY 4.0 for models and data), so ask the contributor to say so in the PR, and for anything they did not make, where it came from. Thank them; credit them in `CREDITS.md` if they ask. Do not run their workflow changes with elevated permissions. Never merge for them without the owner's say.

## 5. Merge

- **Merging is the user's call.** Do not merge or enable auto-merge unless the user has said to. The repo deletes a PR's branch when it merges (the "Automatically delete head branches" setting), so do not delete it by hand; clean up locally afterwards: `git worktree remove` the branch's worktree if it has one, then `git branch -D <branch>` (after checking the branch tip is the PR's merged head: `git rev-parse <branch>` equals `gh pr view <n> --json headRefOid`; after a squash `git log origin/main..<branch>` always lists the commits) and `git fetch --prune`.
- Every box in the PR's Reviews checklist is ticked.
- The final review ran on the latest commit, or on one that the later commits only fixed its findings in; the PR description lists those later commits.
- The Tests check is green on the latest commit, and the PR says what was looked at in the browser.
- Squash merge (the history up to PR #157 is merge commits). Merge with `gh pr merge <n> --squash --subject "<PR title> (#<n>)" --body-file <file>`, the file holding the summary and ending, after a blank line, with the `Co-Authored-By` trailer of each distinct model that wrote a commit: `main` gets one commit per PR, and the review rounds stay in the PR description, not in the history. The "Squash and merge" button on github.com does not do this (this repo's default makes the body all the commit messages and a one-commit PR takes the commit's title): use the command, or edit the title and body in the dialog.
- A PR stacked on this one: the squash leaves it holding the parent's original commits, which then conflict. Before the parent's branch is deleted, retarget the stacked PR to `main` (or it closes and cannot be reopened). Then, before its final review, `git rebase --onto origin/main <the parent PR's head commit> <stacked branch>` (`gh pr view <parent> --json headRefOid`; the stacked branch must sit on that final head, otherwise use the parent commit it was built on) and force-push with the owner's say. To avoid the rebase, merge the stacked PR into the parent's branch first and squash the parent alone: that combined PR gets a fresh final review and both PR numbers in the subject.
