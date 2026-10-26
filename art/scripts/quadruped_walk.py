"""Quadruped gait cycles (walk, trot, run) for the shared rig (quadruped_rig.py). Works on any animal built from that rig.

Run in Blender after the animal is built (gn_animals.py), with RIG_NAME and ANIM_PREFIX passed via init_globals (gn_animal_clips.py does this):
    import runpy; runpy.run_path(r"<repo>/art/scripts/quadruped_walk.py", run_name="__main__")
Optional globals: GAIT ("walk", the default, "trot" or "run"), TARGET_SPEED (m/s the clip should look right at; trot and run only),
EXPORT (False = build and report, write nothing), REPORT (a dict the script fills with the clip's numbers).
Creates the action "Quadruped_<Gait>" on the rig (the last frame = the first, a whole number of strides) and exports
Assets/Art/Global/Animals/Anims/<ANIM_PREFIX>@<Gait>.fbx (@Walk, @Trot, @Run: Unity names the clip from the @).

The walk (24 fps, 36-frame stride for the cow): a lateral-sequence walk (hind left, front left, hind right, front right, a quarter cycle apart).
Each leg's upper bone swings back through the stance phase (60% of the cycle) and returns in the swing phase with the lower leg folded
to clear the ground. During stance the lower-leg angle is solved every frame so the hoof stays on the ground and flat.

The trot (60 fps): diagonal pairs (front left + hind right, front right + hind left) move together, each on the ground for 46% of the cycle,
so there is a brief moment with all four feet in the air; the body bobs twice a stride, the legs fold higher in the swing.

The run (60 fps) is a rotary gallop: hind left, hind right, front left, front right land in turn, each foot on the ground for only a fifth of
the stride; between the front feet leaving and the hind feet landing the legs are gathered under the body and the spine arches, then it
stretches for the next reach (spine and hips pitch once a stride, the body rises in both flight phases).

Every clip is made for a ground speed (the walk's follows from the leg length, the trot's and run's are TARGET_SPEED, lowered when the leg
cannot reach that far): a planted hoof travels, relative to the body, exactly the distance the body covers while it is down, which is what
keeps the feet from skating. The stance of the trot and run is also bent so that the hoof moves at a constant speed along the ground (the
walk's swings at a constant angle, which is slightly faster in the middle). The report at the end prints the ground speed and "foot slide":
how far the planted hoof drifts from where it should be if the body moves at that speed (cm, worst foot), and its height above or below the ground.
"""

import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import importlib
import common
import quadruped_rig
importlib.reload(common)
importlib.reload(quadruped_rig)

RIG_NAME = globals().get("RIG_NAME", "GN_Cow_Rig")
GAIT = globals().get("GAIT", "walk")
EXPORT = globals().get("EXPORT", True)
KEEP = globals().get("KEEP", False)                        # leave the action on the rig (to look at it in Blender); the caller removes it
REPORT = globals().get("REPORT")
ACTION = "Quadruped_" + GAIT.capitalize()
STRIDE_FRAMES = globals().get("STRIDE_FRAMES")             # frames per stride; default scales with leg length (walk) or follows from the speed
TARGET_SPEED = globals().get("TARGET_SPEED")               # m/s, trot and run
STRIDE_LENGTH = globals().get("STRIDE_LENGTH")            # metres each planted hoof travels per stance; default scales with leg length
BODY_DROP = globals().get("BODY_DROP")                      # the standing legs are near straight, so a walking body sits lower; default scales with leg length

