"""Things that go inside things (asset list GH-, GT-, GN-82): food, drinks, groceries, clothes and pet treats. Flat faceted models.

Run in Blender:  import runpy; runpy.run_path(r"<repo>/art/scripts/contents.py", run_name="__main__")
Optional global CONTENT_LIST (item or group names). Exports Assets/Art/Global/<Food|Clothes>/<Group>/FD_<Name>_01.fbx, and for the fresh
food groups a Rotten version (FD_<Name>_Rotten_01.fbx) for abandoned houses and the trailer park.

All real size (an apple is 8 cm, a milk carton 0.2 m tall, a shirt on a hanger 0.7 m), origin on the base so an item sits on whatever
surface its slot is on. The slots in the interactive appliances (interactive.py) say where items can sit; game code decides which kind goes where and spawns the prefabs there.
Groups: produce, bakery, dairy, drinks, canned, boxed, prepared, pet, clothes.
"""

import importlib
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common
import props_lib
for _m in (common, props_lib):
    importlib.reload(_m)
Prop = props_lib.Prop
lathe, ball = props_lib.lathe, props_lib.ball

ITEMS = {}


def item(group, name):
    def deco(fn):
        ITEMS[name] = (fn, group)
        return fn
    return deco


# ===== Produce =================================================================================================
@item("produce", "Apple")
def apple():
    p = Prop("FD_Apple_01"); ball(p, "cloth_red", (0, 0, 0.04), 0.04, n=7, squash=0.9); p.box("bark", (0, 0, 0.088), (0.006, 0.006, 0.02)); return p


@item("produce", "Orange")
def orange():
    p = Prop("FD_Orange_01"); ball(p, "food_orange", (0, 0, 0.04), 0.04, n=7); p.box("plant_green", (0, 0, 0.082), (0.015, 0.015, 0.004)); return p


@item("produce", "Banana")
def banana():
    p = Prop("FD_Banana_01")
    for k, (x, z, r) in enumerate(((-0.07, 0.02, 20), (-0.025, 0.012, 8), (0.025, 0.012, -8), (0.07, 0.02, -20))):
        p.box("paint_yellow", (x, 0, z), (0.05, 0.03, 0.028), rot=(0, r, 0))
    p.box("bark", (-0.095, 0, 0.035), (0.012, 0.012, 0.02))
    return p


@item("produce", "Carrot")
def carrot():
    p = Prop("FD_Carrot_01"); lathe(p, "food_orange", [(0.0, 0.0001), (0.01, 0.006), (0.14, 0.02), (0.15, 0.02)], n=6)
    p.box("plant_green", (0, 0, 0.17), (0.03, 0.03, 0.06), taper=0.5); return p


@item("produce", "Tomato")
def tomato():
    p = Prop("FD_Tomato_01"); ball(p, "cloth_red", (0, 0, 0.035), 0.04, n=7, squash=0.8); p.box("plant_green", (0, 0, 0.066), (0.025, 0.025, 0.006)); return p


@item("produce", "Potato")
def potato():
    p = Prop("FD_Potato_01"); ball(p, "tan", (0, 0, 0.03), 0.045, n=6, squash=0.65); return p


@item("produce", "Onion")
def onion():
    p = Prop("FD_Onion_01"); ball(p, "golden", (0, 0, 0.04), 0.04, n=6, squash=0.9); p.box("dead_wood", (0, 0, 0.095), (0.008, 0.008, 0.025), taper=0.4); return p


@item("produce", "Corn")
def corn():
    p = Prop("FD_Corn_01")
    lathe(p, "corn_cob", [(0.0, 0.0001), (0.02, 0.025), (0.18, 0.028), (0.21, 0.012)], n=8)
    for a in (0, 120, 240):
        p.box("corn_leaf", (0.02 * math.cos(math.radians(a)), 0.02 * math.sin(math.radians(a)), 0.1), (0.01, 0.04, 0.2), rot=(0, 0, a), taper=0.7)
    return p


@item("produce", "Lettuce")
def lettuce():
    p = Prop("FD_Lettuce_01"); ball(p, "corn_leaf", (0, 0, 0.07), 0.09, n=8, squash=0.85); ball(p, "plant_green", (0, 0, 0.09), 0.05, n=6); return p


