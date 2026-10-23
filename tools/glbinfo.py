"""Print what is in a GLB: nodes, animations (name, duration), sizes. Usage: python tools/glbinfo.py site/models/X.glb"""
import json
import struct
import sys


def read(path):
    raw = open(path, "rb").read()
    jlen, _ = struct.unpack_from("<II", raw, 12)
    return json.loads(raw[20:20 + jlen]), raw


if __name__ == "__main__":
    for path in sys.argv[1:]:
        d, raw = read(path)
        print(path, len(raw), "bytes;", len(d.get("nodes", [])), "nodes;", len(d.get("skins", [])), "skins")
        acc = d.get("accessors", [])
        for a in d.get("animations", []):
            t = max(acc[s["input"]]["max"][0] for s in a["samplers"])
            print("  animation", a["name"], round(t, 3), "s,", len(a["channels"]), "channels")
        if "-n" in sys.argv:
            for n in d["nodes"]:
                print("  node", n.get("name"), {k: n[k] for k in ("translation", "rotation", "scale") if k in n})
