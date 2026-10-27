"""Build the models of the asset browser's first slice (run inside Blender, through the Blender MCP).

    import runpy
    runpy.run_path(r"<repo>/tools/build_site_assets.py", init_globals={"GROUPS": ["cars"]}, run_name="__main__")

GROUPS names entries of tools/catalog.py BUILD (ONLY=["cow"] limits an animals or people group to those keys) (default: all, but each group is its own call in practice: a group takes from a few seconds to a
minute and the MCP gives up on a long call). For every group it runs the art script with the group's settings, writes a GLB for each wanted model
into site/models/ and a small JSON of facts about it into out/meta/ (tools/make_manifest.py turns those into site/manifest.json), then removes
what it built.

The Blender file may be shared with other work, so a build never touches what it did not make: the static groups are built with a name prefix
(common.configure(prefix=...)) that no other collection, object or mesh has, and deleted again by that prefix; the rigged groups (animals, people, insects)
are built under their own names, which nothing else in the file uses, and only those collections are removed. The scene's fps and frame range, the
selection and the active object are put back.
"""

import importlib
import runpy
import sys
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "art" / "scripts"))
sys.path.insert(0, str(ROOT / "tools"))
import common
import catalog
import rename_glb
importlib.reload(common)
importlib.reload(catalog)

SCRIPTS = ROOT / "art" / "scripts"
PREFIX = "lpa:"
MODELS = ROOT / "site" / "models"
ONLY = globals().get("ONLY")                                              # people / animals: build just these keys of the group


def purge_prefix(prefix):
    """Delete the collections, objects and meshes whose names start with prefix (what a static build made)."""
    for o in [o for o in bpy.data.objects if o.name.startswith(prefix)]:
        bpy.data.objects.remove(o, do_unlink=True)
    for c in [c for c in bpy.data.collections if c.name.startswith(prefix)]:
        bpy.data.collections.remove(c)
    for m in [m for m in bpy.data.meshes if m.name.startswith(prefix) and m.users == 0]:
        bpy.data.meshes.remove(m)


def purge_collection(coll):
    """Delete one collection with its objects and their data (the rigged builds)."""
    rigs = [o for o in coll.all_objects if o.type == "ARMATURE"]
    for r in rigs:
        common.clear_clips(r)
    datas = [o.data for o in coll.all_objects if o.data is not None]
    # the loop removes from the live collection, so it iterates a copy
    for o in list(coll.all_objects):  # NOSONAR
        bpy.data.objects.remove(o, do_unlink=True)
    bpy.data.collections.remove(coll)
    for d in datas:
        if d.users == 0:
            (bpy.data.meshes if isinstance(d, bpy.types.Mesh) else bpy.data.armatures).remove(d)


class SceneGuard:
    """Put back what a clip script changes in the shared scene: fps, frame range, current frame, the active object and the selection."""

    def __enter__(self):
        sc = bpy.context.scene
        self.s = (sc.render.fps, sc.render.fps_base, sc.frame_start, sc.frame_end, sc.frame_current)
        self.active = bpy.context.view_layer.objects.active
        self.sel = [o for o in bpy.context.view_layer.objects if o.select_get()]
        return self

    def __exit__(self, *exc):
        if bpy.context.object is not None and bpy.context.object.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
        sc = bpy.context.scene
        sc.render.fps, sc.render.fps_base, sc.frame_start, sc.frame_end = self.s[:4]
        sc.frame_set(self.s[4])
        bpy.ops.object.select_all(action="DESELECT")
        for o in self.sel:
            if o.name in bpy.data.objects:
                o.select_set(True)
        if self.active is not None and self.active.name in bpy.data.objects:
            bpy.context.view_layer.objects.active = self.active


def build_static(g):
    """A group of static (or part-carrying) props: run the art script, which hands every finished model to common.export_fbx, which writes the GLB."""
    common.configure(reset=True, out=str(ROOT / "out"), glb=str(MODELS), formats="glb", only=set(g["ids"]), prefix=PREFIX)
    try:
        runpy.run_path(str(SCRIPTS / g["script"]), init_globals=dict(g.get("globals", {})), run_name="__main__")
    finally:
        purge_prefix(PREFIX)
        common.configure(reset=True)
    return g["ids"]


def key_person_clip(rig, name, pose, frames):
    import gp_clips
    importlib.reload(gp_clips)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.mode_set(mode="POSE")
    gp_clips.reset(rig)
    gp_clips.REST_LOW = gp_clips.lowest_foot(rig)
    action = bpy.data.actions.new(f"{rig.name}:{name}")
    rig.animation_data_create()
    rig.animation_data.action = action
    for frame in range(1, frames + 2):
        gp_clips.reset(rig)
        pose(rig, ((frame - 1) % frames) / frames)
        for pb in rig.pose.bones:
            pb.keyframe_insert("rotation_quaternion", frame=frame)
            if pb.name == "pelvis":
                pb.keyframe_insert("location", frame=frame)
    gp_clips.reset(rig)
    bpy.ops.object.mode_set(mode="OBJECT")
    common.stash_clip(rig, action, name, fps=gp_clips.FPS)


