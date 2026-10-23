"""The named people of the asset list (GP-30..GP-56 and friends) and the humanoid aliens (GA-01 Grey, GA-02 Shadow Entity, GA-05 Nordic, the Reptilian),
each a few arguments to gp_builder.build.

Run in Blender:  import runpy; runpy.run_path(r"<repo>/art/scripts/gp_cast.py", run_name="__main__")
Optional global CAST_LIST to build only some, e.g. CAST_LIST = ["sheriff"]. Exports
Assets/Art/Global/People/GP_<Name>_01.fbx. The characters stand in a row along X to be looked at together.
All of them share the humanoid rig, so the Universal Animation Library clips play on every one.

Heights are set with `scale` (1.0 is the rig's 1.84 m), so the cast reads as a real crowd: adults 1.6-1.95 m, a child
1.3 m. `head_scale` enlarges the head, `shape` picks the silhouette (sex).

The people's BUILD (issue #269) is not set here: each person's role in art/data/content/builds.json has a mass factor `mf` (BMI / 23.5: 0.8 very slim, 1.0 average,
1.2 stocky, 1.45 heavy, 1.6 very heavy) and the loop under CAST gives every person that role's region mf, which gp_builder.build turns into a belly, a thicker neck, thighs
and arms and a fuller face (art/scripts/builds.py). The aliens keep `girth`, the one-factor widening of the body.
"""

import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import builds
import gp_builder
importlib.reload(builds)
importlib.reload(gp_builder)

CAST = {
    # GP-30 Farmer: big, flannel shirt, work jeans, a feed cap, a grey beard
    "farmer": dict(outfit=dict(skin="skin_tan", shirt="flannel", pants="denim", shoes="wood_dark", hair="hair_grey"), hat="cap",
                   sleeve=0.80, extras=["beard"], scale=1.01, shape="masculine"),
    # GP-32 Farmer's spouse: house dress, long hair
    "farmer_spouse": dict(outfit=dict(skin="skin_pale", shirt="cream", pants="skin_pale", shoes="wood_dark", hair="hair_blond"), hair="long",
                          extras=["skirt"], scale=0.90, shape="feminine"),
    # GP-31 Farmer's kid: about 1.3 m, a big head
    "farmer_kid": dict(outfit=dict(skin="skin_pale", shirt="denim", pants="rust", shoes="rubber", hair="hair_blond"), scale=0.71, head_scale=1.38),
    # GP-33 Grandparent: smaller, a cardigan and a fedora
    "grandparent": dict(outfit=dict(skin="skin_pale", shirt="grey_suit", pants="brown_coat", shoes="wood_dark", hair="hair_grey"), hat="fedora",
                        sleeve=0.80, scale=0.92),
    # GP-35 Sheriff: tall, tan uniform, campaign hat, badge
    "sheriff": dict(outfit=dict(skin="skin", shirt="tan_uniform", pants="navy", shoes="black", hair="hair_black"), hat="campaign",
                    sleeve=0.80, extras=["badge"], scale=1.04, shape="masculine"),
    # GP-36 Deputy: the same uniform, shorter sleeves, no hat
    "deputy": dict(outfit=dict(skin="skin_dark", shirt="tan_uniform", pants="navy", shoes="black", hair="hair_black"), hair="buzz",
                   sleeve=0.36, extras=["badge"], scale=0.98, shape="masculine"),
    # GP-38 FBI field agents: dark suit, white shirt, tie (one man, one woman)
    "fbi_agent": dict(outfit=dict(skin="skin_pale", shirt="navy", pants="navy", shoes="black", hair="hair_blond"), sleeve=0.80, suit=True,
                      extras=["tie"], scale=1.0),
    "fbi_agent_f": dict(outfit=dict(skin="skin_tan", shirt="navy", pants="navy", shoes="black", hair="hair_black"), hair="long", sleeve=0.80,
                        suit=True, extras=["tie"], scale=0.93, shape="feminine"),
    # GP-43 Man in Black: black suit, white shirt, black tie, sunglasses, identical for every one
    "mib": dict(outfit=dict(skin="skin_pale", shirt="black", pants="black", shoes="black", hair="hair_black"), hair="buzz", sleeve=0.80,
                suit=True, extras=["tie", "sunglasses"], scale=1.0),
    # GP-21 Townsfolk: a mechanic-type in a hard hat and hi-vis vest
    "worker": dict(outfit=dict(skin="skin_dark", shirt="denim", pants="grey_suit", shoes="rubber", hair="hair_black"), hat="hardhat",
                   sleeve=0.80, extras=["vest"], scale=0.98, shape="masculine"),
    # GP-46 Waitress / diner: apron-coloured dress, long hair
    "waitress": dict(outfit=dict(skin="skin_tan", shirt="cloth_red", pants="skin_tan", shoes="black", hair="hair_black"), hair="long",
                     extras=["skirt"], scale=0.92, shape="feminine"),
}
for _key, _spec in CAST.items():                      # the people's build: the region mf of their role (art/data/content/builds.json); `girth` is not used for them
    _role = builds.role_for_cast(_key)
    if _role:
        _spec["mf"] = builds.region_mf(_role)

STYLE = globals().get("STYLE", "faceted")           # "smooth" for the rounded version (files get a _smooth suffix)
ALIENS = {
    # GA-01 Grey: about 1.2 m, a huge head, spindly limbs, no clothes
    "grey": dict(outfit=dict(skin="alien_grey", shirt="alien_grey", pants="alien_grey", shoes="alien_grey", eyes="black"), hair="none",
                 scale=0.66, girth=0.62, head_scale=2.05, face="grey", joints=True, hands="grey"),
    # GA-02 Shadow Entity: tall, thin, light-absorbing, no readable face
    "shadow": dict(outfit=dict(skin="shadow", shirt="shadow", pants="shadow", shoes="shadow", eyes="glow_cyan"), hair="none",
                   scale=1.12, girth=0.55, head_scale=0.95, face="shadow", joints=True, hands="shadow"),
    # GA-05 Nordic: tall and pale, long blond hair, a pale robe, glowing eyes; looks almost human, which is the point
    "nordic": dict(outfit=dict(skin="skin_pale", shirt="linen", pants="linen", shoes="linen", hair="hair_blond", eyes="glow_cyan"), hair="long",
                   sleeve=0.80, extras=["skirt"], suit=True, scale=1.13, girth=0.86, head_scale=1.04, shape="neutral", face="nordic", joints=True),
}
ALIENS["reptilian"] = dict(   # the Reptilian: tall and broad, scaled green skin, a snout, gold slit eyes, a tail and a crest; bare, with darker claw-feet
    outfit=dict(skin="leaf_dark", shirt="leaf_dark", pants="leaf_dark", shoes="mould", eyes="paint_yellow"), hair="none",
    extras=["tail", "crest"], scale=1.08, girth=1.0, head_scale=1.0, shape="masculine", face="reptilian", joints=True, hands="reptilian")
CAST.update(ALIENS)

if __name__ == "__main__":
    names = globals().get("CAST_LIST") or list(CAST)
    for i, key in enumerate(names):
        spec = dict(CAST[key])
        title = key.title().replace("_", "") + ("" if STYLE == "faceted" else "_smooth")
        body, rig, coll = gp_builder.build(f"GP_{title}_01", export=f"Assets/Art/Global/People/GP_{title}_01.fbx", style=STYLE, **spec)
        print(gp_builder.common.stats(body))
        rig.location.x = 1.2 * i
    print("cast done", names)