GAITS = {
    "walk": {"fps": 24, "offset": {"HindUpper_L": 0.0, "FrontUpper_L": 0.25, "HindUpper_R": 0.5, "FrontUpper_R": 0.75},
                 "stance": {"Front": 0.6, "Hind": 0.6}, "flex": {"Front": 42.0, "Hind": 38.0}, "linear_stance": False, "max_cadence": None, "slide": 0.0},
    "trot": {"fps": 60, "offset": {"HindUpper_L": 0.0, "FrontUpper_R": 0.0, "HindUpper_R": 0.5, "FrontUpper_L": 0.5},
                 "stance": {"Front": 0.46, "Hind": 0.46}, "flex": {"Front": 58.0, "Hind": 52.0}, "linear_stance": True, "max_cadence": 2.7, "slide": 0.45},
    "run": {"fps": 60, "offset": {"HindUpper_L": 0.0, "HindUpper_R": 0.08, "FrontUpper_L": 0.40, "FrontUpper_R": 0.48},
                "stance": {"Front": 0.20, "Hind": 0.22}, "flex": {"Front": 75.0, "Hind": 70.0}, "linear_stance": True, "max_cadence": 3.3, "slide": 0.55},
}
CFG = dict(GAITS[GAIT])
if GAIT == "walk" and globals().get("SHOULDER_SLIDE"):
    # a walk for an animal whose legs are too short to take a real stride from the elbow (the dogs): the tops of the legs slide too, like the trot and run
    CFG.update(fps=60, slide=SHOULDER_SLIDE, linear_stance=True, max_cadence=1.4)
FPS = CFG["fps"]
OFFSET = CFG["offset"]
STANCE = CFG["stance"]
FLEX = CFG["flex"]
SWING_ANGLE = {"Front": 22.0, "Hind": 21.0}     # degrees each side of upright (replaced by the fitted angle below)
FLEX_SIGN = {"Front": 1.0, "Hind": -1.0}       # knees fold the foot back, hocks fold it forward

rig = bpy.data.objects[RIG_NAME]
saved_active = bpy.context.view_layer.objects.active
saved_scene = (bpy.context.scene.render.fps, bpy.context.scene.frame_start, bpy.context.scene.frame_end, bpy.context.scene.frame_current)
rig.hide_viewport = False                       # pose mode needs a visible rig
rig.hide_set(False)
ANIM_PREFIX = globals().get("ANIM_PREFIX", "Quadruped")
LEG_LENGTH = rig.data.bones["FrontUpper_L"].head_local.z
if BODY_DROP is None:
    BODY_DROP = round(0.098 * LEG_LENGTH, 3)            # 0.09 m for the cow
bpy.context.view_layer.objects.active = rig
bpy.ops.object.mode_set(mode="POSE")
pb = rig.pose.bones
for b in pb:
    b.rotation_mode = "XYZ"


def smooth(x):
    return x * x * (3 - 2 * x)


def rad(d):
    return math.radians(d)


def set_rot(name, x=None, y=None, z=None):
    r = list(pb[name].rotation_euler)
    for i, v in enumerate((x, y, z)):
        if v is not None:
            r[i] = rad(v)
    pb[name].rotation_euler = r


def foot_tip(side_name):
    return rig.matrix_world @ pb[side_name].tail


def solve_lower(kind, side, upper_deg, target_z=0.0):
    """Lower-leg angle (degrees) that puts the hoof tip on the ground for this upper-leg angle, hoof kept flat."""
    up, lo, ft = f"{kind}Upper_{side}", f"{kind}Lower_{side}", f"{kind}Foot_{side}"
    set_rot(up, x=upper_deg)

    def height(m):
        set_rot(lo, x=m)
        set_rot(ft, x=-(upper_deg + m))
        bpy.context.view_layer.update()
        return foot_tip(ft).z - target_z

    a, b = -20.0, 60.0                                       # slight hyperextension up to a deep fold
    sgn = FLEX_SIGN[kind]
    # flexing in this leg's direction raises the hoof, so height() rises with m*sgn
    lo_m, hi_m = (a, b) if sgn > 0 else (-b, -a)
    for _ in range(14):
        mid = (lo_m + hi_m) / 2
        h = height(mid)
        raising = h > 0
        if (raising and sgn > 0) or (not raising and sgn < 0):
            hi_m = mid
        else:
            lo_m = mid
    return (lo_m + hi_m) / 2


hips_rest = pb["Hips"].bone.matrix_local.to_3x3().inverted()
SLIDE = {k: CFG["slide"] * LEG_LENGTH for k in ("Front", "Hind")}   # how far (m) the top of a leg moves along the body, forward and back: the shoulder blade and the hip
upper_rest = {n: pb[n].bone.matrix_local.to_3x3().inverted() for n in pb.keys() if "Upper" in n}


