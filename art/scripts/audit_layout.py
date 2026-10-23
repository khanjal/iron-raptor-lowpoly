#!/usr/bin/env python3
"""Audit the generated Farmstead layout: is everything where it should be, the way round it should be, and not through anything else?

    python art/scripts/audit_layout.py [Logs/farmstead_layout.json] [--only floor,facing] [--list]

Plain Python 3 (no Blender, no Unity). The JSON comes from the editor method FarmsteadLayoutDump.Run (Assets/Editor/FarmsteadLayoutDump.cs):

    Unity.exe -batchmode -nographics -projectPath . -executeMethod FarmsteadLayoutDump.Run -logFile Logs/dump.log

It prints one line per problem ("FAIL <test> <where>: <what>") and exits 1 if there is any (0 and "layout audit: ok" if none). The skill `layout-audit`
(.claude/skills/layout-audit/SKILL.md) says what to do about each test. The tests are data driven: the tables below say which kinds must be unique, which
stand against a wall, which are hung on one, how many things a room should hold. Add a row when the owner finds a new kind of fault; do not loosen a number to
make a real problem go away.

All coordinates are the dump's: world metres, x east, z north, y up. Rectangles are [xMin, zMin, xMax, zMax]. A model faces +z at yaw 0 (the Blender models face
-Y and the importer turns them), and a yaw of 90 degrees faces +x.
"""

import argparse
import json
import math
import re
import sys
from collections import defaultdict
from pathlib import Path

DEFAULT_JSON = "Logs/farmstead_layout.json"
GEOMETRY_JSON = Path(__file__).resolve().parent.parent / "data" / "prop_geometry.json"   # written by audit_props.py (WRITE=True)

# =====================================================================================================================
# THE DATA: edit these tables, not the tests
# =====================================================================================================================

# --- Naming: "GH_Chair_Kitchen_01" -> "Chair_Kitchen". Tables below are keyed by this short name and matched as a regex against all of it.
STRIP_PREFIX = re.compile(r"^(G[A-Z]|F[A-Z])_")
STRIP_SUFFIX = re.compile(r"_(\d\d)$")

# --- Floating and sinking
SUPPORT_TOLERANCE = 0.03        # m: the bottom of a thing may be this far from what it stands on (the floor, a table top)
SUPPORT_COVER = 0.4             # a thing is supported when this fraction of its footprint is over tops at its height
SUNK_PATCH = 0.045             # m: animals and grey boxes may stand this far (the floor patch) below the floor line
PERSON_STANDING = (-0.05, 0.03)  # a standing person's root (their feet) relative to the floor: down to 5 cm sunk in the floor patch, 3 cm above it
PERSON_SITTING = (-0.05, 0.15)   # a seated person's root relative to the floor: their feet dangle at most 15 cm (a child on a tall chair), none more than the floor patch below it
# The Sit clip puts the Humanoid hip joint this high above the root. MEASURED (issue #146: the Animator posed in Unity batch mode, the Hips bone read back), not the old rule of thumb
# (0.42 / 0.33): the grandparent's joint is 0.544 m above the root, the kid's 0.42 m. A seated body rests on the seat when the joint is 0.00-0.12 m above its top (the thighs lie on the cushion;
# the pelvis hangs about 0.08 m below the joint); more than 0.15 m above it the body hovers, more than 0.03 m below it the thighs are sunk into the seat. "Below" is positive when the hips are under the seat top.
SIT_HIPS = {"Grandparent": 0.544, "FarmerKid": 0.42, "FarmerSpouse": 0.45, "FarmerKid2": 0.378, "FarmerKid3": 0.336}   # (the second and third child are 0.9 and 0.8 of the first: FarmsteadNpcs, issue #194)
SIT_HIPS_DEFAULT = 0.45
HIPS_BELOW_SEAT = (-0.15, 0.03)
# Kinds hung on a wall (their back is against it and they stand off the floor on purpose), or from the ceiling.
WALL_HUNG = r"^(Frame_|Poster|KidDrawing|Mirror_Wall|Clock_Wall|NewspaperClippings|TinfoilPane|CoatHooks|TowelRail|MedicineCabinet|Shelf_Wall|DeerTrophy|Curtains_|FuseBox|LightSwitch|Calendar|Board|Mirror|BulletinBoard|NeonSign|SecurityCamera|Intercom|HandLetteredSign|FirstAidKit|AirConditioner|JarShelf)"
CEILING_HUNG = r"^(CeilingShade|Chandelier|BareBulb|Fluorescent|HangingPlant)"
HANG_TOLERANCE = 0.04           # m: a wall-hung thing's back is within this of the wall; a ceiling-hung one's top within it of the ceiling
# Things that lie on the floor and do not count as furniture for sinking, clearance or overlaps.
FLAT_KINDS = r"^(Rug|Doormat)"
# Tools that lean or hang on a wall when they are raised off the floor (they are not wall-hung when they lie on the floor).
HANGABLE = r"^(Pitchfork|Rake|Shovel|Broom|Axe|Hoe)"
HANGABLE_RAISED = 0.10          # m: a tool this far off the floor is hung
CEILING_SLAB = 0.06             # m: a ceiling-hung thing's top may sink this far into the ceiling slab above the room

# --- Facing. Models face +z unless listed here: kind regex -> the local direction of the model's true front as a yaw offset in degrees
# (0 = +z as built, 180 = the model was built facing the other way). Found by audit_props.py's front test; empty when every model faces -Y in Blender.
KIND_FRONT_OFFSET = {}
# Kinds that stand with their back to a wall: when one is within BACK_WALL_NEAR of a wall, its front must point away from the wall (within FACING_TOLERANCE degrees).
BACK_TO_WALL = (r"^(Sofa|Bookcase|Cabinet|Desk_|Wardrobe|Dresser|Nightstand|Fridge|Stove|Counter_|Washer|Dryer|WoodStove|Bed_|Bench|Chest|Tub|Toilet|Shower|"
                r"Locker|Workbench|Sink_|WaterHeater|Boiler|Cooler|TV_|Armchair|RockingChair|Microwave|Toaster|CoffeeMachine)")
BACK_WALL_NEAR = 0.35           # m
FACING_TOLERANCE = 20.0         # degrees
SEATS = r"^(Chair_|Stool|Bench|Armchair|RockingChair|Sofa)"
SEAT_TARGETS = r"^(Table_Dining|Table_Coffee|Desk_|Workbench|TV_)"   # what a seat near one of these should face
SEAT_NEAR = 1.0                 # m: a seat this close to a target (bounds to bounds) faces it ...
SEAT_TOLERANCE = 55.0           # degrees ... within this
# Seats that stand at a table or desk but are built to face a screen or a person, so they are not judged against the table.
SEAT_FACING_EXEMPT = r"^(RockingChair|Armchair|Sofa|Bench)"

