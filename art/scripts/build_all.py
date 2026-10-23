"""Rebuild every model in the repo: run each asset script in turn, re-exporting all the FBX files.

Run in Blender:  import runpy; runpy.run_path(r"<repo>/art/scripts/build_all.py", run_name="__main__")
Optional globals: GROUPS (a list of group names, default all) and WITH_CLIPS (True also regenerates the animal walk and idle clips,
which do not depend on the palette and are slow).

Needed whenever common.py's palette changes shape (a new grid size moves every swatch in the texture), and a handy way to check
that nothing has rotted. Groups: bucket, base, animals, birds, people, props, vehicles, buildings, kit, vegetation, aliens, household, decor, homestyles (about a minute), ships, cars, ground, contents, interactive (about a minute), terminals, ship_props, ship_hulls.
Not in any group (run each directly, they export their own FBX): insectoid.py (the Insectoid with its clips) and gp_clips.py (the people's Idle, Sit, Walk and Run).
"""

import io
import contextlib
import runpy
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

SCRIPTS = {
    "bucket": "gt_bucket.py", "base": "gp_humanoid.py", "animals": "gn_animals.py", "birds": "gn_birds.py", "people": "gp_cast.py",
    "props": "props_farm.py", "vehicles": "vehicles.py", "buildings": "buildings.py", "kit": "kit.py", "vegetation": "vegetation.py",
    "aliens": "aliens.py", "insectoid": "insectoid.py", "household": "household.py", "decor": "decor.py", "homestyles": "home_styles.py", "ships": "ships.py",
    "cars": "cars.py", "ground": "ground.py", "contents": "contents.py", "interactive": "interactive.py", "terminals": "terminals.py",
    "ship_props": "ship_props.py", "ship_hulls": "ship_hulls.py",
}
groups = globals().get("GROUPS") or list(SCRIPTS)
if not globals().get("GROUPS"):
    # a full rebuild starts art/data/interactions.json afresh, so an entry for a prop that no longer exists does not linger
    (HERE.parent / "data" / "interactions.json").unlink(missing_ok=True)
for g in groups:
    t0 = time.time()
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            runpy.run_path(str(HERE / SCRIPTS[g]), run_name="__main__")
    except Exception:
        print(f"{g} FAILED; its output so far:\n" + buf.getvalue()[-1500:])
        raise
    done = [l for l in buf.getvalue().splitlines() if "done" in l]
    print(f"{g:11s} {time.time() - t0:5.1f}s  {done[-1] if done else ''}")
if globals().get("WITH_CLIPS"):
    runpy.run_path(str(HERE / "gn_animal_clips.py"), run_name="__main__")
    print("clips done")
print("build_all finished:", groups)