def set_slide(kind, side, dy):
    """Move the top of the leg along the body by dy metres (+Y is towards the tail)."""
    name = f"{kind}Upper_{side}"
    pb[name].location = upper_rest[name] @ Vector((0, dy, 0))


def stance_direction(kind):
    """+1 if the planted hoof moves towards +Y as the upper leg swings from -A to +A (it should: the body walks towards -Y), else -1."""
    solve_lower(kind, "L", -10.0)
    y0 = foot_tip(f"{kind}Foot_L").y
    solve_lower(kind, "L", 10.0)
    return 1.0 if foot_tip(f"{kind}Foot_L").y > y0 else -1.0


def bump(t, centre, width):
    """A smooth pulse of height 1 at `centre` (cycle time) that wraps around the stride."""
    d = (t - centre + 0.5) % 1.0 - 0.5
    return math.exp(-(d * d) / (2 * width * width))


def set_body(t):
    """Everything except the legs, for cycle time t in [0, 1): body bob, sway, head nod, tail and ears."""
    w = 2 * math.pi * t
    if GAIT == "walk":
        pb["Hips"].location = hips_rest @ Vector((0, 0, -BODY_DROP + 0.013 * LEG_LENGTH * math.cos(2 * w)))
        set_rot("Hips", z=-2.0 * math.sin(w), y=1.2 * math.sin(w))
        set_rot("Spine", z=2.5 * math.sin(w), y=-1.0 * math.sin(w))
        set_rot("Chest", z=1.5 * math.sin(w - 0.4))
        set_rot("Neck1", x=2.0 * math.sin(w - 0.8))
        set_rot("Neck2", x=2.5 * math.sin(w - 1.4), z=1.5 * math.sin(w))
        set_rot("Head", x=-3.0 * math.sin(w - 1.4))
        set_rot("Ear_L", z=4.0 * math.sin(2 * w + 0.5))
        set_rot("Ear_R", z=-4.0 * math.sin(2 * w + 2.1))
        set_rot("Tail1", z=10.0 * math.sin(w - 1.0), x=2.0 * math.sin(2 * w))
        set_rot("Tail2", z=13.0 * math.sin(w - 1.8))
        set_rot("Tail3", z=15.0 * math.sin(w - 2.6))
    elif GAIT == "trot":
        # highest in the brief flights (t = 0.48, 0.98), lowest in mid stance; the diagonal pairs make the hips and shoulders roll against each other
        bob = 0.5 * math.cos(2 * w - 2 * math.pi * 0.98)
        pb["Hips"].location = hips_rest @ Vector((0, 0, -BODY_DROP + 0.034 * LEG_LENGTH * (bob - 0.5)))
        set_rot("Hips", z=-2.5 * math.sin(w), y=2.0 * math.sin(w), x=-1.5 * math.cos(2 * w))
        set_rot("Spine", z=3.0 * math.sin(w), y=-1.5 * math.sin(w), x=1.0 * math.cos(2 * w))
        set_rot("Chest", z=2.0 * math.sin(w - 0.4), x=-1.0 * math.cos(2 * w))
        set_rot("Neck1", x=3.0 * math.cos(2 * w - 0.8))
        set_rot("Neck2", x=3.5 * math.cos(2 * w - 1.4), z=1.5 * math.sin(w))
        set_rot("Head", x=-4.5 * math.cos(2 * w - 1.4))
        set_rot("Ear_L", z=6.0 * math.sin(2 * w + 0.5), x=5.0 * math.cos(2 * w))
        set_rot("Ear_R", z=-6.0 * math.sin(2 * w + 2.1), x=5.0 * math.cos(2 * w))
        set_rot("Tail1", z=8.0 * math.sin(w - 1.0), x=-10.0 + 2.0 * math.sin(2 * w))
        set_rot("Tail2", z=10.0 * math.sin(w - 1.8), x=-4.0)
        set_rot("Tail3", z=12.0 * math.sin(w - 2.6), x=-3.0)
    else:
        # gathered (back arched, legs under the body) in the long flight, t = 0.68-1.0, stretched (back hollow, reaching) in the short one, t = 0.30-0.40.
        # The back only bends while no foot is under load, so the planted hooves keep their line.
        gather = bump(t, 0.84, 0.09) - 0.55 * bump(t, 0.35, 0.04)
        bob = bump(t, 0.84, 0.12) + 0.8 * bump(t, 0.35, 0.06)
        pb["Hips"].location = hips_rest @ Vector((0, 0, -BODY_DROP + 0.06 * LEG_LENGTH * (bob - 0.2)))
        set_rot("Hips", x=RUN_SPINE["Hips"] * gather, z=-1.0 * math.sin(w))
        set_rot("Spine", x=RUN_SPINE["Spine"] * gather, z=1.5 * math.sin(w))
        set_rot("Chest", x=RUN_SPINE["Chest"] * gather, z=1.0 * math.sin(w - 0.4))
        set_rot("Neck1", x=-6.0 * gather + 2.0 * math.cos(w))
        set_rot("Neck2", x=-5.0 * gather)
        set_rot("Head", x=4.0 * gather)
        set_rot("Ear_L", z=10.0 * math.sin(w + 0.5), x=-14.0)
        set_rot("Ear_R", z=-10.0 * math.sin(w + 2.1), x=-14.0)
        set_rot("Tail1", z=6.0 * math.sin(w - 1.0), x=-14.0 + 6.0 * gather)
        set_rot("Tail2", z=8.0 * math.sin(w - 1.8), x=-8.0)
        set_rot("Tail3", z=10.0 * math.sin(w - 2.6), x=-6.0)