# --- Clearance
MIN_WALL_GAP = 0.10             # m: between flush (<= FLUSH) and this, a gap is a crack nothing fits in: the thing is almost touching the wall
FLUSH = 0.02                    # m: touching
STAIR_END_WALL = 0.30          # m: a wall may reach this far along a stair's run (it stands across its top or foot); more and the stair goes through it
# These defaults are overridden by the "rules" the dump writes (FarmsteadLayout.Rules in C# is the one place the numbers are set).
STAIR_CLEAR = 1.0               # m: nothing stands this far past the foot or the head of a stair
STAIR_FLUSH = 0.05              # m: a stair is flush with the wall it stands against within this
DOOR_APPROACH_NO_LEAF = 0.9     # m: nothing solid this far in front of an opening with no leaf
DOOR_APPROACH_LEAF_MARGIN = 0.05   # m: a door with a leaf keeps its width plus this clear in front of it
CELLAR_MIN_FILL = 0.88          # the cellar's rooms add up to at least this share of the footprint's area
CELLAR_COVER_TOLERANCE = 0.5    # m: a cellar's rooms cover the house's footprint to within this
STAIR_WALL_GAP = 0.60           # m: a stair is flush with its shaft wall or clear of any wall by this much
INSIDE_WALL = 0.03              # m: a thing this far into a wall is in it
WALL_CLEARANCE_EXEMPT = WALL_HUNG + "|" + CEILING_HUNG + "|" + FLAT_KINDS
# Pairs of kinds that may overlap in plan (kind regex, kind regex): a chair pushed under a table, a rug under everything.
OVERLAP_OK = [
    (r"^Chair_", r"^(Table_|Desk_|Workbench)"),
    (r"^(Stool|Bench)", r"^(Table_|Desk_|Workbench)"),
    (r"^Bench", r"^Bench"),
    (r"^(HayBale|Crate|FeedSack)", r"^(HayBale|Crate|FeedSack)"),   # stacked
    (r"^(Curtains_)", r".*"),
    (r"^(Frame_|Poster|KidDrawing|Mirror_Wall|Clock_Wall|NewspaperClippings|TinfoilPane|Shelf_Wall|CoatHooks|TowelRail|MedicineCabinet|DeerTrophy|FuseBox)", r".*"),   # hung: judged by the wall tests
]
OVERLAP_MIN = 0.02              # m: the boxes must overlap by more than this in all three axes to count

# --- Uniqueness and pairs (per building)
UNIQUE_PER_BUILDING = ["Washer", "Dryer", "Fridge", "Stove", "WaterHeater", "Boiler", "Tub", "Shower", "Toilet", "Microwave", "Toaster", "CoffeeMachine", "WoodStove", "FuseBox", "TV_CRT", "Tractor"]
# A washer needs a dryer within 1.2 m beside it, a dryer needs a washer: (kind, partner, max gap in m)
PAIRS = [("Washer", "Dryer", 1.2), ("Dryer", "Washer", 1.2)]
# Pairs may be split across floors on purpose: no.

# --- Connected parts: a part that must run into a wall, the ceiling or the floor (a pipe, a cable, a duct). Kind -> list of
# (name, local end point in Blender model coordinates [x right, y back, z up, front -Y], what it must reach: any of "wall", "ceiling", "floor").
# The numbers come from the model's script (art/scripts/household.py): the water heater's and the boiler's pipes run up and back into a plate on the wall, so they have no free end to list (audit_props.py checks that they have none). audit_props.py checks this table
# against the model (every free pipe end of a model is listed here, and every listed end is on the model).
CONNECTED = {
    "GL_BareBulb_01": [
        ("cord top", (0.0, 0.0, 1.20), ("ceiling",)),
    ],

}
CONNECT_TOLERANCE = 0.03

# --- Rooms: the fewest things (not hung, not flat) a room should hold, by room name (any building); a room not listed has no target
ROOM_ITEM_TARGET = {
    "Kitchen": 10, "Dining": 8, "Mudroom": 6, "StairHall": 3, "Hall": 3, "Living": 10,
    "FarmerRoom": 8, "Bath": 6, "KidRoom": 8, "UpperStairs": 2, "Landing": 5, "Cellar": 12,
    "Workshop": 10, "TackRoom": 5, "Outhouse": 1, "CellarWorkshop": 12, "CellarPantry": 10, "CellarStore": 12,
}
ROOM_MIN_NAV_FRACTION = 0.15    # a room whose NavMesh is under this fraction of its floor is a closed box
ROOM_NAV_EXEMPT = {"Outhouse"}  # a hiding place a player stands in; the agent radius leaves no NavMesh in 2 x 2 m

# --- Twins: two things this close (centres, m) and the same kind
TWIN_DISTANCE = 0.03

# --- Variety: kinds that should not be all the same model when there are several in a building: (kind regex, the most identical copies allowed in one building)
VARIETY = [
    (r"^Bookcase", 2),
    (r"^(Frame_Landscape|Frame_Portrait)", 3),
    (r"^KidDrawing", 2),
    (r"^Shelf_Wall", 6),
    (r"^Locker", 6),
]

# --- Doors
DOOR_HINGE_TOLERANCE = 0.06     # m: the hinge is on an end of its opening
DOOR_ARC_STEP = 10.0            # degrees between samples of the swing
DOOR_SWING_CLEAR_HEIGHT = 2.0   # m: items below this above the door's base can be hit by the leaf


# =====================================================================================================================
# Helpers
# =====================================================================================================================

def short(kind):
    """GH_Chair_Kitchen_01 -> Chair_Kitchen; names that are not models stay as they are."""
    k = STRIP_PREFIX.sub("", kind, count=1) if re.match(r"^[A-Z]{2}_", kind) else kind
    return STRIP_SUFFIX.sub("", k)


def match(pattern, text):
    return re.search(pattern, text) is not None


class Item:
    """One placed thing from the dump, with the numbers the tests use."""

    def __init__(self, raw, index):
        self.raw = raw
        self.index = index
        self.name = raw["name"]
        self.kind = raw["kind"]
        self.s = short(self.kind)
        self.category = raw["category"]
        self.building = raw.get("building", "")
        self.floor = raw.get("floor", "")
        self.room = raw.get("room", "")
        self.pos = raw["pos"]
        self.yaw = raw["yaw"]
        self.scale = raw.get("scale", [1, 1, 1])
        self.floor_y = raw.get("floorY", 0.0)
        self.state = raw.get("state", "")
        box = raw.get("rend") or raw.get("coll")
        self.has_box = box is not None
        if box:
            self.lo, self.hi = box["min"], box["max"]
        else:
            self.lo = self.hi = self.pos
        self.hidden = raw.get("hidden", False)
        self.hung = match(WALL_HUNG, self.s) or (match(HANGABLE, self.s) and self.lo[1] > self.floor_y + HANGABLE_RAISED)
        self.ceiling = match(CEILING_HUNG, self.s)
        self.flat = match(FLAT_KINDS, self.s)

    @property
    def rect(self):
        return (self.lo[0], self.lo[2], self.hi[0], self.hi[2])

    @property
    def centre(self):
        return ((self.lo[0] + self.hi[0]) / 2, (self.lo[2] + self.hi[2]) / 2)

    @property
    def bottom(self):
        return self.lo[1]

    @property
    def top(self):
        return self.hi[1]

    @property
    def is_model(self):
        return re.search(r"_\d\d$", self.kind) is not None

    def surfaces(self, geometry):
        """World heights of the tops other things can stand on: the exposed horizontal tops of the model (from prop_geometry.json), else the top of its bounds."""
        g = geometry.get(self.kind)
        if not g or not g.get("surfaces"):
            return [self.top]
        k = self.scale[1] if self.scale else 1.0
        return [self.bottom + (z - g.get("zmin", 0.0)) * k for z in g["surfaces"]]

    def front(self):
        """The unit vector (x, z) the item's front points along."""
        offset = 0.0
        for pat, off in KIND_FRONT_OFFSET.items():
            if match(pat, self.s) or match(pat, self.kind):
                offset = off
        a = math.radians(self.yaw + offset)
        return (math.sin(a), math.cos(a))

    def where(self):
        place = "/".join(p for p in (self.building, self.floor, self.room) if p) or "outdoors"
        return f"{place}: {self.name} [{self.kind}] at ({self.pos[0]:.2f}, {self.pos[2]:.2f})"