def build_people(g):
    import gp_clips
    importlib.reload(gp_clips)
    done = []
    for key, pid in g["people"].items():
        if ONLY and key not in ONLY:
            continue
        common.configure(reset=True, out=str(ROOT / "out"), glb=str(MODELS), formats="glb", only={pid})
        with SceneGuard():
            ns = runpy.run_path(str(SCRIPTS / "gp_cast.py"), init_globals={"CAST_LIST": [key]}, run_name="__main__")
            rig, coll = ns["rig"], ns["coll"]
            rig.location = (0, 0, 0)
            for clip in g["clips"]:
                pose, frames = gp_clips.CLIPS[clip]
                key_person_clip(rig, clip, pose, frames)
            common.export_glb(coll, pid)
            purge_collection(coll)
        common.configure(reset=True)
        done.append(pid)
    return done


def run_animal(g, key):
    """Build one animal or bird with its art script; returns (the script's namespace, the clips to add)."""
    import species_pets
    if g.get("birds"):
        ns = runpy.run_path(str(SCRIPTS / "gn_birds.py"), init_globals={"SPECIES_LIST": [key]}, run_name="__main__")
        return ns, []
    ns = runpy.run_path(str(SCRIPTS / "gn_animals.py"), init_globals={"SPECIES_LIST": [key], "STYLES_LIST": ["faceted"]}, run_name="__main__")
    return ns, g["clips"] + (g.get("dog_clips", []) if key in species_pets.DOGS else [])


def add_clip(rig, anim_prefix, clip, key, report):
    """Run the clip's script on the rig and stash its action under the clip's name."""
    import quadruped_rig
    import species_pets
    init = {"RIG_NAME": rig.name, "ANIM_PREFIX": anim_prefix, "EXPORT": False, "KEEP": True, "REPORT": report}
    if clip == "Idle":
        runpy.run_path(str(SCRIPTS / "quadruped_idle.py"), init_globals=init, run_name="__main__")
        fps = 24
    else:
        init["GAIT"] = clip.lower()
        if clip == "Walk" and key in species_pets.DOGS:
            init["SHOULDER_SLIDE"] = 0.45                          # as gn_animal_clips.py does for the dogs
        runpy.run_path(str(SCRIPTS / "quadruped_walk.py"), init_globals=init, run_name="__main__")
        fps = report[f"{anim_prefix}@{clip.lower()}"]["fps"]
    if bpy.context.object is not None and bpy.context.object.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")
    common.stash_clip(rig, rig.animation_data.action, clip, fps=fps)
    quadruped_rig.rest_pose(rig)


def build_animals(g):
    done = []
    for key, aid in g["animals"].items():
        if ONLY and key not in ONLY:
            continue
        common.configure(reset=True, out=str(ROOT / "out"), glb=str(MODELS), formats="glb", only={aid})
        with SceneGuard():
            report = {}
            ns, clips = run_animal(g, key)
            rig, coll = ns["rig"], ns["coll"]
            rig.location = (0, 0, 0)
            prefix = rig.name[:-len("_Rig")]                                  # GN_Cow_faceted
            anim_prefix = prefix[len("GN_"):]                                  # Cow_faceted
            for clip in clips:
                add_clip(rig, anim_prefix, clip, key, report)
            common.export_glb(coll, aid)
            purge_collection(coll)
        common.configure(reset=True)
        done.append(aid)
    return done


def build_critters(g):
    """The insects: insect_anim.py rigs each one from the moving pieces insects.py marks and keys its clips; one model at a time under the build prefix."""
    import insect_anim
    importlib.reload(insect_anim)
    done = []
    for key, aid in g["critters"].items():
        if ONLY and key not in ONLY:
            continue
        common.configure(reset=True, out=str(ROOT / "out"), glb=str(MODELS), formats="glb", only={aid}, prefix=PREFIX)
        try:
            with SceneGuard():
                _, rig, coll, clips = insect_anim.build_rigged(key)
                insect_anim.key_clips(rig, clips)
                common.export_glb(coll, aid)
                purge_collection(coll)
        finally:
            purge_prefix(PREFIX)
            common.configure(reset=True)
        done.append(aid)
    return done


if __name__ == "__main__":
    wanted = globals().get("GROUPS") or list(catalog.BUILD)
    for name in wanted:
        g = catalog.BUILD[name]
        kind = g.get("kind", "static")
        ids = {"static": build_static, "people": build_people, "animals": build_animals, "critters": build_critters}[kind](g)
        ids = rename_glb.rename_group(ids, catalog.SITE_IDS)         # the generator's name -> the browser's id
        print("built", name, len(ids), "models")