RUN_SPINE = globals().get("RUN_SPINE", {"Hips": -4.0, "Spine": 8.0, "Chest": 3.0})      # degrees of pitch at the gathered moment (the back arching; the stretch is the opposite)


def leg_angles(kind, side, p):
    """(upper, lower, foot, slide) for one leg at gait phase p in [0, 1); p = 0 is hoof strike. Angles in degrees, slide in metres."""
    A = SWING_ANGLE[kind]
    stance = STANCE[kind]
    d = leg_angles.direction[kind] * SLIDE[kind]
    if p < stance:
        x = p / stance
        dy = d * (2 * x - 1)
        set_slide(kind, side, dy)
        u = stance_upper(kind, side, x, dy)
        l = solve_lower(kind, side, u)
        return u, l, -(u + l), dy
    s = (p - stance) / (1 - stance)
    u_start, u_end = A, -A
    l_start = leg_angles._ends[(kind, side)][1]            # lower angle at lift-off
    l_end = leg_angles._ends[(kind, side)][0]              # lower angle at the next strike
    u = u_start + (u_end - u_start) * smooth(s)
    l = l_start + (l_end - l_start) * smooth(s) + FLEX_SIGN[kind] * FLEX[kind] * math.sin(math.pi * s) ** 1.2
    c = 1.0 - 0.45 * math.sin(math.pi * s)                  # let the hoof curl a little while it is lifted
    dy = d * (1 - 2 * smooth(s))                            # the top of the leg comes forward again
    return u, l, -(u + l) * c, dy


leg_angles.direction = {}


def stance_upper(kind, side, x, dy=0.0):
    """Upper-leg angle a fraction x of the way through the stance: linear in the angle for the walk, bent so the hoof moves evenly for the others."""
    A = SWING_ANGLE[kind]
    if not CFG["linear_stance"] or kind not in stance_upper.table:
        return -A + 2 * A * x
    ys, us = stance_upper.table[kind]                       # hoof y at upper-leg angles us (from -A to A), the top of the leg at rest
    d = leg_angles.direction[kind] * SLIDE[kind]
    y = (ys[0] - d) + ((ys[-1] + d) - (ys[0] - d)) * x - dy        # where the hoof should be, less where the top of the leg already is
    for i in range(len(ys) - 1):
        if (ys[i] - y) * (ys[i + 1] - y) <= 0 and ys[i] != ys[i + 1]:
            return us[i] + (us[i + 1] - us[i]) * (y - ys[i]) / (ys[i + 1] - ys[i])
    return -A + 2 * A * x


stance_upper.table = {}


