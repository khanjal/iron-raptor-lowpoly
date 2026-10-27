# Tests and CI

## What exists now

| Check | Where | Runs |
|---|---|---|
| Unit tests: the Blender -> glTF axis conversion of the moving parts, the manifest entry builder, the catalog's rules for types and tags (`tests/test_manifest.py`, `tests/test_catalog.py`) | `python -m unittest discover -s tests -t .` | CI + locally |
| Site consistency: `python tools/check_site.py` (and `tests/test_check_site.py`, which also breaks a copy of the site on purpose to see each failure reported). For every manifest entry: the GLB and a 256 x 256 PNG exist, fields and types are valid, ids are unique, the triangle count equals the GLB's, `rigged` matches the GLB having a skin, `clips` equal the GLB's animation names, every `parts` entry names a node that exists in the GLB **at the part's pivot** (this is the check on the axis conversion, against the real files), variants exist and are symmetric; and the pages (`index.html`, `stress.html`): every file a page refers to exists, every element id its own script (`app.js`, `stress.js`) looks up is in its HTML | CI + locally |
| JavaScript syntax (`tests/test_js_syntax.py`, needs Node) | | CI + locally |

`.github/workflows/tests.yml` runs these on every pull request, on every push to `main` and by hand. It was manual-only while the repository was private on the Free plan (GitHub refused to start the one trial run: "recent account payments have failed or your spending limit needs to be increased"); since the repository became public on 2026-10-23 it runs on the standard runners. The job needs no install (standard library only) and takes well under a minute. `sonar.yml` fails a pull request while SonarCloud reports an open issue on its new code (`tools/sonar_issues.py`; no token, SonarCloud analyses the PR itself). `pages.yml` publishes `site/` when a change to it reaches `main`.

What is **not** covered by these tests: whether the page works in a browser (this was checked by hand in the built-in browser of the Claude desktop app, see the PR), and whether a model *looks* right.

## Proposal: a browser smoke test

A headless Chromium (Playwright) job that serves `site/`, opens `#GI_Fridge_01`, waits for the canvas to render, clicks the door and checks that the part button turns pressed, opens a person and selects Run, and fails on any console error. Cost: `pip install playwright` + `playwright install chromium` (a browser download of the order of 100 to 200 MB, roughly a minute per run) and a small script. Not added: it could not be run and tried here, and the Python checks above already catch the most likely breakages (a missing file, a manifest that does not match the models). Worth adding when the page grows or the repository is public.

## Proposal: a Blender job (not enabled, untested)

Goal: rebuild a few generators in CI and fail on (a) floating parts, (b) a triangle-budget regression, (c) a manifest that no longer matches what the scripts produce.

**Is `bpy` from PyPI practical?** What PyPI says (queried 2026-10-23, `https://pypi.org/pypi/bpy/json`):

- The package is "Blender as a Python module", author "Blender Foundation", licence GPL-3.0. Its description: "Each Blender release supports one Python version, and the package is only compatible with that version." and "Blender versions outside the current LTS window are removed from PyPI but are available at https://download.blender.org/pypi/bpy/".
- Versions on PyPI now: **5.2.3** (uploaded 2026-10-22), 5.2.2, 5.2.1, 5.2.0, 5.1.2, and the 4.5.x and 4.2.x LTS lines (4.5.15, 4.2.23). So the Blender used here, **5.2.3**, is on PyPI, and 5.2.x is the current line.
- `requires_python` is **`==3.13.*`** for 5.x (3.11 for 4.x). The wheels: `manylinux_2_28_x86_64` (**403 MB**), `win_amd64` (340 MB), `macosx_11_0_arm64` (245 MB), `win_arm64` (211 MB). Dependencies: `numpy>=2.2,<3`, `cattrs`, `cython`, `requests`, `zstandard`.

So a runner needs Python 3.13 (`actions/setup-python`) and a 403 MB download per job unless cached (`actions/cache` on pip's cache; the cache allowance is 10 GB per repository). Downloading Blender's own Linux archive from blender.org instead is a similar size and needs the extra steps of unpacking it and running `blender -b --python`; `bpy` is simpler. Either way the version must be **pinned** (`bpy==5.2.3`) because the generators' output can change between Blender versions.

**Not checked here** (needs a try on a runner, or an install of the wheel, which I did not do on this machine without asking): that the glTF exporter add-on (`io_scene_gltf2`) is available inside the `bpy` module without enabling it, that `bpy.ops.export_scene.gltf` runs without a GUI, and how long a build takes. The scripts only use `bpy`, `bmesh` and `mathutils`, and have been run through the Blender MCP in a normal Blender 5.2.3, not as a module.

**Sketch** (a manual workflow; the helper script `tools/ci_build.py` is not written):

```yaml
name: Blender build check
on: workflow_dispatch              # manual: 400 MB download, minutes of build; Free-plan minutes are limited
jobs:
  build:
    runs-on: ubuntu-latest
    timeout-minutes: 30
    steps:
      - uses: actions/checkout@<pinned sha>
      - uses: actions/setup-python@<pinned sha>
        with: { python-version: "3.13" }
      - uses: actions/cache@<pinned sha>
        with: { path: ~/.cache/pip, key: bpy-5.2.3 }
      - run: pip install bpy==5.2.3
      - run: python tools/ci_build.py        # see below
      - run: python tools/make_manifest.py && python tools/check_site.py
```

`tools/ci_build.py` would `import bpy`, call `common.configure(out="out", glb="site/models", formats="glb", prefix="ci:")` and run a short list of generators with the same `runpy` calls as `tools/build_site_assets.py` (one of each kind: a car, an interactive prop, a person with clips, an animal), then:

1. **Floating parts**: run `art/scripts/audit.py`'s `islands` / `groups_of` on every built model and compare with a committed baseline, `art/data/audit_baseline.json` (model name -> number of floating groups). Fail when a model is not in the baseline or has more groups than recorded. The audit over-reports by design (its docstring: it is "a bounding-box test"), so a baseline of accepted cases is needed; fail on new ones only.
2. **Triangle budget**: `tools/budget.json` with a ceiling per model (the current triangle count plus 10 %, or a per-category default); fail when `out/meta/<id>.json`'s `triangles` exceeds it. Run on every generator that the manifest uses.
3. **Manifest drift**: after building, `make_manifest.py` and `check_site.py` must pass, which catches a renamed part node or a changed pivot.

The pure parts (reading a baseline and a budget, comparing numbers) can be unit-tested without Blender, like the rest. The job would be started by hand before merging a change to `art/scripts`, and could move to "on push to a branch that touches `art/scripts/**`" once the repository is public.
