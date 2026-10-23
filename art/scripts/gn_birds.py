"""Build the bird species in biped_bird.py in both styles and export each as a rigged FBX.

Run in Blender:  import runpy; runpy.run_path(r"<repo>/art/scripts/gn_birds.py", run_name="__main__")
Exports Assets/Art/Global/Animals/GN_<Species>_<style>_01.fbx. Optional globals SPECIES_LIST / STYLES_LIST.
"""

import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common
import quadruped_rig
import biped_bird
for m in (common, quadruped_rig, biped_bird):
    importlib.reload(m)

SPECIES = {"chicken_hen": biped_bird.CHICKEN_HEN, "turkey_tom": biped_bird.TURKEY_TOM, "turkey_hen": biped_bird.TURKEY_HEN}
SIZE = {"chicken_hen": 0.85}          # a hen is about 0.4 m tall to the comb; a tom turkey is about 1.0 m to the top of its head
names = globals().get("SPECIES_LIST") or list(SPECIES)
styles = globals().get("STYLES_LIST") or ["faceted"]
for r, style in enumerate(styles):
    for i, key in enumerate(names):
        sp = SPECIES[key]
        mesh, rig, coll = biped_bird.build(sp, style, scale=SIZE.get(key, 1.0))
        print(common.stats(mesh))
        common.export_fbx(coll, f"Assets/Art/Global/Animals/GN_{sp['name']}_{style}_01.fbx", rigged=True)
        rig.location = (0.8 * i, -3.0 - 0.8 * r, 0)
print("done", names, styles)