def rect_gap(a, b):
    """Distance between two rectangles (0 if they touch or overlap)."""
    dx = max(a[0] - b[2], b[0] - a[2], 0.0)
    dz = max(a[1] - b[3], b[1] - a[3], 0.0)
    return math.hypot(dx, dz)


def rect_overlap(a, b):
    """The overlap in x and z (negative: apart by that much)."""
    return min(a[2], b[2]) - max(a[0], b[0]), min(a[3], b[3]) - max(a[1], b[1])


def contains(rect, x, z, margin=0.0):
    return rect[0] - margin <= x <= rect[2] + margin and rect[1] - margin <= z <= rect[3] + margin


def angle_between(u, v):
    dot = max(-1.0, min(1.0, u[0] * v[0] + u[1] * v[1]))
    return math.degrees(math.acos(dot))


def compass(v):
    if abs(v[0]) > abs(v[1]):
        return "east (+x)" if v[0] > 0 else "west (-x)"
    return "north (+z)" if v[1] > 0 else "south (-z)"


class Wall:
    """A wall piece: a rectangle in plan (the segment grown by half its thickness), a height range, and the doorways removed."""

    def __init__(self, building, floor, raw):
        self.building, self.floor = building, floor
        self.raw = raw
        self.a, self.b = raw["a"], raw["b"]
        self.t = raw["thickness"]
        self.y0, self.y1 = raw["y0"], raw["y1"]
        self.exterior = raw["exterior"]
        self.openings = raw["openings"]
        self.along_x = abs(self.b[0] - self.a[0]) >= abs(self.b[1] - self.a[1])
        self.pieces = self._pieces()

    def rect_of(self, s0, s1):
        ax, az, bx, bz = self.a[0], self.a[1], self.b[0], self.b[1]
        length = math.hypot(bx - ax, bz - az)
        ux, uz = ((bx - ax) / length, (bz - az) / length) if length else (1.0, 0.0)
        p0 = (ax + ux * s0, az + uz * s0)
        p1 = (ax + ux * s1, az + uz * s1)
        h = self.t / 2
        return (min(p0[0], p1[0]) - (0 if self.along_x else h), min(p0[1], p1[1]) - (h if self.along_x else 0),
                max(p0[0], p1[0]) + (0 if self.along_x else h), max(p0[1], p1[1]) + (h if self.along_x else 0))

    def _pieces(self):
        """Rectangles of wall, with the doors and archways (openings that reach the floor) cut out."""
        length = math.hypot(self.b[0] - self.a[0], self.b[1] - self.a[1])
        cuts = []
        for o in self.openings:
            if o["sill"] > 0.1 or o["kind"] == "Window":
                continue
            s0 = math.hypot(o["a"][0] - self.a[0], o["a"][1] - self.a[1])
            s1 = math.hypot(o["b"][0] - self.a[0], o["b"][1] - self.a[1])
            cuts.append((min(s0, s1), max(s0, s1)))
        cuts.sort()
        pieces, cursor = [], 0.0
        for c0, c1 in cuts:
            if c0 > cursor + 0.01:
                pieces.append(self.rect_of(cursor, c0))
            cursor = max(cursor, c1)
        if length > cursor + 0.01:
            pieces.append(self.rect_of(cursor, length))
        return pieces

    def overlaps_y(self, lo, hi, need=0.05):
        return min(hi, self.y1) - max(lo, self.y0) > need


def apply_rules(rules):
    """The clearance rules live in FarmsteadLayout.Rules (C#), as data; the dump writes them under "rules" and the audit uses those numbers over its defaults."""
    global STAIR_CLEAR, STAIR_WALL_GAP, STAIR_FLUSH, DOOR_APPROACH_NO_LEAF, DOOR_APPROACH_LEAF_MARGIN, CELLAR_COVER_TOLERANCE, CELLAR_MIN_FILL
    STAIR_CLEAR = rules.get("stairClear", STAIR_CLEAR)
    STAIR_WALL_GAP = rules.get("stairWallGap", STAIR_WALL_GAP)
    STAIR_FLUSH = rules.get("stairFlush", STAIR_FLUSH)
    DOOR_APPROACH_NO_LEAF = rules.get("doorApproachNoLeaf", DOOR_APPROACH_NO_LEAF)
    DOOR_APPROACH_LEAF_MARGIN = rules.get("doorApproachLeafMargin", DOOR_APPROACH_LEAF_MARGIN)
    CELLAR_COVER_TOLERANCE = rules.get("cellarCoverTolerance", CELLAR_COVER_TOLERANCE)
    CELLAR_MIN_FILL = rules.get("cellarMinFill", CELLAR_MIN_FILL)


class Layout:
    def __init__(self, data):
        self.data = data
        apply_rules(data.get("rules", {}))
        self.items = [Item(r, i) for i, r in enumerate(data["items"])]
        self.buildings = {b["name"]: b for b in data["buildings"]}
        self.walls = defaultdict(list)       # building -> [Wall]
        self.rooms = []                       # (building, floor dict, room dict)
        self.stairs = []                      # (building, floor dict, stair dict)
        for b in data["buildings"]:
            for f in b["floors"]:
                for w in f["walls"]:
                    self.walls[b["name"]].append(Wall(b["name"], f["name"], w))
                for r in f["rooms"]:
                    self.rooms.append((b["name"], f, r))
                for s in f["stairs"]:
                    self.stairs.append((b["name"], f, s))
        self.doors = data.get("doors", [])
        self.geometry = {}
        if GEOMETRY_JSON.exists():
            self.geometry = json.loads(GEOMETRY_JSON.read_text(encoding="utf-8")).get("props", {})

    def indoor(self):
        return [i for i in self.items if i.building and i.has_box and not i.hidden]

    def floor_of(self, building, name):
        for f in self.buildings[building]["floors"]:
            if f["name"] == name:
                return f
        return None


# =====================================================================================================================
# THE TESTS: each returns a list of (where, message)
# =====================================================================================================================

