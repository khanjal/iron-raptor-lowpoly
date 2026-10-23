"""Generate the gait and idle clips for species built by gn_animals.py, one FBX file per clip.

Run in Blender after gn_animals.py (which builds the rigs):
    import runpy; runpy.run_path(r"<repo>/art/scripts/gn_animal_clips.py", run_name="__main__")
Optional globals: SPECIES_LIST and STYLES_LIST as in gn_animals.py, CLIPS (default ["walk", "idle", "trot", "run"]: which clips to make) and
EXPORT=False (build and print the speed and foot-slide report, write nothing; the dict REPORT, if given, is filled in).
Writes Assets/Art/Global/Animals/Anims/<Species>_<style>@Walk.fbx, @Idle.fbx and, for the dogs only (the species in species_pets.DOGS),
@Trot.fbx and @Run.fbx, so Unity names the clips Walk, Idle, Trot and Run. The walk adapts to each animal's leg length: stride, cadence
and body drop are derived from the skeleton. The dogs' legs, from the elbow down, are too short to take a real stride, so their walk, trot
and run also slide the tops of the legs along the body (the shoulder blade and the hip: SHOULDER_SLIDE in quadruped_walk.py); every dog
gait is made for a ground speed that follows from its leg length, and each clip's speed is written to Anims/gait-speeds.json for the
animator tool (Assets/Editor/FarmsteadAnimals.cs) to set its blend thresholds.

The Blender file may be shared with other work: the clip scripts (quadruped_walk.py, quadruped_idle.py) replace only their own action and
export only that one, so other actions in the file are left alone.
"""

import json
import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import common
import species
import species_pets

REPO = HERE.parents[1]
SPEED_FILE = common.out_dir() / "Assets" / "Art" / "Global" / "Animals" / "Anims" / "gait-speeds.json"
DOG_SLIDE = 0.45                                           # the walk's slide, as a fraction of the leg length (the trot and run have their own in quadruped_walk.py)

names = globals().get("SPECIES_LIST") or list(species.SPECIES)
styles = globals().get("STYLES_LIST") or ["faceted"]
clips = globals().get("CLIPS") or ["walk", "idle", "trot", "run"]
export = globals().get("EXPORT", True)                     # False: build and report only, write nothing
report = {}
for style in styles:
    for key in names:
        if key in species_pets.DOG_SKINS:                  # the farm dog's other coats are models only: the game swaps their mesh onto the dog that has the clips
            continue
        sp = species.SPECIES[key]
        is_dog = key in species_pets.DOGS
        init = {"RIG_NAME": f"GN_{sp['name']}_{style}_Rig", "ANIM_PREFIX": f"{sp['name']}_{style}"}
        for clip in clips:
            if clip in ("trot", "run") and not is_dog:
                continue
            if clip == "idle":
                runpy.run_path(str(HERE / "quadruped_idle.py"), init_globals=dict(init, EXPORT=export), run_name="__main__")
                continue
            gait = dict(init, GAIT=clip, REPORT=report, EXPORT=export)
            if clip == "walk" and is_dog:
                gait["SHOULDER_SLIDE"] = DOG_SLIDE
            runpy.run_path(str(HERE / "quadruped_walk.py"), init_globals=gait, run_name="__main__")

if report and export:
    # merge this run's gaits into the file: one entry per species and gait
    entries = {}
    if SPEED_FILE.exists():
        for e in json.loads(SPEED_FILE.read_text(encoding="utf-8")).get("clips", []):
            entries[(e["species"], e["gait"])] = e
    for name, r in report.items():
        prefix, gait = name.split("@")
        species_name = prefix.split("_")[0]
        if gait == "walk" and not species_name.startswith("Dog"):
            continue                                       # only the dogs' walk is fitted to a speed: the other animals' walks are the old shuffle
        entries[(species_name, gait.capitalize())] = dict(species=species_name, gait=gait.capitalize(), speed=r["speed"], strideSeconds=round(r["frames"] / r["fps"], 4),
                                                         footSlideCm=r["drift_cm"], legMetres=r["leg_m"])
    ordered = [entries[k] for k in sorted(entries)]
    SPEED_FILE.write_text(json.dumps({"clips": ordered}, indent=2) + "\n", encoding="utf-8")
    print("wrote", SPEED_FILE)
print("clips done", names, styles, clips)
