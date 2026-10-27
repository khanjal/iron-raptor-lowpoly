"""Print what is in a GLB: nodes, animations (name, duration), sizes. Usage: python tools/glbinfo.py site/models/X.glb"""
import json
import struct
import sys

from stamp_glb import project_path


def read(path):
    """(json, bytes) of a GLB inside the project; ValueError when it is not."""
    raw = project_path(path).read_bytes()
    jlen, _ = struct.unpack_from("<II", raw, 12)
    return json.loads(raw[20:20 + jlen]), raw


if __name__ == "__main__":
    for path in sys.argv[1:]:
        try:
            d, raw = read(path)
        except ValueError as e:
            print(e, file=sys.stderr)
            sys.exit(2)
        print(path, len(raw), "bytes;", len(d.get("nodes", [])), "nodes;", len(d.get("skins", [])), "skins")
        acc = d.get("accessors", [])
        for a in d.get("animations", []):
            t = max(acc[s["input"]]["max"][0] for s in a["samplers"])
            print("  animation", a["name"], round(t, 3), "s,", len(a["channels"]), "channels")
        if "-n" in sys.argv:
            for n in d["nodes"]:
                print("  node", n.get("name"), {k: n[k] for k in ("translation", "rotation", "scale") if k in n})