def test_floor(L):
    """Floor penetration and floating: the lowest point of a thing is on its floor or on the top of what it stands on (within 3 cm)."""
    out = []
    indoors = [i for i in L.indoor() if not i.hidden]
    for it in L.items:
        if it.category == "person":
            if it.building:   # no state (the farmer, who walks) is standing
                lo, hi = PERSON_SITTING if it.state == "Sit" else PERSON_STANDING
                if it.state == "Sit":   # a smaller child's feet dangle further: the hips are higher above the root the taller the body, so a body with lower hips is lifted more onto the same seat
                    hi += max(0.0, SIT_HIPS_DEFAULT - SIT_HIPS.get(re.sub(r"^NPC_", "", short(it.kind)), SIT_HIPS_DEFAULT))
                d = it.pos[1] - it.floor_y
                if d < lo:
                    out.append((it.where(), f"{abs(d) * 100:.0f} cm below the floor: their root is at y {it.pos[1]:.3f}, the floor {it.floor_y:.3f}" + (" (seated)" if it.state == "Sit" else "")))
                elif d > hi:
                    out.append((it.where(), f"floats {d * 100:.0f} cm above the floor: their root is at y {it.pos[1]:.3f}, the floor {it.floor_y:.3f}" + (f", seated, feet may dangle {hi * 100:.0f} cm" if it.state == "Sit" else "")))
            if it.building and it.state == "Sit":
                hips = it.pos[1] + SIT_HIPS.get(re.sub(r"^NPC_", "", short(it.kind)), SIT_HIPS_DEFAULT)   # the people are NPC_<Name> since the bystanders became networked humans
                seats = []
                for o in L.indoor():
                    if o.building == it.building and o.floor == it.floor and o.category == "prop" and match(SEATS, o.s) and contains(o.rect, it.pos[0], it.pos[2], 0.05):
                        seats += [(y, o) for y in o.surfaces(L.geometry) if hips + HIPS_BELOW_SEAT[0] <= y <= hips + 0.6]
                if not seats:
                    out.append((it.where(), f"sits on nothing: their hips are at y {hips:.2f} and there is no seat under them"))
                else:
                    y, o = min(seats, key=lambda t: t[0])
                    below = y - hips
                    if below < HIPS_BELOW_SEAT[0]:
                        out.append((it.where(), f"sits too high on {o.name}: their hip joint is {below * 100:.0f} cm under its seat top (y {y:.2f}), it should be {-HIPS_BELOW_SEAT[0] * 100:.0f} cm above to {HIPS_BELOW_SEAT[1] * 100:.0f} cm under it"))
                    elif below > HIPS_BELOW_SEAT[1]:
                        out.append((it.where(), f"is sunk into {o.name}: their hip joint is {below * 100:.0f} cm under its seat top (y {y:.2f}), it should be {-HIPS_BELOW_SEAT[0] * 100:.0f} cm above to {HIPS_BELOW_SEAT[1] * 100:.0f} cm under it"))
            continue
        if it.category not in ("prop", "animal") or not it.building or not it.has_box or it.hidden or it.hung or it.ceiling or it.flat:
            continue
        bottom = it.pos[1] if it.category == "animal" else it.bottom   # an animal's skinned bounds are padded: judge its root
        # a grey box (no model) or an animal stands on the room's floor line, 4 cm under the coloured floor patch: the patch is a decal
        slack = SUNK_PATCH if (it.category == "animal" or not it.is_model) else SUPPORT_TOLERANCE
        if it.floor_y - slack > bottom > it.floor_y - 0.5:
            out.append((it.where(), f"{(it.floor_y - bottom) * 100:.0f} cm below the floor (bottom y {bottom:.3f}, floor {it.floor_y:.3f})"))
            continue
        if it.category == "animal":
            if bottom > it.floor_y + SUPPORT_TOLERANCE + 1e-3:
                out.append((it.where(), f"floats {(bottom - it.floor_y) * 100:.0f} cm above the floor (root y {bottom:.3f}, floor {it.floor_y:.3f})"))
            continue
        cx, cz = it.centre
        area = max((it.rect[2] - it.rect[0]) * (it.rect[3] - it.rect[1]), 1e-6)
        eps = 1e-3
        if abs(bottom - it.floor_y) <= SUPPORT_TOLERANCE + eps or (not it.is_model and it.floor_y - SUNK_PATCH <= bottom <= it.floor_y + SUPPORT_TOLERANCE):
            continue
        under, matching = [it.floor_y], []
        for other in indoors:
            if other is it or other.category != "prop" or other.building != it.building or other.floor != it.floor or other.flat or other.ceiling:
                continue
            ys = [y for y in other.surfaces(L.geometry) if bottom - 0.6 <= y <= bottom + 0.6]
            if not ys:
                continue
            ox, oz = rect_overlap(it.rect, other.rect)
            frac = max(ox, 0.0) * max(oz, 0.0) / area
            if contains(other.rect, cx, cz, 0.02):
                under += ys
            if rect_gap(it.rect, other.rect) > 0.5:
                continue
            for y in ys:
                if abs(bottom - y) <= SUPPORT_TOLERANCE + eps:
                    matching.append((frac, other))
        if sum(f for f, _o in matching) >= SUPPORT_COVER:
            continue                                  # enough of its footprint is on tops at its height (a crate across two crates)
        nearest = min(under, key=lambda t: abs(bottom - t))
        d = bottom - nearest
        if matching:
            frac, other = max(matching, key=lambda m: m[0])
            out.append((it.where(), f"is off its support: its height matches the top of {other.name} [{other.kind}] at ({other.pos[0]:.2f}, {other.pos[2]:.2f}) but only {frac * 100:.0f}% of "
                                    f"its footprint is over it (its centre is {max(max(other.rect[0] - cx, cx - other.rect[2]), max(other.rect[1] - cz, cz - other.rect[3]), 0.0) * 100:.0f} cm outside), nothing else is under it"))
        elif d > 0:
            what = "the floor" if nearest == it.floor_y else "the thing under it"
            out.append((it.where(), f"floats {d * 100:.0f} cm above {what} (bottom y {bottom:.3f}, nearest support top {nearest:.3f})"))
        else:
            out.append((it.where(), f"sunk {-d * 100:.0f} cm into what it stands on (bottom y {bottom:.3f}, support top {nearest:.3f})"))
    return out


def test_hung(L):
    """Things hung on a wall touch it; things hung from the ceiling reach it."""
    out = []
    for it in L.indoor():
        if it.category != "prop" or not (it.hung or it.ceiling):
            continue
        if it.ceiling:
            f = L.floor_of(it.building, it.floor)
            if f is not None and not (f["ceiling"] - HANG_TOLERANCE <= it.top <= f["ceiling"] + CEILING_SLAB) and not match(r"^BareBulb", it.s):
                out.append((it.where(), f"hangs from nothing: its top is y {it.top:.3f}, the ceiling {f['ceiling']:.3f} ({(f['ceiling'] - it.top) * 100:.0f} cm apart)"))
            continue
        best = None
        for w in L.walls[it.building]:
            if not w.overlaps_y(it.bottom, it.top, 0.0) or w.floor != it.floor:
                continue
            for piece in w.pieces:
                g = rect_gap(it.rect, piece)
                if best is None or g < best:
                    best = g
        if best is not None and best > HANG_TOLERANCE:
            out.append((it.where(), f"hangs in the room, {best * 100:.0f} cm from the nearest wall"))
    return out


def nearest_wall(L, it, near):
    """Walls within `near` of the item's footprint on its floor: [(gap, wall rect, normal pointing from the wall into the room as (x, z))]."""
    found = []
    for w in L.walls[it.building]:
        if w.floor != it.floor or not w.overlaps_y(it.bottom, it.top):
            continue
        for piece in w.pieces:
            ox, oz = rect_overlap(it.rect, piece)
            gx = it.rect[0] - piece[2]   # item right of the wall
            gx2 = piece[0] - it.rect[2]  # item left of the wall
            gz = it.rect[1] - piece[3]
            gz2 = piece[1] - it.rect[3]
            if oz > 0.05:               # beside the wall along x
                if 0 <= gx <= near:
                    found.append((gx, piece, (1.0, 0.0)))
                if 0 <= gx2 <= near:
                    found.append((gx2, piece, (-1.0, 0.0)))
            if ox > 0.05:
                if 0 <= gz <= near:
                    found.append((gz, piece, (0.0, 1.0)))
                if 0 <= gz2 <= near:
                    found.append((gz2, piece, (0.0, -1.0)))
    return sorted(found, key=lambda f: f[0])


