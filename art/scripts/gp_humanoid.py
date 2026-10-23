"""GP-01..03 base person: the plain low-poly humanoid on the Universal Animation Library skeleton.

Run in Blender:  import runpy; runpy.run_path(r"<repo>/art/scripts/gp_humanoid.py", run_name="__main__")
Exports Assets/Art/Global/People/GP_Humanoid_Base_01.fbx. All the work is in gp_builder.py; see gp_cast.py for
the named characters (farmer, sheriff, FBI agent, Man in Black...).
"""

import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gp_builder
importlib.reload(gp_builder)

body, rig, coll = gp_builder.build("GP_Humanoid_Base_01", export="Assets/Art/Global/People/GP_Humanoid_Base_01.fbx")
print(gp_builder.common.stats(body))