@item("produce", "Cabbage")
def cabbage():
    p = Prop("FD_Cabbage_01"); ball(p, "siding_green", (0, 0, 0.1), 0.11, n=8, squash=0.9); return p


@item("produce", "Pumpkin")
def pumpkin():
    p = Prop("FD_Pumpkin_01"); ball(p, "food_orange", (0, 0, 0.13), 0.16, n=8, squash=0.8); p.box("plant_green", (0, 0, 0.27), (0.04, 0.04, 0.07), taper=0.6); return p


@item("produce", "Watermelon")
def watermelon():
    p = Prop("FD_Watermelon_01"); ball(p, "plant_green", (0, 0, 0.12), 0.17, n=8, squash=0.7)
    for a in range(0, 360, 60):
        p.box("leaf_dark", (0.12 * math.cos(math.radians(a)), 0.12 * math.sin(math.radians(a)), 0.12), (0.02, 0.1, 0.22), rot=(0, 0, a))
    return p


# ===== Bakery ==================================================================================================
@item("bakery", "BreadLoaf")
def bread_loaf():
    p = Prop("FD_BreadLoaf_01"); p.box("crust", (0, 0, 0.06), (0.24, 0.12, 0.1)); ball(p, "crust", (0, 0, 0.1), 0.065, n=6, squash=0.6)
    for x in (-0.05, 0.0, 0.05):
        p.box("dough", (x, -0.0, 0.14), (0.01, 0.1, 0.01))
    return p


@item("bakery", "Baguette")
def baguette():
    p = Prop("FD_Baguette_01"); p.cyl("crust", (0, 0, 0.04), 0.04, 0.7, n=6, axis="y"); p.box("dough", (0, -0.0, 0.082), (0.01, 0.5, 0.004)); return p


@item("bakery", "Pie")
def pie():
    p = Prop("FD_Pie_01"); lathe(p, "metal_galv", [(0.0, 0.1), (0.04, 0.12)], n=10); lathe(p, "crust", [(0.0, 0.11), (0.05, 0.115), (0.06, 0.1)], n=10)
    for a in range(0, 360, 90):
        p.box("dough", (0.04 * math.cos(math.radians(a)), 0.04 * math.sin(math.radians(a)), 0.062), (0.1, 0.01, 0.006), rot=(0, 0, a))
    return p


@item("bakery", "Cake")
def cake():
    p = Prop("FD_Cake_01")
    p.cyl("paint_white", (0, 0, 0.06), 0.14, 0.12, n=10); p.cyl("fabric_pink", (0, 0, 0.16), 0.11, 0.08, n=10); p.cyl("cloth_red", (0, 0, 0.215), 0.04, 0.03, n=6)
    for a in range(0, 360, 90):
        p.cyl("paint_yellow", (0.07 * math.cos(math.radians(a)), 0.07 * math.sin(math.radians(a)), 0.225), 0.006, 0.05, n=4)
    p.cyl("metal_galv", (0, 0, 0.005), 0.16, 0.01, n=10); return p


@item("bakery", "Donut")
def donut():
    p = Prop("FD_Donut_01"); p.cyl("crust", (0, 0, 0.02), 0.045, 0.04, n=8); p.cyl("fabric_pink", (0, 0, 0.042), 0.04, 0.006, n=8); p.cyl("black", (0, 0, 0.03), 0.014, 0.045, n=6); return p


@item("bakery", "CookieJar")
def cookie_jar():
    p = Prop("FD_CookieJar_01"); p.cyl("glass", (0, 0, 0.1), 0.09, 0.2, n=8); p.cyl("terracotta", (0, 0, 0.21), 0.08, 0.04, n=8)
    for k, (x, z) in enumerate(((0.02, 0.04), (-0.03, 0.07), (0.0, 0.1), (0.03, 0.13))):
        p.cyl("crust", (x, 0, z), 0.035, 0.012, n=6)
    return p


# ===== Dairy ===================================================================================================
@item("dairy", "MilkCarton")
def milk_carton():
    p = Prop("FD_MilkCarton_01"); p.box("label_white", (0, 0, 0.1), (0.07, 0.07, 0.2)); p.box("label_blue", (0, -0.036, 0.09), (0.06, 0.004, 0.1))
    p.box("label_white", (0, 0, 0.23), (0.07, 0.07, 0.05), rot=(0, 0, 0), taper=0.4); return p


