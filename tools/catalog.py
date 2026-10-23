"""What the first slice of the asset browser contains: how each model is built (BUILD) and how the browser describes it (ASSETS).

Plain data, no Blender: tools/build_site_assets.py (in Blender) reads BUILD, tools/make_manifest.py reads ASSETS.
"""

# ===== How to build ==============================================================================================
# kind "static": run the art script `script` with `globals`, keep the models in `ids`.
# kind "people" / "animals": one model at a time, then its clips; the dict maps the art script's key to the model id.
BUILD = {
    "cars_sedan": dict(script="cars.py", globals={"CAR_LIST": ["Sedan"], "VARIANT_LIST": ["Blue", "Red"]},
                       ids=["GV_Sedan_Blue_01", "GV_Sedan_Red_01", "GV_Sedan_Red_Damaged_01"]),
    "cars_taxi": dict(script="cars.py", globals={"CAR_LIST": ["Taxi"], "VARIANT_LIST": ["Yellow"], "CONDITIONS": ["New"]}, ids=["GV_Taxi_Yellow_01"]),
    "cars_van": dict(script="cars.py", globals={"CAR_LIST": ["Van"], "VARIANT_LIST": ["Brown"], "CONDITIONS": ["New"]}, ids=["GV_Van_Brown_01"]),
    "cars_police": dict(script="cars.py", globals={"CAR_LIST": ["Police"], "VARIANT_LIST": ["Sheriff"], "CONDITIONS": ["New"]}, ids=["GV_Police_Sheriff_01"]),
    "cars_ambulance": dict(script="cars.py", globals={"CAR_LIST": ["Ambulance"], "CONDITIONS": ["New"]}, ids=["GV_Ambulance_White_01"]),
    "cars_moto": dict(script="cars.py", globals={"CAR_LIST": ["Motorcycle"], "VARIANT_LIST": ["Red"], "CONDITIONS": ["New"]}, ids=["GV_Motorcycle_Red_01"]),
    "cars_tractor": dict(script="cars.py", globals={"CAR_LIST": ["Tractor"], "VARIANT_LIST": ["Green", "Red"], "CONDITIONS": ["New"]},
                         ids=["GV_Tractor_Green_01", "GV_Tractor_Red_01"]),
    "cars_pickup": dict(script="cars.py", globals={"CAR_LIST": ["Pickup"], "VARIANT_LIST": ["Blue"], "CONDITIONS": ["New"]}, ids=["GV_Pickup_Blue_01"]),
    "ships": dict(script="ships.py", globals={"SHIP_LIST": ["Scout", "Dart"]}, ids=["SH_Scout_01", "SH_Dart_01"]),
    "int_fridge": dict(script="interactive.py", globals={"INTERACTIVE_LIST": ["Fridge"]},
                       ids=["GI_Fridge_01", "GI_Fridge_Modern_01", "GI_Fridge_Retro_01", "GI_Fridge_Damaged_01"]),
    "int_wardrobe": dict(script="interactive.py", globals={"INTERACTIVE_LIST": ["Wardrobe"], "STYLE_LIST": ["Classic", "Damaged"]},
                         ids=["GI_Wardrobe_01", "GI_Wardrobe_Damaged_01"]),
    "int_dresser": dict(script="interactive.py", globals={"INTERACTIVE_LIST": ["Dresser", "Toolbox", "Microwave", "Chest", "Mailbox", "Locker"], "STYLE_LIST": ["Classic"]},
                        ids=["GI_Dresser_01", "GI_Toolbox_01", "GI_Microwave_01", "GI_Chest_01", "GI_Mailbox_01", "GI_Locker_01"]),
    "home_sofa": dict(script="home_styles.py", globals={"STYLE_PIECES": ["Sofa", "Armchair", "Bookcase", "Bed_Double"]},
                      ids=["GH_Sofa_Modern_01", "GH_Sofa_Retro_01", "GH_Sofa_Damaged_01", "GH_Armchair_Retro_01", "GH_Bookcase_Modern_01", "GH_Bed_Double_Modern_01"]),
    "home_misc": dict(script="home_styles.py", globals={"STYLE_PIECES": ["TV_Flat", "TableLamp", "Clock_Wall"]},
                      ids=["GD_TV_Flat_Modern_01", "GD_TableLamp_Retro_01", "GD_Clock_Wall_Retro_01"]),
    "decor": dict(script="decor.py", globals={"DECOR_LIST": ["PottedPlant", "NeonSign"]}, ids=["GD_PottedPlant_01", "GD_NeonSign_01"]),
    "food": dict(script="contents.py", globals={"CONTENT_LIST": ["Apple", "BreadLoaf", "Pie", "Hamburger"]},
                 ids=["FD_Apple_01", "FD_Apple_Rotten_01", "FD_BreadLoaf_01", "FD_Pie_01", "FD_Hamburger_01"]),
    "farm": dict(script="props_farm.py", globals={"PROP_LIST": ["barrel", "wheelbarrow", "scarecrow", "hay_round", "doghouse"]},
                 ids=["GT_Barrel_01", "GT_Wheelbarrow_01", "FM_Scarecrow_01", "GT_HayBale_Round_01", "FM_DogHouse_01"]),
    "kit": dict(script="kit.py", globals={"KIT_LIST": ["Wall_Window"], "SKIN_LIST": ["Brick", "Clapboard", "Barn"]},
                ids=["GK_Wall_Window_Brick_01", "GK_Wall_Window_Clapboard_01", "GK_Wall_Window_Barn_01"]),
    "kit_door": dict(script="kit.py", globals={"KIT_LIST": ["Door_Exterior"]}, ids=["GK_Door_Exterior_01"]),
    "veg": dict(script="vegetation.py", globals={"VEG_LIST": ["oak", "pine"]}, ids=["FM_TreeOak_01", "FM_TreePine_01"]),
    "people": dict(kind="people", clips=["Idle", "Walk", "Run", "Sit"],
                   people={"farmer": "GP_Farmer_01", "sheriff": "GP_Sheriff_01", "farmer_kid": "GP_FarmerKid_01", "waitress": "GP_Waitress_01", "grey": "GP_Grey_01"}),
    "animals": dict(kind="animals", clips=["Idle", "Walk"], dog_clips=["Trot", "Run"],
                    animals={"cow": "GN_Cow_faceted_01", "horse": "GN_Horse_faceted_01", "dog_collie": "GN_DogCollie_faceted_01",
                             "dog_husky": "GN_DogHusky_faceted_01", "cat_tabby": "GN_CatTabby_faceted_01"}),
    "birds": dict(kind="animals", birds=True, clips=[], animals={"chicken_hen": "GN_ChickenHen_faceted_01"}),
}