def test_facing(L):
    """Facing: back-to-wall kinds face away from the wall they stand against; seats near a table or TV face it."""
    out = []
    for it in L.indoor():
        if it.category != "prop" or it.hung or it.ceiling or it.flat:
            continue
        front = it.front()
        if match(BACK_TO_WALL, it.s):
            walls = nearest_wall(L, it, BACK_WALL_NEAR)
            if walls:
                ok = any(angle_between(front, n) <= FACING_TOLERANCE for gap, piece, n in walls[:2])
                if not ok:
                    gap, piece, n = walls[0]
                    out.append((it.where(), f"stands {gap * 100:.0f} cm from the {compass((-n[0], -n[1]))} wall but its front points {compass(front)}: "
                                            f"{angle_between(front, n):.0f} degrees off pointing away from it"))
        # moving parts (doors and drawers the importer split off) are on the side the front points to
        for part in it.raw.get("parts", []):
            if not match(r"^(Door|Drawer)", part["name"]):
                continue
            pc = ((part["rend"]["min"][0] + part["rend"]["max"][0]) / 2, (part["rend"]["min"][2] + part["rend"]["max"][2]) / 2)
            ahead = (pc[0] - it.pos[0]) * front[0] + (pc[1] - it.pos[2]) * front[1]
            if ahead < -0.02:
                out.append((it.where(), f"its {part['name']} is on the {compass((-front[0], -front[1]))} side but the item faces {compass(front)}: the front is the wrong way round"))
        if match(SEATS, it.s) and not match(SEAT_FACING_EXEMPT, it.s):
            best, best_gap = None, SEAT_NEAR
            for other in L.indoor():
                if other is it or other.building != it.building or other.floor != it.floor or not match(SEAT_TARGETS, other.s):
                    continue
                g = rect_gap(it.rect, other.rect)
                if g <= best_gap:
                    best, best_gap = other, g
            if best is not None:
                cx, cz = it.centre
                tx, tz = best.centre
                to = (tx - cx, tz - cz)
                n = math.hypot(*to) or 1.0
                a = angle_between(front, (to[0] / n, to[1] / n))
                if a > SEAT_TOLERANCE:
                    out.append((it.where(), f"is {best_gap * 100:.0f} cm from {best.name} but faces {compass(front)}, {a:.0f} degrees off it"))
        if match(r"^(Sofa|Armchair)", it.s):
            tvs = [o for o in L.indoor() if o.building == it.building and o.floor == it.floor and match(r"^TV_", o.s) and o.room == it.room]
            if tvs:
                cx, cz = it.centre
                tv = min(tvs, key=lambda o: math.hypot(o.centre[0] - cx, o.centre[1] - cz))
                to = (tv.centre[0] - cx, tv.centre[1] - cz)
                n = math.hypot(*to) or 1.0
                a = angle_between(front, (to[0] / n, to[1] / n))
                if a > 70.0 and match(r"^Sofa", it.s):
                    out.append((it.where(), f"faces {compass(front)}, {a:.0f} degrees off the TV {tv.name}"))
    return out


def test_clearance(L):
    """Clearance: between flush (2 cm) and 10 cm from a wall is a crack; inside a wall is a fault; boxes of different things do not overlap; stairs keep 60 cm off walls."""
    out = []
    for it in L.indoor():
        if it.category != "prop" or match(WALL_CLEARANCE_EXEMPT, it.s):
            continue
        for w in L.walls[it.building]:
            if w.floor != it.floor or not w.overlaps_y(it.bottom, it.top, 0.1):
                continue
            for piece in w.pieces:
                ox, oz = rect_overlap(it.rect, piece)
                if ox > INSIDE_WALL and oz > INSIDE_WALL:
                    out.append((it.where(), f"is {min(ox, oz) * 100:.0f} cm inside a wall ({w.raw['a'][0]:.1f},{w.raw['a'][1]:.1f})-({w.raw['b'][0]:.1f},{w.raw['b'][1]:.1f})"))
    for it in L.indoor():
        if it.category != "prop" or match(WALL_CLEARANCE_EXEMPT, it.s):
            continue
        for gap, piece, n in nearest_wall(L, it, MIN_WALL_GAP)[:1]:
            if FLUSH < gap < MIN_WALL_GAP and it.bottom - it.floor_y < 0.2:
                out.append((it.where(), f"stands {gap * 100:.0f} cm from the wall to the {compass((-n[0], -n[1]))}: flush (under {FLUSH * 100:.0f} cm) or at least {MIN_WALL_GAP * 100:.0f} cm"))
    # boxes through each other
    things = [i for i in L.indoor() if i.category in ("prop", "person", "animal") and not i.flat and not i.hung and not i.ceiling]
    for ai, a in enumerate(things):
        for b in things[ai + 1:]:
            if a.building != b.building or a.floor != b.floor:
                continue
            ox, oz = rect_overlap(a.rect, b.rect)
            oy = min(a.top, b.top) - max(a.bottom, b.bottom)
            if ox <= OVERLAP_MIN or oz <= OVERLAP_MIN or oy <= OVERLAP_MIN:
                continue
            # one stands on the other: the top of one is the bottom of the other
            if any(abs(a.bottom - y) <= SUPPORT_TOLERANCE + 1e-3 for y in b.surfaces(L.geometry)) or any(abs(b.bottom - y) <= SUPPORT_TOLERANCE + 1e-3 for y in a.surfaces(L.geometry)):
                continue                                  # one stands on a top of the other
            if (a.category == "person" and match(SEATS, b.s)) or (b.category == "person" and match(SEATS, a.s)):
                continue                                  # sitting is the point
            if any((match(p, a.s) and match(q, b.s)) or (match(p, b.s) and match(q, a.s)) for p, q in OVERLAP_OK):
                continue
            if a.s == b.s and a.name.startswith(("Bale", "StallHay")):
                continue
            out.append((a.where(), f"overlaps {b.name} [{b.kind}] at ({b.pos[0]:.2f}, {b.pos[2]:.2f}) by {ox * 100:.0f} x {oz * 100:.0f} x {oy * 100:.0f} cm"))
    # stairs
    for building, f, s in L.stairs:
        rect = tuple(s["rect"])
        for w in L.walls[building]:
            if not w.overlaps_y(s["y0"], s["y1"], 0.5):
                continue
            for piece in w.pieces:
                g = rect_gap(rect, piece)
                ox, oz = rect_overlap(rect, piece)
                if ox > 0.02 and oz > 0.02:
                    along = oz if abs(s["dir"][1]) > abs(s["dir"][0]) else ox     # how far the wall reaches along the run
                    if along > STAIR_END_WALL:
                        out.append((f"{building}/{f['name']}: stair at ({s['start'][0]:.2f}, {s['start'][1]:.2f}) rising to y {s['y1']:.1f}",
                                    f"runs {along * 100:.0f} cm into a wall ({w.raw['a'][0]:.1f},{w.raw['a'][1]:.1f})-({w.raw['b'][0]:.1f},{w.raw['b'][1]:.1f})"))
                    continue   # a wall across the stair's end: only the side gap matters
                if (ox > 0.05 or oz > 0.05) and STAIR_FLUSH < g < STAIR_WALL_GAP:
                    out.append((f"{building}/{f['name']}: stair at ({s['start'][0]:.2f}, {s['start'][1]:.2f}) rising to y {s['y1']:.1f}",
                                f"is {g * 100:.0f} cm from a wall ({w.raw['a'][0]:.1f},{w.raw['a'][1]:.1f})-({w.raw['b'][0]:.1f},{w.raw['b'][1]:.1f}): "
                                f"flush or at least {STAIR_WALL_GAP * 100:.0f} cm (a player's shoulders)"))
    # the foot and the head of a stair are clear: nothing that stands on the floor within STAIR_CLEAR of either end (the foot on the stair's own floor, the head on the floor it arrives on)
    for building, f, s in L.stairs:
        dx, dz = s["dir"]
        n = math.hypot(dx, dz) or 1.0
        dx, dz = dx / n, dz / n
        ax, az = -dz, dx
        half = s["width"] / 2 - 0.02
        run = s["run"] * s["steps"]
        start = s["start"]
        end = (start[0] + dx * run, start[1] + dz * run)
        for what, base, step, elevation in (("foot", start, -STAIR_CLEAR, f["elevation"]), ("head", end, STAIR_CLEAR, s["y1"])):
            xs = [base[0] + ax * half, base[0] - ax * half, base[0] + ax * half + dx * step, base[0] - ax * half + dx * step]
            zs = [base[1] + az * half, base[1] - az * half, base[1] + az * half + dz * step, base[1] - az * half + dz * step]
            zone = (min(xs), min(zs), max(xs), max(zs))
            for it in L.items:
                if it.building != building or it.category not in ("prop", "person") or not it.has_box or it.hidden or it.hung or it.ceiling or it.flat:
                    continue
                its_floor = L.floor_of(building, it.floor)
                if its_floor is None or abs(its_floor["elevation"] - elevation) > 0.2 or it.top <= elevation + 0.1:
                    continue
                ox, oz = rect_overlap(zone, it.rect)
                if ox > 0.03 and oz > 0.03:
                    out.append((it.where(), f"stands at the {what} of the stair at ({start[0]:.2f}, {start[1]:.2f}) rising to y {s['y1']:.1f}: keep {STAIR_CLEAR:.1f} m clear"))
    return out