@item("dairy", "MilkBottle")
def milk_bottle():
    p = Prop("FD_MilkBottle_01"); lathe(p, "glass", [(0.0, 0.04), (0.14, 0.04), (0.18, 0.02), (0.22, 0.02)], n=8); lathe(p, "label_white", [(0.0, 0.037), (0.13, 0.037)], n=8)
    p.cyl("metal_galv", (0, 0, 0.225), 0.022, 0.01, n=6); return p


@item("dairy", "EggCarton")
def egg_carton():
    p = Prop("FD_EggCarton_01"); p.box("paper", (0, 0, 0.025), (0.26, 0.1, 0.05))
    for r in range(2):
        for c in range(6):
            ball(p, "label_white", (-0.108 + c * 0.0432, -0.025 + r * 0.05, 0.062), 0.019, n=6, squash=1.25, rings=3)
    return p


@item("dairy", "CheeseWedge")
def cheese():
    p = Prop("FD_CheeseWedge_01"); p.box("paint_yellow", (0, 0, 0.04), (0.12, 0.08, 0.08), taper=0.7)
    for x, z in ((-0.03, 0.03), (0.02, 0.05)):
        p.box("golden", (x, -0.042, z), (0.015, 0.004, 0.015))
    return p


@item("dairy", "Butter")
def butter():
    p = Prop("FD_Butter_01"); p.box("paint_yellow", (0, 0, 0.025), (0.1, 0.05, 0.05)); p.box("paint_white", (0, 0, 0.055), (0.1, 0.05, 0.008)); return p


@item("dairy", "JuiceBox")
def juice_box():
    p = Prop("FD_JuiceBox_01"); p.box("food_orange", (0, 0, 0.055), (0.06, 0.04, 0.11)); p.box("label_white", (0, -0.021, 0.055), (0.04, 0.003, 0.05)); p.box("metal_galv", (0.015, 0, 0.115), (0.004, 0.004, 0.03)); return p


# ===== Drinks ==================================================================================================
def _can(p, label, h=0.12, r=0.033):
    p.cyl("metal_galv", (0, 0, h / 2), r, h, n=8); p.cyl(label, (0, 0, h / 2), r + 0.001, h * 0.6, n=8); p.cyl("metal_dark", (0, 0, h + 0.002), r * 0.8, 0.004, n=8)


@item("drinks", "SodaCan_Red")
def soda_red():
    p = Prop("FD_SodaCan_Red_01"); _can(p, "label_red"); return p


@item("drinks", "SodaCan_Blue")
def soda_blue():
    p = Prop("FD_SodaCan_Blue_01"); _can(p, "label_blue"); return p


@item("drinks", "SodaCan_Green")
def soda_green():
    p = Prop("FD_SodaCan_Green_01"); _can(p, "plant_green"); return p


@item("drinks", "BeerCan")
def beer_can():
    p = Prop("FD_BeerCan_01"); _can(p, "paint_yellow", h=0.15, r=0.033); return p


@item("drinks", "BeerBottle")
def beer_bottle():
    p = Prop("FD_BeerBottle_01"); lathe(p, "glass_brown", [(0.0, 0.032), (0.14, 0.032), (0.19, 0.016), (0.25, 0.014)], n=8)
    lathe(p, "label_white", [(0.04, 0.0335), (0.11, 0.0335)], n=8); p.cyl("metal_galv", (0, 0, 0.253), 0.017, 0.008, n=6); return p


@item("drinks", "WaterBottle")
def water_bottle():
    p = Prop("FD_WaterBottle_01"); lathe(p, "glass", [(0.0, 0.034), (0.16, 0.034), (0.2, 0.016), (0.22, 0.015)], n=8)
    lathe(p, "label_blue", [(0.08, 0.0355), (0.14, 0.0355)], n=8); p.cyl("label_blue", (0, 0, 0.226), 0.017, 0.012, n=6); return p


