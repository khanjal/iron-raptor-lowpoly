"""Every model in site/models/ is painted from the palette image: each of its materials carries a base-colour texture.

A GLB whose material lost its texture (a Blender file shared with other work can export an empty image node) shows flat white in the viewer, and the colour
pickers, which repaint that texture, cannot change it.
"""
import json
import struct
import unittest
from pathlib import Path

MODELS = Path(__file__).resolve().parents[1] / "site" / "models"


def gltf_json(path):
    raw = path.read_bytes()
    length = struct.unpack("<I", raw[12:16])[0]
    return json.loads(raw[20:20 + length])


class PaletteTextures(unittest.TestCase):
    def test_every_material_has_a_base_colour_texture(self):
        files = sorted(MODELS.glob("*.glb"))
        self.assertGreater(len(files), 100)
        bad = []
        for f in files:
            doc = gltf_json(f)
            for m in doc.get("materials", []):
                if "baseColorTexture" not in m.get("pbrMetallicRoughness", {}):
                    bad.append(f"{f.name}:{m.get('name')}")
            if doc.get("materials") and not doc.get("images"):
                bad.append(f"{f.name}: no image")
        self.assertEqual(bad, [], "materials without the palette texture render white")


if __name__ == "__main__":
    unittest.main()
