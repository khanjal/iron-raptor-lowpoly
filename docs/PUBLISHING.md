# Before this repository goes public

Status: **public since 2026-10-23** (the owner chose to publish this repository directly, to start using GitHub Pages; the commit email below is therefore already in the public history). Kept for reference: the steps that were not done, and what remains (name, third-party audit).

## 1. The commit email (do this first)
Every commit so far has `khanjal@gmail.com` as author and committer (10 commits on 2026-10-23, plus the ones on the open branches). In a public repository that address is visible in the commit data and cannot be taken back. Use GitHub's no-reply address instead: `1860742+khanjal@users.noreply.github.com` (the id comes from `gh api user --jq .id`; confirm it under GitHub Settings, Emails).

**The trap:** GitHub keeps a hidden ref for every pull request (`refs/pull/<n>/head`). Those refs cannot be deleted by the owner and keep the old commits reachable, even after the branch is rewritten or deleted, and a repository that is made public exposes them. So rewriting history in place is not enough while pull requests exist (PR #1 does). The safe way is to publish from a **new repository**:

1. Finish the work in this private repository (merge the open pull requests, or fold the branches together).
2. In GitHub Settings, Emails: tick "Keep my email addresses private" and "Block command line pushes that expose my email".
3. Set the no-reply address for new commits in this clone: `git config user.email 1860742+khanjal@users.noreply.github.com`.
4. Make a fresh clone of the merged `main` and rewrite the authors there (`pip install git-filter-repo`, then `git filter-repo --mailmap mailmap.txt` with the single line `Justin <1860742+khanjal@users.noreply.github.com> <khanjal@gmail.com>`; add a second line to change the name if you do not want "Justin" shown).
5. Check nothing is left: `git log --all --format='%ae %ce' | sort -u` must show only the no-reply address (and `noreply@anthropic.com` from co-author trailers, which is fine).
6. Create a brand-new repository with the final name, push only the rewritten `main` (no other branches, no pull requests), set it public, and delete this private one.

(If you would rather keep this repository, GitHub Support can remove cached pull-request refs on request; a new repository avoids the wait. This is from GitHub's behaviour as I understand it, not something tested here.)

## 2. Licence
Done on the `licence` branch: [LICENSE](../LICENSE) (MIT, code), [LICENSE-MODELS](../LICENSE-MODELS) (CC BY 4.0, models and data), [LICENSES.md](../LICENSES.md) (what applies where and how to credit), [CREDITS.md](../CREDITS.md). Confirm the copyright line in `LICENSE`, and that you are happy with attribution-required.

## 3. Third-party audit
`CREDITS.md` lists the vendored three.js and the Quaternius skeleton layout. Before publishing: check `site/vendor/` and `art/data/` for anything else, and that no file or mesh from the reference packs (Kenney, Quaternius) was copied in.

## 4. Name
The project is called **Iron Raptor Lowpoly** (it was `lowpoly-assets` while it was a working name; the repository was renamed to `iron-raptor-lowpoly` on 2026-10-24). The site address (`<user>.github.io/<name>`) and the credit line in `LICENSES.md` carry the name.

## 5. The site
GitHub Pages works from a public repository on the Free plan (not from a private one). In the new repository: Settings, Pages, source "GitHub Actions"; enable the Pages workflow (it is manual-only now, see `docs/ci.md`); run it once and open the site. Add the site address to the repository's About box and the README.

## 6. After publishing
Check the home page and the README render, the licences show in GitHub's sidebar, and the site's models load. Nothing here needs Git LFS, so forks cost the owner no bandwidth.