@item("drinks", "WineBottle")
def wine_bottle():
    p = Prop("FD_WineBottle_01"); lathe(p, "glass_green", [(0.0, 0.04), (0.2, 0.04), (0.27, 0.014), (0.33, 0.013)], n=8)
    lathe(p, "paper", [(0.04, 0.0415), (0.16, 0.0415)], n=8); p.cyl("cloth_red", (0, 0, 0.332), 0.016, 0.03, n=6); return p


@item("drinks", "WhiskeyBottle")
def whiskey_bottle():
    p = Prop("FD_WhiskeyBottle_01"); lathe(p, "golden", [(0.0, 0.045), (0.16, 0.045), (0.21, 0.02), (0.25, 0.019)], n=8)
    lathe(p, "label_white", [(0.05, 0.0465), (0.13, 0.0465)], n=8); p.cyl("black", (0, 0, 0.255), 0.022, 0.03, n=6); return p


@item("drinks", "CoffeeCan")
def coffee_can():
    p = Prop("FD_CoffeeCan_01"); p.cyl("cloth_red", (0, 0, 0.1), 0.075, 0.2, n=10); p.cyl("label_white", (0, 0, 0.1), 0.0765, 0.08, n=10); p.cyl("black", (0, 0, 0.205), 0.07, 0.012, n=10); return p


# ===== Canned and boxed goods ==================================================================================
@item("canned", "Can_Soup")
def can_soup():
    p = Prop("FD_Can_Soup_01"); _can(p, "label_red", h=0.1, r=0.04); return p


@item("canned", "Can_Beans")
def can_beans():
    p = Prop("FD_Can_Beans_01"); _can(p, "tan", h=0.11, r=0.04); return p


@item("canned", "Jar_Pickles")
def jar_pickles():
    p = Prop("FD_Jar_Pickles_01"); p.cyl("glass", (0, 0, 0.09), 0.05, 0.18, n=8); p.cyl("plant_green", (0, 0, 0.08), 0.04, 0.13, n=6); p.cyl("metal_galv", (0, 0, 0.19), 0.052, 0.025, n=8); return p


@item("canned", "Jar_Jam")
def jar_jam():
    p = Prop("FD_Jar_Jam_01"); p.cyl("glass", (0, 0, 0.055), 0.04, 0.11, n=8); p.cyl("roof_red", (0, 0, 0.05), 0.037, 0.08, n=8); p.cyl("cloth_red", (0, 0, 0.115), 0.042, 0.02, n=8); return p


@item("canned", "Ketchup")
def ketchup():
    p = Prop("FD_Ketchup_01"); lathe(p, "cloth_red", [(0.0, 0.035), (0.14, 0.035), (0.18, 0.015), (0.19, 0.012)], n=8); p.cyl("label_white", (0, 0, 0.195), 0.018, 0.02, n=6); return p


@item("canned", "Mustard")
def mustard():
    p = Prop("FD_Mustard_01"); lathe(p, "paint_yellow", [(0.0, 0.03), (0.12, 0.03), (0.15, 0.012), (0.16, 0.01)], n=8); p.cyl("cloth_red", (0, 0, 0.165), 0.014, 0.02, n=6); return p


@item("canned", "PeanutButter")
def peanut_butter():
    p = Prop("FD_PeanutButter_01"); p.cyl("tan", (0, 0, 0.07), 0.045, 0.14, n=8); p.cyl("cloth_red", (0, 0, 0.145), 0.047, 0.02, n=8); p.cyl("label_white", (0, 0, 0.07), 0.0465, 0.07, n=8); return p


@item("boxed", "CerealBox")
def cereal_box():
    p = Prop("FD_CerealBox_01"); p.box("food_orange", (0, 0, 0.15), (0.2, 0.07, 0.3)); p.box("paint_yellow", (0, -0.036, 0.15), (0.16, 0.004, 0.2)); p.box("label_blue", (0, -0.038, 0.2), (0.08, 0.004, 0.06)); return p


@item("boxed", "PastaBox")
def pasta_box():
    p = Prop("FD_PastaBox_01"); p.box("label_blue", (0, 0, 0.12), (0.1, 0.04, 0.24)); p.box("glass", (0, -0.021, 0.12), (0.05, 0.003, 0.12)); p.box("dough", (0, -0.023, 0.12), (0.04, 0.002, 0.1)); return p