def stance_travel(kind, A):
    """How far the planted hoof moves along Y between hoof strike and lift-off for a swing of +-A degrees."""
    o = OFFSET[f"{kind}Upper_L"]
    ft = f"{kind}Foot_L"
    d = leg_angles.direction[kind] * SLIDE[kind]
    set_body(o % 1.0)
    set_slide(kind, "L", -d)
    solve_lower(kind, "L", -A)
    y_strike = foot_tip(ft).y
    set_body((o + STANCE[kind]) % 1.0)
    set_slide(kind, "L", d)
    solve_lower(kind, "L", A)
    y_lift = foot_tip(ft).y
    set_slide(kind, "L", 0.0)
    return abs(y_lift - y_strike)


# The legs are different lengths, so pick each pair's swing angle so every planted hoof moves the same
# distance per stride (= the body's speed), otherwise the hooves slide on the ground. Each leg can only reach so
# far before the contact solver runs out of leg (travel jumps), so find that limit first and cap the stride to it.
reach = {}
for kind in ("Front", "Hind"):
    leg_angles.direction[kind] = stance_direction(kind)
for kind in ("Front", "Hind"):
    prev = stance_travel(kind, 2.0)
    best = (2.0, prev)
    for A in range(4, 40, 2):
        t = stance_travel(kind, float(A))
        if t - prev > 0.12 * LEG_LENGTH or t < prev - 1e-6:        # a jump or a reversal: the solver lost the ground
            break
        best, prev = (float(A), t), t
    reach[kind] = best
max_travel = 0.97 * min(t for _, t in reach.values())

if GAIT == "walk" and CFG["slide"] == 0.0:
    STRIDE_FRAMES = STRIDE_FRAMES or max(16, round(36 * (LEG_LENGTH / 0.92) ** 0.5))   # small animals step faster
    if STRIDE_LENGTH is None:
        STRIDE_LENGTH = round(0.57 * LEG_LENGTH, 3)         # 0.52 m for the cow (leg 0.92 m)
else:
    # the stride is as long as the legs reach, the speed is the target unless the cadence would pass what a body of this size can do
    if STRIDE_LENGTH is None:
        STRIDE_LENGTH = round(max_travel, 3)
    STRIDE_LENGTH = min(STRIDE_LENGTH, max_travel)
    mean_stance = (STANCE["Front"] + STANCE["Hind"]) / 2
    # the speeds are for the collie (legs 0.28 m); a smaller or larger dog goes slower or faster by the square root of its leg (Froude)
    speed = TARGET_SPEED or {"walk": 1.1, "trot": 3.0, "run": 7.0}[GAIT] * (LEG_LENGTH / 0.28) ** 0.5
    cadence = speed * mean_stance / STRIDE_LENGTH           # strides per second for the planted hoof to cover STRIDE_LENGTH while the body goes at `speed`
    cadence_limit = CFG["max_cadence"] * (0.28 / max(LEG_LENGTH, 0.1)) ** 0.5   # smaller legs can turn over faster (Froude: cadence ~ leg ** -0.5; the collie's leg is 0.28 m)
    if cadence > cadence_limit:
        print(f"{GAIT}: {speed:.2f} m/s would need {cadence:.2f} strides/s (limit {cadence_limit:.2f}): slowed to fit the legs")
        cadence = cadence_limit
    STRIDE_FRAMES = STRIDE_FRAMES or max(8, round(FPS / cadence))
    # with the frame count rounded, shorten the stride so the planted hoof's speed is exactly the target (or as close as the cap allows)
    STRIDE_LENGTH = min(STRIDE_LENGTH, speed * mean_stance * STRIDE_FRAMES / FPS)

stride = min(STRIDE_LENGTH, max_travel)
if stride < STRIDE_LENGTH:
    print(f"stride capped to {stride:.3f} m by leg reach {reach}")
STRIDE_LENGTH = stride
for kind in ("Front", "Hind"):
    t0 = stance_travel(kind, 0.0)
    if t0 > STRIDE_LENGTH:                                   # the slide alone already goes further than the stride: shorten it
        SLIDE[kind] *= STRIDE_LENGTH / t0 * 0.98
        t0 = stance_travel(kind, 0.0)
    lo, hi = 0.0, reach[kind][0]
    for _ in range(14):
        mid = (lo + hi) / 2
        if stance_travel(kind, mid) < STRIDE_LENGTH:
            lo = mid
        else:
            hi = mid
    SWING_ANGLE[kind] = (lo + hi) / 2
