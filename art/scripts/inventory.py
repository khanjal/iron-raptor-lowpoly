#!/usr/bin/env python3
"""The asset inventory (issue #345, step 1): every art model, its size and what interactions.json says about it.

Plain Python 3, standard library only. It needs no Blender, no Unity and no LFS objects: in a cloud checkout the
FBX are Git LFS pointer files, and their `size N` line is the size of the real file.

    python art/scripts/inventory.py            writes docs/assets/inventory.md
    python art/scripts/inventory.py --check    exits 1 when the committed file is out of date

What it reads
  - Assets/Art/**/*.fbx, leaving out `Anims/` folders and any name with `＠` (animation sources)
  - art/data/interactions.json: `props[<file name without extension>]` -> emitters (light/sound/switch), parts, traits
  - `--dev-world Logs/dev_world_inventory.json` (opt-in, a list of {"id", "tris", "materials"}): fills the Tris and Mats columns.
    The Unity dev test world is meant to write it later; until it does the columns stay empty.

The id of a model is its path under Assets/Art without the extension (`Global/Animals/GN_Cow_faceted_01`),
the id the dev test world shows.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
ART = ROOT / "Assets" / "Art"
INTERACTIONS = ROOT / "art" / "data" / "interactions.json"
DEV_WORLD = ROOT / "Logs" / "dev_world_inventory.json"
OUT = ROOT / "docs" / "assets" / "inventory.md"

STYLES = ("Classic", "Modern", "Retro", "Damaged")
STYLE_GROUPS = ("Household", "Decor", "Interactive")   # their style folders are a column of the parent's table, not tables
ANIM_MARK = "@"                                     # the at sign of a clip file, `GP_Humanoid@Idle.fbx`
LFS_MAGIC = b"version https://git-lfs"


# -----------------------------------------------------------------------------
# Reading
# -----------------------------------------------------------------------------

def file_size(path):
    """Bytes of the real model: the `size N` line of a Git LFS pointer, or the file's own size if it is a real FBX."""
    with open(path, "rb") as f:
        head = f.read(512)
    if head.startswith(LFS_MAGIC):
        for line in head.decode("utf-8", "replace").splitlines():
            if line.startswith("size "):
                return int(line.split()[1])
    return path.stat().st_size


def is_model(path, art):
    rel = path.relative_to(art)
    return path.suffix.lower() == ".fbx" and "Anims" not in rel.parts[:-1] and ANIM_MARK not in path.name


def classify(rel_parts):
    """(category, style, group) of a model from its folders: `Global/Household/Retro/x.fbx` -> Global/Household, Retro, "";
    `Global/Vehicles/Sedan/x.fbx` -> Global/Vehicles, "", Sedan."""
    folders = list(rel_parts[:-1])
    category = "/".join(folders[:2])
    rest = folders[2:]
    style, group = "", ""
    if len(folders) >= 2 and folders[1] in STYLE_GROUPS:
        style = rest[0] if rest and rest[0] in STYLES else "base"
        rest = rest[1:] if rest and rest[0] in STYLES else rest
    group = "/".join(rest)
    return category, style, group


def entry_summary(entry):
    """Counts from one `props` entry of interactions.json, or None when the model has no entry."""
    if entry is None:
        return None
    kinds = {"light": 0, "sound": 0, "switch": 0}
    for emitter in (entry.get("emitters") or {}).values():
        kind = emitter.get("kind")
        if kind in kinds:
            kinds[kind] += 1
    return {**kinds, "parts": len(entry.get("parts") or {}), "traits": list(entry.get("traits") or [])}


def collect(art=ART, interactions=INTERACTIONS):
    """One record per model, sorted by id."""
    props = {}
    if Path(interactions).exists():
        props = json.loads(Path(interactions).read_text(encoding="utf-8")).get("props", {})
    models = []
    for path in Path(art).rglob("*.fbx"):
        if not is_model(path, Path(art)):
            continue
        rel = path.relative_to(art)
        category, style, group = classify(rel.parts)
        models.append({
            "id": rel.with_suffix("").as_posix(),
            "category": category, "style": style, "group": group,
            "size": file_size(path),
            "entry": entry_summary(props.get(path.stem)),
        })
    models.sort(key=lambda m: m["id"])
    return models


def load_dev_world(path=DEV_WORLD):
    """{id: {"tris", "materials"}} from the dev test world's file; empty when the file is missing or unreadable."""
    path = Path(path)
    if not path.exists():
        return {}
    try:
        rows = json.loads(path.read_text(encoding="utf-8"))
        return {r["id"]: r for r in rows if isinstance(r, dict) and "id" in r}
    except (ValueError, KeyError, TypeError):
        return {}


# -----------------------------------------------------------------------------
# Writing the table
# -----------------------------------------------------------------------------

def has(m, key):
    e = m["entry"]
    return e is not None and (e[key] if key == "parts" else e["light"] + e["sound"] + e["switch"]) > 0


def cell(value):
    return "" if value is None else str(value)