@item("boxed", "CrackerBox")
def cracker_box():
    p = Prop("FD_CrackerBox_01"); p.box("cloth_red", (0, 0, 0.1), (0.16, 0.05, 0.2)); p.box("crust", (0, -0.026, 0.1), (0.12, 0.003, 0.1)); return p


@item("boxed", "FlourSack")
def flour_sack():
    p = Prop("FD_FlourSack_01"); p.box("label_white", (0, 0, 0.15), (0.26, 0.12, 0.3), taper=0.9); p.box("label_white", (0, 0, 0.31), (0.2, 0.1, 0.04), taper=0.6)
    p.box("label_blue", (0, -0.062, 0.16), (0.16, 0.004, 0.12)); return p


@item("boxed", "SugarBag")
def sugar_bag():
    p = Prop("FD_SugarBag_01"); p.box("paint_white", (0, 0, 0.12), (0.12, 0.06, 0.24), taper=0.95); p.box("label_blue", (0, -0.031, 0.12), (0.08, 0.004, 0.1)); return p


@item("boxed", "ChipsBag")
def chips_bag():
    p = Prop("FD_ChipsBag_01"); p.box("paint_yellow", (0, 0, 0.13), (0.2, 0.05, 0.26), taper=0.95); p.box("cloth_red", (0, -0.026, 0.13), (0.14, 0.004, 0.12)); p.box("paint_yellow", (0, 0, 0.27), (0.2, 0.03, 0.02)); return p


@item("boxed", "CandyBar")
def candy_bar():
    p = Prop("FD_CandyBar_01"); p.box("fabric_brown", (0, 0, 0.01), (0.14, 0.04, 0.02)); p.box("cloth_red", (0, -0.0, 0.021), (0.14, 0.04, 0.004)); return p


# ===== Prepared food and meat ==================================================================================
@item("prepared", "Steak")
def steak():
    p = Prop("FD_Steak_01"); p.box("paint_white", (0, 0, 0.012), (0.18, 0.12, 0.024)); p.box("meat_red", (0, 0, 0.034), (0.15, 0.09, 0.03), taper=0.8); p.box("paint_white", (0.05, 0.0, 0.05), (0.04, 0.03, 0.01)); return p


@item("prepared", "Sausages")
def sausages():
    p = Prop("FD_Sausages_01")
    for k in range(4):
        p.cyl("meat_red", (0, -0.03 + k * 0.02, 0.02), 0.012, 0.16, n=6, axis="x")
    p.box("paint_white", (0, 0, 0.004), (0.2, 0.1, 0.008)); return p


@item("prepared", "Drumstick")
def drumstick():
    p = Prop("FD_Drumstick_01"); ball(p, "crust", (0, 0, 0.04), 0.04, n=6, squash=0.9); p.cyl("paint_white", (0.07, 0, 0.045), 0.009, 0.08, n=4, axis="x"); return p


@item("prepared", "TurkeyRoast")
def turkey_roast():
    p = Prop("FD_TurkeyRoast_01"); ball(p, "crust", (0, 0, 0.1), 0.15, n=8, squash=0.65)
    for s in (-1, 1):
        p.cyl("crust", (s * 0.12, -0.12, 0.08), 0.04, 0.1, n=6, axis="y"); p.cyl("paint_white", (s * 0.12, -0.18, 0.08), 0.01, 0.04, n=4, axis="y")
    p.cyl("metal_galv", (0, 0, 0.005), 0.22, 0.01, n=10); return p


@item("prepared", "Fish")
def fish():
    p = Prop("FD_Fish_01"); p.box("fabric_grey", (0, 0, 0.04), (0.34, 0.08, 0.08), taper=0.8); p.box("paint_white", (0, 0, 0.012), (0.34, 0.06, 0.02)); p.box("fabric_grey", (0.2, 0, 0.04), (0.08, 0.01, 0.12), rot=(0, 25, 0)); p.box("black", (-0.13, -0.041, 0.055), (0.012, 0.004, 0.012)); return p


