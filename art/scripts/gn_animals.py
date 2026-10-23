"""Build quadruped species from species.py in one or both styles and export each as a rigged FBX.

Run in Blender:  import runpy; runpy.run_path(r"<repo>/art/scripts/gn_animals.py", run_name="__main__")
Optional globals before running: SPECIES_LIST (default every species) and STYLES_LIST (default faceted only; "smooth" is the rounded variant), e.g.
    SPECIES_LIST = ["horse"]; STYLES_LIST = ["faceted"]
Exports Assets/Art/Global/Animals/GN_<Species>_<style>_01.fbx (the farm dog's other coats, species_pets.DOG_SKINS, are species of their own: SPECIES_LIST = ["dog_collie_yellow", ...]). The animals are spread along X in the scene so they
can be looked at together; positions do not affect the exports.
"""

import importlib
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common
import quadruped_rig
import quadruped_builder
import species_farm_dog
import species_pets
import species                       # first: it imports species_wild, which imports it back
import species_wild
for m in (common, quadruped_rig, species_farm_dog, species_pets, species_wild, species, quadruped_builder):
    importlib.reload(m)

names = globals().get("SPECIES_LIST") or list(species.SPECIES)
styles = globals().get("STYLES_LIST") or ["faceted"]
row = 0
for style in styles:
    for key in names:
        sp = species.SPECIES[key]
        mesh, rig, coll = quadruped_builder.build(sp, style)
        print(common.stats(mesh))
        out = common.export_fbx(coll, f"Assets/Art/Global/Animals/GN_{sp['name']}_{style}_01.fbx", rigged=True)
        mesh.location.x = rig.location.x = 3.2 * row
        mesh.location.y = rig.location.y = 3.0 * styles.index(style)
        row += 1
    row = 0
print("done", names, styles)