def render(models, dev_world=None):
    dev_world = dev_world or {}
    by_category = {}
    for m in models:
        by_category.setdefault(m["category"], []).append(m)

    out = [
        "# Asset inventory",
        "",
        "Every model under `Assets/Art` (animation sources left out), made by `art/scripts/inventory.py` "
        "(issue #345, step 1) with plain Python: no Blender, no Unity. Do not edit by hand; run",
        "",
        "```",
        "python art/scripts/inventory.py",
        "```",
        "",
        "- **Id** is the path under `Assets/Art` without the extension, the id the dev test world shows.",
        "- **Bytes** is the FBX size (read from the Git LFS pointer in a cloud checkout).",
        "- **Light / Sound / Switch / Parts** count the `emitters` (by kind) and `parts` that `art/data/interactions.json` gives the model; "
        "**Traits** are its alien-ability traits. A model with no entry there has – in those columns.",
        "- **Tris** and **Mats** (triangles and materials) stay empty in the committed table: they need a Unity run, so they are filled only "
        "with `--dev-world <file>` (a list of `{\"id\", \"tris\", \"materials\"}` the dev test world is meant to write; nothing writes it yet, #345). "
        "The table is regenerated on demand with `python art/scripts/inventory.py`; `dev/check.py` does not check it, so rerun it after adding models.",
        "",
        "## Summary",
        "",
        "| Category | Models | With an entry | With emitters | With parts | Bytes |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for category in sorted(by_category):
        ms = by_category[category]
        out.append(f"| [{category}](#{anchor(category)}) | {len(ms)} | {sum(m['entry'] is not None for m in ms)} | "
                   f"{sum(has(m, 'emitters') for m in ms)} | {sum(has(m, 'parts') for m in ms)} | {sum(m['size'] for m in ms)} |")
    out.append(f"| **Total** | {len(models)} | {sum(m['entry'] is not None for m in models)} | "
               f"{sum(has(m, 'emitters') for m in models)} | {sum(has(m, 'parts') for m in models)} | {sum(m['size'] for m in models)} |")

    vehicles = [m for m in models if m["category"] == "Global/Vehicles"]
    if vehicles:
        out += ["", "## Vehicles with no `interactions.json` entry", "",
                "Models without an entry have no lights, sounds, switches or moving parts in the data; "
                "the Global/Vehicles table below shows \u2013 for each of them.", "",
                "| Group | Models | With an entry | Without |", "|---|---:|---:|---:|"]
        groups = {}
        for m in vehicles:
            groups.setdefault(m["group"] or ("Ship hulls and interior props" if m["id"].rsplit("/", 1)[-1].startswith(("GV_Ship", "GV_CrashedShip")) else "Road vehicles (loose)"), []).append(m)
        for g in sorted(groups):
            with_entry = sum(m["entry"] is not None for m in groups[g])
            out.append(f"| {g} | {len(groups[g])} | {with_entry} | {len(groups[g]) - with_entry} |")

    for category in sorted(by_category):
        ms = by_category[category]
        show_style = any(m["style"] for m in ms)
        show_group = any(m["group"] for m in ms)
        head = ["Id"] + (["Style"] if show_style else []) + (["Group"] if show_group else []) + \
               ["Bytes", "Light", "Sound", "Switch", "Parts", "Traits", "Tris", "Mats"]
        out += ["", f"## {category}", "", f"{len(ms)} models.", "",
                "| " + " | ".join(head) + " |",
                "|" + "|".join("---" if h in ("Id", "Style", "Group", "Traits") else "---:" for h in head) + "|"]
        for m in ms:
            e, d = m["entry"], dev_world.get(m["id"], {})
            row = [f"`{m['id']}`"] + ([m["style"]] if show_style else []) + ([m["group"]] if show_group else []) + [str(m["size"])]
            if e is None:
                row += ["–"] * 5
            else:
                row += [str(e["light"]), str(e["sound"]), str(e["switch"]), str(e["parts"]), ", ".join(e["traits"])]
            row += [cell(d.get("tris")), cell(d.get("materials"))]
            out.append("| " + " | ".join(row) + " |")
    return "\n".join(out) + "\n"


def anchor(category):
    return category.lower().replace("/", "")   # GitHub drops the slash from "## Global/Animals"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=str(OUT), help="the markdown file to write")
    ap.add_argument("--dev-world", default=None, help="the dev test world's tris/materials file, e.g. Logs/dev_world_inventory.json (opt-in: with no flag the table has no Tris, so it is the same on every machine)")
    ap.add_argument("--check", action="store_true", help="write nothing; exit 1 if the file differs from what would be written")
    args = ap.parse_args(argv)

    models = collect()
    dev_world = load_dev_world(args.dev_world) if args.dev_world else {}
    text = render(models, dev_world)
    out = Path(args.out)
    if args.check:
        same = out.exists() and out.read_text(encoding="utf-8") == text
        print("inventory: up to date" if same else f"inventory: {out} is out of date, run art/scripts/inventory.py")
        return 0 if same else 1
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8", newline="\n")
    print(f"{len(models)} models -> {out}" + (f" (tris for {len(dev_world)} from the dev world)" if dev_world else " (no dev world file: Tris empty)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