@item("prepared", "Hamburger")
def hamburger():
    p = Prop("FD_Hamburger_01"); p.cyl("crust", (0, 0, 0.012), 0.05, 0.024, n=8); p.cyl("fabric_brown", (0, 0, 0.032), 0.05, 0.016, n=8); p.cyl("plant_green", (0, 0, 0.044), 0.054, 0.006, n=8)
    p.cyl("paint_yellow", (0, 0, 0.05), 0.05, 0.004, n=8); ball(p, "crust", (0, 0, 0.052), 0.05, n=8, squash=0.55, rings=3); return p


@item("prepared", "HotDog")
def hot_dog():
    p = Prop("FD_HotDog_01"); p.box("dough", (0, 0, 0.02), (0.16, 0.04, 0.04)); p.cyl("meat_red", (0, 0, 0.032), 0.012, 0.17, n=6, axis="x"); p.box("paint_yellow", (0, 0, 0.046), (0.14, 0.008, 0.004)); return p


@item("prepared", "PizzaBox")
def pizza_box():
    p = Prop("FD_PizzaBox_01"); p.box("fabric_brown", (0, 0, 0.02), (0.36, 0.36, 0.04)); p.box("cloth_red", (0, -0.181, 0.02), (0.12, 0.004, 0.02)); return p


@item("prepared", "Sandwich")
def sandwich():
    p = Prop("FD_Sandwich_01"); p.box("dough", (0, 0, 0.012), (0.12, 0.1, 0.024), taper=0.9); p.box("plant_green", (0, 0, 0.03), (0.12, 0.1, 0.01)); p.box("meat_red", (0, 0, 0.038), (0.11, 0.09, 0.01)); p.box("dough", (0, 0, 0.052), (0.12, 0.1, 0.022), taper=0.9); return p


@item("prepared", "TVDinner")
def tv_dinner():
    p = Prop("FD_TVDinner_01"); p.box("label_blue", (0, 0, 0.015), (0.2, 0.16, 0.03)); p.box("metal_galv", (0, 0, 0.031), (0.18, 0.14, 0.004))
    for x in (-0.05, 0.05):
        p.box("food_orange" if x < 0 else "plant_green", (x, 0.0, 0.034), (0.07, 0.1, 0.006))
    return p


# ===== Pet food and treats (GN-82) =============================================================================
@item("pet", "DogBone")
def dog_bone():
    p = Prop("FD_DogBone_01"); p.box("label_white", (0, 0, 0.02), (0.14, 0.026, 0.026))
    for sx in (-1, 1):
        for sy in (-1, 1):
            ball(p, "label_white", (sx * 0.072, sy * 0.016, 0.02), 0.016, n=5, rings=3)
    return p


@item("pet", "CatFoodTin")
def cat_food_tin():
    p = Prop("FD_CatFoodTin_01"); _can(p, "fabric_pink", h=0.035, r=0.04); return p


@item("pet", "HayFlake")
def hay_flake():
    p = Prop("FD_HayFlake_01"); p.box("hay", (0, 0, 0.06), (0.4, 0.2, 0.12)); p.box("wood_dark", (0.1, 0, 0.06), (0.012, 0.21, 0.125)); return p


@item("pet", "SeedBag")
def seed_bag():
    p = Prop("FD_SeedBag_01"); p.box("tan", (0, 0, 0.1), (0.16, 0.07, 0.2), taper=0.95); p.box("plant_green", (0, -0.036, 0.1), (0.1, 0.004, 0.08)); return p


# ===== Clothes (for wardrobes and laundry) =====================================================================
def _hanger(p, z):
    p.box("wood_light", (0, 0, z + 0.02), (0.4, 0.012, 0.012), rot=(0, 18, 0)); p.cyl("metal_galv", (0, 0, z + 0.05), 0.004, 0.04, n=4)


@item("clothes", "Shirt_Hanger")
def shirt_hanger():
    p = Prop("FD_Shirt_Hanger_01"); _hanger(p, 0.6)
    p.box("denim", (0, 0, 0.3), (0.44, 0.04, 0.62), taper=0.85)
    for s in (-1, 1):
        p.box("denim", (s * 0.26, 0, 0.5), (0.1, 0.04, 0.3), rot=(0, s * 20, 0))
    return p


