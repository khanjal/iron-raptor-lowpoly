"""Every clip in site/models/ ends where it starts: its last key equals its first.

The first keys of a clip were once set from the previous clip's pose (the earlier NLA tracks were still live while the next clip was keyed), so in the viewer
Walk, Run and Sit snapped to a wrong pose for a few frames every time they looped (issue #95).
"""
import json
import struct
import unittest
from pathlib import Path

MODELS = Path(__file__).resolve().parents[1] / "site" / "models"
ROTATION = 0.001                                                     # 1 - |dot| of the two quaternions (about 5 degrees); the original glitches were 0.007 to 0.4
TRANSLATION = 0.001                                                  # metres


def read(path):
    raw = path.read_bytes()
    jlen = struct.unpack_from("<I", raw, 12)[0]
    return json.loads(raw[20:20 + jlen]), raw[20 + jlen + 8:]


def values(doc, binary, index):
    acc = doc["accessors"][index]
    if acc["componentType"] != 5126 or acc.get("normalized") or "sparse" in acc:
        raise AssertionError("this test reads plain float accessors")
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
        bad, checked = [], 0
        for glb in sorted(MODELS.glob("*.glb")):
            doc, binary = read(glb)
            for anim in doc.get("animations", []):
                for ch in anim["channels"]:
                    if ch["target"]["path"] not in ("rotation", "translation"):
                        continue
                    sampler = anim["samplers"][ch["sampler"]]
                    if sampler.get("interpolation", "LINEAR") not in ("LINEAR", "STEP"):
                        raise AssertionError(f"{glb.name} {anim['name']}: first and last values are not the ends of a cubic spline")
                    out = values(doc, binary, sampler["output"])
                    checked += 1
                    gap = mismatch(ch["target"]["path"], out[0], out[-1])
                    if gap > (ROTATION if ch["target"]["path"] == "rotation" else TRANSLATION):
                        bad.append((gap, f"{glb.name} {anim['name']} {doc['nodes'][ch['target']['node']].get('name')} {ch['target']['path']}"))
        self.assertGreater(checked, 1000, "the clips of site/models/ were not found")
        bad.sort(reverse=True)
        self.assertEqual([], [f"{name} (off by {gap:.4f})" for gap, name in bad[:15]], f"{len(bad)} channels do not close their loop")


if __name__ == "__main__":
    unittest.main()