def test_unique(L):
    """Kinds that appear once per building do; a washer has a dryer beside it."""
    out = []
    by = defaultdict(list)
    for it in L.items:
        if it.building:
            by[(it.building, it.s)].append(it)
    for (building, s), items in sorted(by.items()):
        for pat in UNIQUE_PER_BUILDING:
            if match("^" + pat, s) and len(items) > 1:
                where = ", ".join(f"{i.floor}/{i.room} ({i.pos[0]:.1f}, {i.pos[2]:.1f})" for i in items)
                out.append((f"{building}", f"{len(items)} x {items[0].kind} where there is one per house: {where}"))
    for kind, partner, gap in PAIRS:
        for building in {i.building for i in L.items if i.building}:
            mine = [i for i in L.items if i.building == building and match("^" + kind, i.s)]
            theirs = [i for i in L.items if i.building == building and match("^" + partner, i.s)]
            for it in mine:
                near = [o for o in theirs if o.floor == it.floor and rect_gap(it.rect, o.rect) <= gap]
                if not near:
                    out.append((it.where(), f"has no {partner} within {gap} m beside it" + ("" if theirs else f" (there is no {partner} in the {building} at all)")))
    return out


def world_point(it, local):
    """A point in the model's Blender coordinates (x right, y back, z up, front -Y) to the world. The importer maps (x, y, z) to Unity (-x, z, -y)."""
    ux, uy, uz = -local[0], local[2], -local[1]
    s = it.scale
    ux, uy, uz = ux * s[0], uy * s[1], uz * s[2]
    a = math.radians(it.yaw)
    c, sn = math.cos(a), math.sin(a)
    # Unity rotates about +y by yaw: x' = x cos + z sin, z' = -x sin + z cos
    return (it.pos[0] + ux * c + uz * sn, it.pos[1] + uy, it.pos[2] - ux * sn + uz * c)


def test_connected(L):
    """Connections: a pipe, cable or duct end that is meant to go into a wall, the ceiling or the floor does."""
    out = []
    for it in L.indoor():
        ends = None
        for kind, e in CONNECTED.items():
            if it.kind == kind:
                ends = e
        if not ends:
            continue
        f = L.floor_of(it.building, it.floor)
        for name, local, targets in ends:
            p = world_point(it, local)
            best = {"ceiling": max(f["ceiling"] - p[1], 0.0) if f else 9.9,   # an end above the ceiling is in the roof or the slab: that is reached, not in the air
                     "floor": abs(p[1] - it.floor_y)}
            wall_gap = 9.9
            for w in L.walls[it.building]:
                if w.floor != it.floor or not (w.y0 - CONNECT_TOLERANCE <= p[1] <= w.y1 + CONNECT_TOLERANCE):
                    continue
                for piece in w.pieces:
                    wall_gap = min(wall_gap, rect_gap((p[0], p[2], p[0], p[2]), piece))
            best["wall"] = wall_gap
            if not any(best[t] <= CONNECT_TOLERANCE for t in targets):
                out.append((it.where(), f"{name} ends in the air at ({p[0]:.2f}, {p[1]:.2f}, {p[2]:.2f}): " +
                            ", ".join(f"{t} {best[t] * 100:.0f} cm away" for t in targets)))
    return out


def test_doors(L):
    """Doors that work: the hinge is on the edge of its opening, the swing is clear of items and ends inside the building's room, not in a wall; and nothing solid stands in front of any opening."""
    out = []
    # the approach to every doorway and archway: DOOR_APPROACH_NO_LEAF m in front (a leaf's width plus a margin when it has one), as wide as the opening
    for building in L.buildings:
        for w in L.walls.get(building, []):
            for o in w.openings:
                if o["kind"] == "Window":
                    continue
                (ax, az), (bx, bz) = o["a"], o["b"]
                width = math.hypot(bx - ax, bz - az)
                depth = (width * (0.5 if o.get("double") else 1.0) + DOOR_APPROACH_LEAF_MARGIN) if o["leaf"] else DOOR_APPROACH_NO_LEAF   # two leaves swing half the width each
                cx, cz = (ax + bx) / 2, (az + bz) / 2
                if abs(bx - ax) >= abs(bz - az):
                    zone = (min(ax, bx), cz - depth, max(ax, bx), cz + depth)
                else:
                    zone = (cx - depth, min(az, bz), cx + depth, max(az, bz))
                for it in L.items:
                    if it.building != building or it.floor != w.floor or it.category != "prop" or not it.has_box or it.hidden or it.hung or it.ceiling or it.flat:
                        continue
                    f = L.floor_of(building, it.floor)
                    if f is None or it.top <= f["elevation"] + 0.35 or it.bottom > f["elevation"] + 0.5:
                        continue
                    ox, oz = rect_overlap(zone, it.rect)
                    if ox > 0.03 and oz > 0.03:
                        out.append((it.where(), f"stands in front of {o['name']} on the {w.floor} floor (keep {depth:.2f} m clear)"))
    for d in L.doors:
        hinge = d["hinge"]
        where = f"{d['building']}/{d['floor']}: door {d['name']}"
        ends = []
        for w in L.walls.get(d["building"], []):
            if w.floor != d["floor"]:
                continue
            for o in w.openings:
                if o["kind"] != "Door" or not o["leaf"]:
                    continue
                for e in (o["a"], o["b"]):
                    ends.append(math.hypot(e[0] - hinge[0], e[1] - hinge[2]))
        if ends and min(ends) > DOOR_HINGE_TOLERANCE:
            out.append((where, f"hinge is {min(ends) * 100:.0f} cm from the nearest edge of any opening: it is not on the door's edge"))
        # swing
        cx, cz = d["closedDir"]
        n = math.hypot(cx, cz) or 1.0
        cx, cz = cx / n, cz / n
        rx, rz = cz, -cx                              # to the right of the leaf's direction (the sign of openAngle)
        angle = d["openAngle"]
        steps = max(1, int(abs(angle) / DOOR_ARC_STEP))
        y0, y1 = hinge[1], hinge[1] + min(d["height"], DOOR_SWING_CLEAR_HEIGHT)
        hit = None
        for k in range(1, steps + 1):
            th = math.radians(angle * k / steps)
            dx = cx * math.cos(th) + rx * math.sin(th)
            dz = cz * math.cos(th) + rz * math.sin(th)
            for r in [0.1 * k for k in range(1, int(d["width"] / 0.1) + 1)] + [d["width"] - 0.03]:
                px, pz = hinge[0] + dx * r, hinge[2] + dz * r
                for it in L.items:
                    if it.building not in (d["building"], "") or it.category not in ("prop", "person") or it.flat or it.ceiling or it.hung or it.hidden or not it.has_box:
                        continue
                    if it.top <= y0 + 0.05 or it.bottom >= y1:
                        continue
                    if contains(it.rect, px, pz, 0.0):
                        hit = (it, math.degrees(th))
                        break
                if hit:
                    break
                for w in L.walls.get(d["building"], []):          # the leaf may not swing into a wall (the first 15 cm are its own frame)
                    if w.floor != d["floor"] or r < 0.15 or not w.overlaps_y(y0, y1, 0.5):
                        continue
                    if any(contains(piece, px, pz, -0.02) for piece in w.pieces):
                        hit = (None, math.degrees(th))
                        break
                if hit:
                    break
            if hit:
                break
        if hit:
            what = "a wall" if hit[0] is None else f"{hit[0].name} [{hit[0].kind}] at ({hit[0].pos[0]:.2f}, {hit[0].pos[2]:.2f})"
            out.append((where, f"swing is blocked by {what} after {abs(hit[1]):.0f} degrees"))
    return out


