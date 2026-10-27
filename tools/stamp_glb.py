"""Write the credit line into the `asset.copyright` field of GLB files (standard library only, no Blender), so it travels with the model.

    python tools/stamp_glb.py                 # every site/models/*.glb
    python tools/stamp_glb.py a.glb b.glb     # just these (the files must be inside the project)

Only the JSON chunk is rewritten (padded with spaces to a multiple of 4 bytes, the binary chunk is copied unchanged), and a file that already has the
line is left alone, so running it twice changes nothing. Blender's exporter writes the same line when art/scripts/common.py builds a GLB
(`GLB_COPYRIGHT`, which must equal COPYRIGHT here: tests/test_stamp_glb.py checks), so this tool is for models built before that.
"""

import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COPYRIGHT = "CC BY 4.0, khanjal, https://github.com/khanjal/iron-raptor-lowpoly"
JSON_CHUNK = 0x4E4F534A


def project_path(arg, root=ROOT):
    """`arg` as a resolved path; ValueError when it is not inside `root`."""
    path = Path(arg).resolve()
    if not path.is_relative_to(Path(root).resolve()):
        raise ValueError(f"outside the project: {arg}")
    return path


def rewrite_json(raw, mutate):
    """The GLB bytes with `mutate(doc)` applied to the JSON chunk (the same bytes when mutate returns False; the binary chunk is copied unchanged)."""
    if len(raw) < 20 or raw[:4] != b"glTF":
        raise ValueError("not a GLB (bad magic)")
    jlen, jtype = struct.unpack_from("<II", raw, 12)
    if jtype != JSON_CHUNK:
        raise ValueError("first chunk is not JSON")
    doc = json.loads(raw[20:20 + jlen].decode("utf-8"))
    if mutate(doc) is False:
        return raw
    body = json.dumps(doc, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    body += b" " * (-len(body) % 4)
    rest = raw[20 + jlen:]
    return b"glTF" + struct.pack("<II", 2, 12 + 8 + len(body) + len(rest)) + struct.pack("<II", len(body), JSON_CHUNK) + body + rest


def stamp_bytes(raw, copyright=COPYRIGHT):
    """The GLB bytes with asset.copyright set (the same bytes when it is already set)."""
    def mutate(doc):
        if doc.get("asset", {}).get("copyright") == copyright:
            return False
        doc.setdefault("asset", {})["copyright"] = copyright
    return rewrite_json(raw, mutate)


def stamp(path, copyright=COPYRIGHT):
    """Stamp one file in place; True if it changed. ValueError when the file is not inside the project."""
    path = project_path(path)
    raw = path.read_bytes()
    new = stamp_bytes(raw, copyright)
    if new == raw:
        return False
    # the bytes written are this file's own, with one JSON field set; the path was checked by project_path above
    path.write_bytes(new)  # NOSONAR
    return True


if __name__ == "__main__":
    try:
        files = [project_path(a) for a in sys.argv[1:]] or sorted((ROOT / "site" / "models").glob("*.glb"))
    except ValueError as e:
        print(e, file=sys.stderr)
        sys.exit(2)
    changed = 0
    for f in files:
        try:
            changed += stamp(f)
        except ValueError as e:
            print(f"FAIL {f}: {e}")
            sys.exit(1)
    print(f"{changed} of {len(files)} files stamped")
