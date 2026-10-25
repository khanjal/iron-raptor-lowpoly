"""Every looping clip in site/models/ ends where it starts: its last key equals its first.

The first keys of a clip were once set from the previous clip's pose (the earlier NLA tracks were still live while the next clip was keyed), so in the viewer
Walk, Run and Sit snapped to a wrong pose for a few frames every time they looped (issue #95).
"""
import json
import struct
import unittest
from pathlib import Path

MODELS = Path(__file__).resolve().parents[1] / "site" / "models"
TOLERANCE = 0.02                                                     # a rotation compared as |dot| of the quaternions, a translation in metres


def read(path):
    raw = path.read_bytes()
    jlen = struct.unpack_from("<I", raw, 12)[0]
    return json.loads(raw[20:20 + jlen]), raw[20 + jlen + 8:]


def values(doc, binary, index):
    acc = doc["accessors"][index]
    view = doc["bufferViews"][acc["bufferView"]]
    width = {"SCALAR": 1, "VEC3": 3, "VEC4": 4}[acc["type"]]
    flat = struct.unpack_from("<%df" % (acc["count"] * width), binary, view.get("byteOffset", 0) + acc.get("byteOffset", 0))
    return [flat[i * width:(i + 1) * width] for i in range(acc["count"])]


def mismatch(path, a, b):
    if path == "rotation":
        return 1.0 - abs(sum(x * y for x, y in zip(a, b)))
    return max(abs(x - y) for x, y in zip(a, b))


class ClipLoops(unittest.TestCase):
    def test_last_key_equals_first(self):
        bad = []
        for glb in sorted(MODELS.glob("*.glb")):
            doc, binary = read(glb)
            for anim in doc.get("animations", []):
                for ch in anim["channels"]:
                    if ch["target"]["path"] not in ("rotation", "translation"):
                        continue
                    out = values(doc, binary, anim["samplers"][ch["sampler"]]["output"])
                    gap = mismatch(ch["target"]["path"], out[0], out[-1])
                    if gap > TOLERANCE:
                        bad.append((gap, f"{glb.name} {anim['name']} {doc['nodes'][ch['target']['node']].get('name')} {ch['target']['path']}"))
        bad.sort(reverse=True)
        self.assertEqual([], [f"{name} (off by {gap:.2f})" for gap, name in bad[:15]], f"{len(bad)} channels do not close their loop")


if __name__ == "__main__":
    unittest.main()