def test_rooms(L):
    """Empty rooms: a room with fewer things than its target, or no NavMesh to walk on; and a cellar that covers the house."""
    out = []
    for building in L.buildings.values():
        fp = building.get("footprint")
        for f in building["floors"]:
            if f["elevation"] >= -0.5 or f["name"] != "Cellar" or not fp:
                continue
            rooms = [r["rect"] for r in f["rooms"]]
            if not rooms:
                continue
            lo_x, lo_z = min(r[0] for r in rooms), min(r[1] for r in rooms)
            hi_x, hi_z = max(r[2] for r in rooms), max(r[3] for r in rooms)
            tol = CELLAR_COVER_TOLERANCE
            if lo_x > fp[0] + tol or lo_z > fp[1] + tol or hi_x < fp[2] - tol or hi_z < fp[3] - tol:
                out.append((f"{building['name']}/{f['name']}", f"the cellar's rooms cover x {lo_x:.1f}..{hi_x:.1f}, z {lo_z:.1f}..{hi_z:.1f}, not the house's footprint {fp[0]:.1f}..{fp[2]:.1f} x {fp[1]:.1f}..{fp[3]:.1f} (the porch stands outside it)"))
            filled = sum((r[2] - r[0]) * (r[3] - r[1]) for r in rooms)
            total = (fp[2] - fp[0]) * (fp[3] - fp[1])
            if filled < CELLAR_MIN_FILL * total:
                out.append((f"{building['name']}/{f['name']}", f"the cellar's rooms add up to {filled:.0f} m2 of the footprint's {total:.0f} m2 (at least {CELLAR_MIN_FILL:.0%}: a room is missing)"))
    for building, f, r in L.rooms:
        target = ROOM_ITEM_TARGET.get(r["name"])
        rect = r["rect"]
        area = (rect[2] - rect[0]) * (rect[3] - rect[1])
        if target:
            count = sum(1 for i in L.items if i.building == building and i.floor == f["name"] and i.room == r["name"]
                        and i.category == "prop" and not i.hung and not i.ceiling and not i.flat)
            if count < target:
                out.append((f"{building}/{f['name']}/{r['name']}", f"holds {count} things, the target is {target} ({area:.0f} m2)"))
        if r["name"] not in ROOM_NAV_EXEMPT and area > 1 and r["navArea"] < area * ROOM_MIN_NAV_FRACTION:
            out.append((f"{building}/{f['name']}/{r['name']}", f"has {r['navArea']:.1f} m2 of NavMesh in {area:.0f} m2: nobody can walk in it"))
    return out


def test_twins(L):
    """Twins: two things of the same kind on the same spot (z-fighting duplicates)."""
    out = []
    items = [i for i in L.items if i.category in ("prop", "person", "animal")]
    for ai, a in enumerate(items):
        for b in items[ai + 1:]:
            if a.kind != b.kind or a.building != b.building:
                continue
            d = math.dist(a.pos, b.pos)
            if d <= TWIN_DISTANCE:
                out.append((a.where(), f"has a twin {b.name} {d * 100:.1f} cm away: two copies on one spot"))
    return out


def test_variety(L):
    """Variety: a kind that should vary is not all one model."""
    out = []
    by = defaultdict(list)
    for it in L.items:
        if it.building and it.category == "prop":
            by[(it.building, it.kind)].append(it)
    for (building, kind), items in sorted(by.items()):
        s = short(kind)
        for pat, most in VARIETY:
            if match(pat, s) and len(items) > most:
                where = ", ".join(f"{i.floor}/{i.room}" for i in items)
                out.append((building, f"{len(items)} x {kind}, identical copies of one model (at most {most} allowed): {where}"))
    return out