@item("clothes", "Jacket_Hanger")
def jacket_hanger():
    p = Prop("FD_Jacket_Hanger_01"); _hanger(p, 0.7)
    p.box("fabric_brown", (0, 0, 0.34), (0.5, 0.07, 0.7), taper=0.9)
    for s in (-1, 1):
        p.box("fabric_brown", (s * 0.29, 0, 0.45), (0.12, 0.07, 0.5), rot=(0, s * 8, 0))
    p.box("black", (0, -0.04, 0.4), (0.012, 0.004, 0.5))
    return p


@item("clothes", "Dress_Hanger")
def dress_hanger():
    p = Prop("FD_Dress_Hanger_01"); _hanger(p, 0.95)
    p.box("cloth_red", (0, 0, 0.7), (0.32, 0.04, 0.5), taper=1.1); p.box("cloth_red", (0, 0, 0.35), (0.5, 0.05, 0.7), taper=0.62, rot=(180, 0, 0)); return p


@item("clothes", "Pants_Folded")
def pants_folded():
    p = Prop("FD_Pants_Folded_01")
    for k, c in enumerate(("denim", "rust_dark", "grey_suit")):
        p.box(c, (0, 0, 0.03 + k * 0.06), (0.34, 0.26, 0.055))
    return p


@item("clothes", "Towel_Folded")
def towel_folded():
    p = Prop("FD_Towel_Folded_01")
    for k, c in enumerate(("linen", "fabric_blue", "paint_white")):
        p.box(c, (0, 0, 0.04 + k * 0.08), (0.36, 0.24, 0.07))
    return p


@item("clothes", "Shoes_Pair")
def shoes_pair():
    p = Prop("FD_Shoes_Pair_01")
    for s in (-1, 1):
        p.box("black", (s * 0.06, 0.0, 0.04), (0.09, 0.26, 0.08), taper=0.9); p.box("rubber", (s * 0.06, 0, 0.01), (0.095, 0.27, 0.02)); p.box("paint_white", (s * 0.06, 0.04, 0.085), (0.06, 0.1, 0.006))
    return p


@item("clothes", "Scarf")
def scarf():
    p = Prop("FD_Scarf_01"); p.box("cloth_red", (0, 0, 0.02), (0.6, 0.1, 0.03)); p.box("paint_yellow", (0.1, 0, 0.037), (0.04, 0.1, 0.004)); p.box("paint_yellow", (-0.1, 0, 0.037), (0.04, 0.1, 0.004)); return p


ROTTEN = {"cloth_red": "mould", "paint_yellow": "fabric_brown", "plant_green": "mould", "food_orange": "mould", "corn_leaf": "dead_wood", "corn_cob": "fabric_brown",
          "crust": "dead_wood", "dough": "fabric_brown", "meat_red": "mould", "paint_white": "dead_wood", "label_white": "wood_grey", "tan": "dead_wood",
          "golden": "dead_wood", "siding_green": "mould", "fabric_pink": "dead_wood", "leaf_dark": "mould", "hay": "dead_wood", "fabric_grey": "mould"}
FRESH_GROUPS = ("produce", "bakery", "dairy", "prepared")


def run():
    names = globals().get("CONTENT_LIST")
    count, x, y, row = 0, 0.0, 0.0, None
    for key, (fn, group) in ITEMS.items():
        if names and key not in names and group not in names:
            continue
        folder = "Clothes" if group == "clothes" else "Food"
        if group != row:
            row, x, y = group, 0.0, (y + 1.2 if row is not None else 0.0)
        for rotten in ([False, True] if group in FRESH_GROUPS else [False]):
            props_lib.THEME = ROTTEN if rotten else {}
            try:
                prop = fn()
            finally:
                props_lib.THEME = {}
            if rotten:
                prop.name = prop.name[:-3] + "_Rotten_01"
            obj, coll = prop.finish()
            sub = "" if group == "clothes" else f"{group.title()}/"
            common.export_fbx(coll, f"Assets/Art/Global/{folder}/{sub}{prop.name}.fbx")
            obj.location = (x, y + (0.6 if rotten else 0.0), 0)
            count += 1
        x += max(0.3, obj.dimensions.x + 0.1)
    print("contents done", count)


if __name__ == "__main__":
    run()