print("swing angles (deg):", {k: round(v, 1) for k, v in SWING_ANGLE.items()},
      "stance travel:", {k: round(stance_travel(k, SWING_ANGLE[k]), 3) for k in SWING_ANGLE})

if CFG["linear_stance"]:
    # tabulate the hoof's y against the upper-leg angle through the stance (the body at the middle of its bob), to bend the angle so y is linear in time
    for kind in ("Front", "Hind"):
        o = OFFSET[f"{kind}Upper_L"]
        A = SWING_ANGLE[kind]
        set_body((o + STANCE[kind] / 2) % 1.0)
        ys, us = [], []
        set_slide(kind, "L", 0.0)
        for i in range(25):
            u = -A + 2 * A * i / 24
            solve_lower(kind, "L", u)
            ys.append(foot_tip(f"{kind}Foot_L").y)
            us.append(u)
        if all(ys[i + 1] > ys[i] for i in range(24)) or all(ys[i + 1] < ys[i] for i in range(24)):
            stance_upper.table[kind] = (ys, us)
        else:
            print(f"{kind}: hoof y is not monotonic in the leg angle: linear angle used")

leg_angles._ends = {}
for kind in ("Front", "Hind"):
    for side in ("L", "R"):
        A = SWING_ANGLE[kind]
        o = OFFSET[f"{kind}Upper_{side}"]
        set_body(o % 1.0)
        strike = solve_lower(kind, side, -A)
        set_body((o + STANCE[kind]) % 1.0)
        liftoff = solve_lower(kind, side, A)
        leg_angles._ends[(kind, side)] = (strike, liftoff)
        set_rot(f"{kind}Upper_{side}", x=0)
        set_rot(f"{kind}Lower_{side}", x=0)
        set_rot(f"{kind}Foot_{side}", x=0)

# --- Keyframe the whole cycle -------------------------------------------------------------------------------
# Only this clip's action is replaced: the Blender file is shared with other work, so no other action is touched.
for stale in [a for a in bpy.data.actions if a.name == ACTION or a.name.startswith(ACTION + ".")]:
    bpy.data.actions.remove(stale)
rig.animation_data_create()
action = bpy.data.actions.new(ACTION)
rig.animation_data.action = action
bpy.context.scene.render.fps = FPS
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = STRIDE_FRAMES + 1

KEYED = ["Hips", "Spine", "Chest", "Neck1", "Neck2", "Head", "Ear_L", "Ear_R", "Tail1", "Tail2", "Tail3"] + \
        [f"{k}{p}_{s}" for k in ("Front", "Hind") for p in ("Upper", "Lower", "Foot") for s in ("L", "R")]
foot_log = {n: [] for n in ("FrontFoot_L", "FrontFoot_R", "HindFoot_L", "HindFoot_R")}
for frame in range(1, STRIDE_FRAMES + 2):
    t = ((frame - 1) % STRIDE_FRAMES) / STRIDE_FRAMES
    set_body(t)
    for kind in ("Front", "Hind"):
        for side in ("L", "R"):
            p = (t - OFFSET[f"{kind}Upper_{side}"]) % 1.0
            u, l, f, dy = leg_angles(kind, side, p)
            set_slide(kind, side, dy)
            set_rot(f"{kind}Upper_{side}", x=u)
            set_rot(f"{kind}Lower_{side}", x=l)
            set_rot(f"{kind}Foot_{side}", x=f)
    bpy.context.view_layer.update()
    for n in foot_log:
        tip = foot_tip(n)
        foot_log[n].append((tip.y, tip.z))
    for name in KEYED:
        b = pb[name]
        if name == "Hips" or (SLIDE["Front"] > 0 and "Upper" in name):
            b.keyframe_insert("location", frame=frame)
        b.keyframe_insert("rotation_euler", frame=frame)