def _selftest():
    """Build a small made-up layout with one of each fault in it and check that every test notices its own. Run by `--selftest` (and by dev/check.py)."""
    def item(name, kind, pos, yaw, lo, hi, **kw):
        d = {"name": name, "kind": kind, "category": "prop", "group": "Blocks", "parent": "Blocks", "building": "T", "floor": "Ground", "room": "R", "pos": pos, "yaw": yaw,
             "scale": [1, 1, 1], "rend": {"min": lo, "max": hi}, "floorY": 0.04, "hidden": False}
        d.update(kw)
        return d

    def wall(a, b, **kw):
        d = {"a": a, "b": b, "thickness": 0.25, "exterior": True, "y0": 0.0, "y1": 2.7, "openings": []}
        d.update(kw)
        return d

    walls = [wall([3.4, 3.0], [3.4, 6.0], thickness=0.12, exterior=False), wall([0, 0], [6, 0]), wall([6, 0], [6, 6]), wall([6, 6], [0, 6]), wall([0, 6], [0, 0], openings=[
        {"name": "Door_T", "kind": "Door", "a": [0, 1], "b": [0, 2.2], "sill": 0, "height": 2.2, "leaf": True, "double": False}])]
    data = {"buildings": [{"name": "T", "footprint": [0, 0, 6, 6], "floors": [{"name": "Ground", "elevation": 0, "floorTop": 0.04, "ceiling": 2.7, "bottom": 0, "top": 3, "holes": [],
            "rooms": [{"name": "R", "rect": [0, 0, 6, 6], "navArea": 0.5}, {"name": "Kitchen", "rect": [0, 0, 1, 1], "navArea": 0.5}], "walls": walls,
            "stairs": [{"rect": [2.0, 3.5, 3.2, 6.0], "start": [2.6, 3.5], "dir": [0, 1], "width": 1.2, "rise": 0.19, "run": 0.28, "steps": 16, "y0": 0, "y1": 3.0, "open": False},
                       {"rect": [3.0, 3.2, 3.8, 5.0], "start": [3.4, 3.2], "dir": [0, 1], "width": 0.8, "rise": 0.19, "run": 0.28, "steps": 6, "y0": 0, "y1": 1.1, "open": False}]}]}],
            "items": [
                # a sofa against the south wall (z 0.125) facing the wall (yaw 180 faces -z)
                item("Sofa", "GH_Sofa_01", [3, 0.04, 0.6], 180, [2.0, 0.04, 0.125], [4.0, 0.9, 1.0]),
                # a kid whose feet are below the floor and a table lamp beside its table, and a second one floating above
                item("Kid", "GP_Kid_01", [4, -0.1, 4], 0, [3.6, -0.1, 3.8], [4.4, 1.2, 4.2], category="person", state="Idle"),
                item("Table", "GH_Table_Side_01", [5, 0.04, 5], 0, [4.75, 0.04, 4.75], [5.25, 0.61, 5.25]),
                item("Lamp", "GD_TableLamp_01", [4.3, 0.61, 5.0], 0, [4.16, 0.61, 4.86], [4.44, 1.05, 5.14]),
                # two washers and two twins, no dryer
                item("Washer", "GI_Washer_01", [1.0, 0.04, 5.5], 0, [0.7, 0.04, 5.2], [1.3, 0.94, 5.85]),
                item("Washer", "GI_Washer_01", [2.0, 0.04, 5.5], 0, [1.7, 0.04, 5.2], [2.3, 0.94, 5.85]),
                item("Bookcase", "GH_Bookcase_01", [5.8, 0.04, 2.0], 270, [5.55, 0.04, 1.6], [5.87, 1.8, 2.4]),
                item("Bookcase", "GH_Bookcase_01", [5.8, 0.04, 2.0], 270, [5.55, 0.04, 1.6], [5.87, 1.8, 2.4]),
                item("Bookcase", "GH_Bookcase_01", [5.8, 0.04, 3.2], 270, [5.55, 0.04, 2.8], [5.87, 1.8, 3.6]),
                # a heater whose pipes end in the air
                item("WaterHeater", "GH_WaterHeater_01", [3.0, 0.04, 5.6], 0, [2.74, 0.04, 5.34], [3.26, 1.38, 5.86]),
                # a cabinet 6 cm from the wall
                item("Cabinet", "GH_Cabinet_01", [3.0, 0.04, 2.0], 0, [2.5, 0.04, 1.9], [3.5, 1.0, 2.4]),
            ],
            "doors": [{"name": "Door_T", "building": "T", "floor": "Ground", "hinge": [0, 0, 2.2], "closedDir": [0, -1], "width": 1.16, "height": 2.15, "openAngle": -90}]}
    data["items"].append(item("Crate", "GT_Crate_01", [2.6, 0.04, 3.0], 0, [2.35, 0.04, 2.75], [2.85, 0.54, 3.25]))   # at the foot of the first stair (foot at z 3.5, the zone runs back to z 2.5)
    data["items"].append(item("Frame", "GD_Frame_Landscape_01", [3.0, 1.6, 3.0], 0, [2.7, 1.4, 2.95], [3.3, 1.8, 3.0]))   # hung in the middle of the room
    data["items"].append(item("Cow", "GN_Cow_faceted_01", [4.5, 1.0, 1.0], 0, [4.0, 1.0, 0.5], [5.0, 2.4, 1.5], category="animal"))   # a cow in the air
    data["items"].append(item("Bulb", "GL_BareBulb_01", [5.0, 1.2, 4.5], 0, [4.9, 1.2, 4.4], [5.1, 1.6, 4.6]))   # its cord ends at y 2.4, 30 cm short of the ceiling
    data["items"].append(item("Grandpa", "GP_Grandparent_01", [1.5, 0.04, 3.0], 0, [1.1, 0.04, 2.8], [1.9, 1.9, 3.2], category="person", state="Sit"))   # sits on nothing
    data["items"].append(item("Crate", "GT_Crate_01", [1.0, 0.04, 1.4], 0, [0.7, 0.04, 1.1], [1.4, 0.6, 1.7]))   # in the swing of the door (hinge at z 2.2, leaf runs to z 1.04)
    CONNECTED["GH_WaterHeater_01"] = [("pipe end", (0.0, 0.0, 1.34), ("wall", "ceiling"))]   # the real model's pipes end in a plate on the wall (no free end): the test needs a heater whose pipe ends in the air
    L = Layout(data)
    wanted = {"floor": ["below the floor", "off its support", "sits on nothing", "floats"], "facing": ["points"], "clearance": ["stair", "from the wall", "into a wall", "foot of the stair"], "unique": ["where there is one per house", "no Dryer"],
              "hung": ["hangs in the room"], "connected": ["pipe", "cord top"], "doors": ["blocked", "in front of Door_T"], "rooms": ["holds", "NavMesh"], "twins": ["twin"], "variety": ["identical"]}
    failed = 0
    # a cellar whose rooms do not cover the house's footprint
    small = {"buildings": [{"name": "C", "footprint": [0, 0, 6, 6], "floors": [{"name": "Cellar", "elevation": -3, "floorTop": -2.97, "ceiling": -0.15, "bottom": -3.3, "top": -0.15, "holes": [],
                                                                           "rooms": [{"name": "Rc", "rect": [0, 0, 3, 3], "navArea": 5.0}], "walls": [], "stairs": []}]}], "items": [], "doors": []}
    text = chr(10).join(f"{w}: {m}" for w, m in test_rooms(Layout(small)))
    if "not the house's footprint" not in text:
        print("selftest: rooms did not report a cellar that is not the house's footprint")
        failed += 1
    # a cellar with a room missing: the rooms that are left still span the footprint (corners), but do not fill it
    gap = {"buildings": [{"name": "C", "footprint": [0, 0, 6, 6], "floors": [{"name": "Cellar", "elevation": -3, "floorTop": -2.97, "ceiling": -0.15, "bottom": -3.3, "top": -0.15, "holes": [],
                                                                         "rooms": [{"name": "Ra", "rect": [0, 0, 2, 2], "navArea": 3.0}, {"name": "Rb", "rect": [4, 4, 6, 6], "navArea": 3.0}], "walls": [], "stairs": []}]}], "items": [], "doors": []}
    text = chr(10).join(f"{w}: {m}" for w, m in test_rooms(Layout(gap)))
    if "a room is missing" not in text:
        print("selftest: rooms did not report a missing cellar room")
        failed += 1
    apply_rules({})   # the selftest layouts carry no rules: the defaults
    for name, needles in wanted.items():
        text = chr(10).join(f"{w}: {m}" for w, m in TESTS[name](L))
        for needle in needles:
            if needle not in text:
                print(f"selftest: {name} did not report '{needle}'")
                failed += 1
    del CONNECTED["GH_WaterHeater_01"]
    print("selftest: " + ("ok" if not failed else f"{failed} test(s) missed their fault"))
    return 1 if failed else 0


TESTS = {
    "floor": test_floor,
    "hung": test_hung,
    "facing": test_facing,
    "clearance": test_clearance,
    "unique": test_unique,
    "connected": test_connected,
    "doors": test_doors,
    "rooms": test_rooms,
    "twins": test_twins,
    "variety": test_variety,
}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("json", nargs="?", default=None, help=f"the layout dump (default {DEFAULT_JSON} in the repository)")
    ap.add_argument("--only", help="comma-separated tests to run")
    ap.add_argument("--list", action="store_true", help="list the tests")
    ap.add_argument("--selftest", action="store_true", help="check the tests against a made-up layout with one of each fault")
    args = ap.parse_args(argv)

    if args.selftest:
        return _selftest()
    if args.list:
        for name, fn in TESTS.items():
            print(f"{name:10} {fn.__doc__.strip().splitlines()[0]}")
        return 0

    path = Path(args.json) if args.json else Path(__file__).resolve().parent.parent.parent / DEFAULT_JSON
    if not path.exists():
        print(f"layout audit: {path} not found: run FarmsteadLayoutDump.Run (see the layout-audit skill)", file=sys.stderr)
        return 2
    L = Layout(json.loads(path.read_text(encoding="utf-8")))

    chosen = [t.strip() for t in args.only.split(",")] if args.only else list(TESTS)
    unknown = [t for t in chosen if t not in TESTS]
    if unknown:
        print("layout audit: unknown test " + ", ".join(unknown) + " (--list)", file=sys.stderr)
        return 2

    problems = 0
    for name in chosen:
        for where, message in TESTS[name](L):
            print(f"FAIL {name}: {where}: {message}")
            problems += 1
    if problems:
        print(f"layout audit: {problems} problem(s) in {len(L.items)} items")
        return 1
    print(f"layout audit: ok ({len(L.items)} items, {len(chosen)} tests)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
