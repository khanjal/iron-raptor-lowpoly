---
name: ship-it
description: The end-to-end procedure for landing a change in khanjal/iron-raptor-lowpoly (Blender-generated low-poly models and their static asset browser) once the work is ready — confirm the branch, run the unit tests and check_site.py and report the real results, update the manifest and docs, commit with the right trailer, push a feature branch, open the PR from the template. Use this whenever finishing a change here, whenever about to commit, push or open a PR, even if the user just says "commit this", "ship it" or "let's land this".
---

# Shipping a change in Iron Raptor Lowpoly

Adapted from the `ship-it` skills in the owner's other projects. Each step exists because skipping it causes trouble later; follow the sequence, and judge a step that clearly does not apply rather than forcing it. The two model reviews (`pr-review`) are never the step that does not apply, however small the change.

## 1. Confirm the starting point

`git status` and `git branch --show-current`. **Never commit to `main`.** One topic per branch: `models/<slug>`, `site/<slug>`, `docs/<slug>`, `fix/<slug>`, or `issue-<n>-<slug>` when an issue exists. If you are on `main`, branch before editing. Leave changes that are not yours (an uncommitted file in the tree) alone: stage by name, never `git add -A`.

## 2. Make the change

Match the surrounding style. Don't refactor unrelated code in passing. For a model, follow the `blender-assets` skill, including the site's files (GLB, catalog entry, manifest, thumbnail). The palette is append-only and an existing model id keeps its name.

## 3. Run the checks and report real results

```bash
python -m unittest discover -s tests -t .     # unit tests
python tools/check_site.py                    # manifest, GLBs, thumbnails, pivots, credit lines, page files
```

Report what each printed: PASS, FAIL or SKIPPED. **SKIPPED is not a pass**, and nothing here compiles or renders the Blender scripts in CI: if you changed `art/scripts/`, say which models you rebuilt and looked at, and which you did not. Never write "works" for something nobody ran or looked at. For anything visible in the browser, run the site locally and look (see `blender-assets`, "After the build").

## 4. Document it

- `README.md`: model counts (badge, intro, "The asset browser"), categories, rebuild steps when they change.
- `CREDITS.md` / `LICENSES.md`: anything vendored or copied in, before it is committed.
- `NOTES.md`: a dated line for decisions and what is not done or not checked.
- `art/README.md`: new script files.

## 5. Commit

Small, focused commits. Subject: a short imperative line (what and why, not how); a body when the reason isn't obvious. Don't write that something is tested, fixed or working unless it ran. End with the trailer the session instructs, for example:

```
Co-Authored-By: <the model that wrote it> <noreply@anthropic.com>
```

("Written by" in the PR checklist is read off this trailer.) The repository is public: no private paths, tokens, personal data or other people's files in a commit.

## 6. Push and open the PR

Pushing a branch and opening a PR publish to GitHub: do it when the user has asked for it or agreed to it. Then:

1. `git fetch origin` and check the branch is on top of its base (`origin/main`, or the parent branch of a stacked PR; do not rebase a stacked branch onto `main` while its parent is open; after the parent is squash-merged, `pr-review` step 5 says how).
2. First model review by a *different* model (`pr-review`), findings handled.
3. `git push -u origin <branch>`; open the PR (a draft if it is unfinished) with the body from `.github/pull_request_template.md` filled in (tools that take a body do not apply the template), `Closes #<issue>` when it closes one, and labels (`area:generators`, `area:site`, `area:ci`, `area:docs`).
4. The Tests workflow runs on every PR (about half a minute, free on a public repository). Read the result on the head commit. The Sonar workflow also runs and fails the PR if it adds any open SonarCloud issue: run `python tools/sonar_issues.py <pr> --wait`, report the count and fix what it lists (`sonar-check`).
5. The final review as `pr-review` describes. Merge only when the user says to.

Models that came from a request in an issue: say in the PR who asked (by issue link), and thank them in the issue when it closes.

## 7. After merge

Switch to `main` and pull. The repo deletes the remote branch when the PR merges; remove your local branch and worktree (`git worktree remove`, `git branch -D`: after a squash `git branch -d` refuses because the commits are not in `main`, which is not a failed merge; `git fetch --prune`). A merge that changes `site/` deploys the site (Pages workflow); a `v*` tag builds the release zips (`release.yml`) and is the owner's call.