# --- Report: ground contact and ground speed ---------------------------------------------------------------
print("hoof clearance (m) per foot: min z, max z during swing")
for n, pts in foot_log.items():
    zs = [z for _, z in pts]
    print(f"  {n}: min {min(zs):+.3f}  max {max(zs):.3f}")
stride_seconds = STRIDE_FRAMES / FPS
slide = {}
for n, pts in foot_log.items():                              # planted-hoof travel per stance = ground speed check
    kind = n.replace("Foot_L", "").replace("Foot_R", "")
    o = OFFSET[n.replace("Foot", "Upper")]
    stance = sorted(((((i / STRIDE_FRAMES) - o) % 1.0, i, y, z) for i, (y, z) in enumerate(pts[:-1]) if ((i / STRIDE_FRAMES) - o) % 1.0 < STANCE[kind]))
    travel = abs(stance[0][2] - stance[-1][2])
    print(f"  {n}: planted hoof moves {travel:.3f} m per stance = {travel / (STANCE[kind] * stride_seconds):.2f} m/s")
    # foot slide: the world position of the planted hoof if the body moves at the clip's ground speed (a line fitted to the hoof's y in the stance);
    # its drift from the straight line, and its height above the ground, in centimetres
    n_s = len(stance)
    xs = [ph * stride_seconds for ph, _, _, _ in stance]
    ys = [y for _, _, y, _ in stance]
    mx, my = sum(xs) / n_s, sum(ys) / n_s
    slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / max(1e-9, sum((x - mx) ** 2 for x in xs))
    height = max(abs(z) for _, _, _, z in stance) * 100.0
    slide[n] = [abs(slope), 0.0, height, xs, ys]
speed_measured = sum(v[0] for v in slide.values()) / 4          # the clip's ground speed: what the body moves at
for n, v in slide.items():                                       # a hoof is planted if it moves back at exactly that speed; its drift from such a line
    direction = 1.0 if sum(y1 - y0 for y0, y1 in zip(v[4][:-1], v[4][1:])) > 0 else -1.0
    dev = [y - direction * speed_measured * x for x, y in zip(v[3], v[4])]
    v[1] = (max(dev) - min(dev)) / 2 * 100.0
worst_drift = max(v[1] for v in slide.values())
worst_height = max(v[2] for v in slide.values())
print(f"{GAIT}: ground speed {speed_measured:.2f} m/s (feet {', '.join(f'{k.replace("Foot_", "")} {v[0]:.2f}' for k, v in slide.items())}); {STRIDE_FRAMES} frames at {FPS} fps"
      f" = {1 / stride_seconds:.2f} strides/s")
print(f"{GAIT}: foot slide: planted hoof drifts at most {worst_drift:.1f} cm from its line, {worst_height:.1f} cm off the ground"
      f" (leg {LEG_LENGTH * 100:.0f} cm; stride {STRIDE_LENGTH * 100:.0f} cm)")
if REPORT is not None:
    REPORT[ANIM_PREFIX + "@" + GAIT] = {"speed": round(speed_measured, 3), "drift_cm": round(worst_drift, 2), "height_cm": round(worst_height, 2),
                                           "frames": STRIDE_FRAMES, "fps": FPS, "stride_m": round(STRIDE_LENGTH, 3), "leg_m": round(LEG_LENGTH, 3)}

bpy.context.scene.frame_set(1)
if EXPORT:
    bpy.ops.object.mode_set(mode="OBJECT")
    out = common.export_anim_fbx(rig, f"Assets/Art/Global/Animals/Anims/{ANIM_PREFIX}@{GAIT.capitalize()}.fbx", only_active=True)
    print("exported", out)

if not KEEP:
    # leave the shared file as found: the rig back at rest, no leftover action on it, the scene settings and the selected object as they were
    quadruped_rig.rest_pose(rig)
    bpy.ops.object.mode_set(mode="OBJECT")
    rig.animation_data.action = None
    bpy.data.actions.remove(action)
    bpy.context.scene.render.fps, bpy.context.scene.frame_start, bpy.context.scene.frame_end = saved_scene[:3]
    bpy.context.scene.frame_set(saved_scene[3])
    if saved_active is not None:
        bpy.context.view_layer.objects.active = saved_active
