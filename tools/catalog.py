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


# ===== How the browser describes each model =====================================================================
# id -> name, type (ONE primary category path), tags (space separated: the setting, colour, condition, and whatever helps a search),
# group (models in one group are variants of each other: the same model in another skin, style or colour).
ASSETS = {}


def _a(id, name, type, tags, group=None):
    ASSETS[id] = dict(name=name, type=type, tags=tags.split(), group=group)


# vehicles
_a("GV_Sedan_Blue_01", "Sedan, blue", "vehicles/road/sedan", "modern urban suburban car blue new civilian", "sedan")
_a("GV_Sedan_Red_01", "Sedan, red", "vehicles/road/sedan", "modern urban suburban car red new civilian", "sedan")
_a("GV_Sedan_Red_Damaged_01", "Sedan, red, wrecked", "vehicles/road/sedan", "modern urban suburban car red damaged wreck rusty abandoned", "sedan")
_a("GV_Taxi_Yellow_01", "Taxi", "vehicles/road/taxi", "modern urban car yellow new cab service")
_a("GV_Van_Brown_01", "Delivery van", "vehicles/road/van", "modern urban brown new delivery service")
_a("GV_Police_Sheriff_01", "Sheriff's cruiser", "vehicles/road/police", "rural law enforcement car white new emergency sheriff")
_a("GV_Ambulance_White_01", "Ambulance", "vehicles/road/ambulance", "modern urban white new emergency medical van")
_a("GV_Motorcycle_Red_01", "Motorcycle", "vehicles/road/motorcycle", "modern red new bike two-wheeler")
_a("GV_Tractor_Green_01", "Tractor, green", "vehicles/farm/tractor", "rural farm green new machine", "tractor")
_a("GV_Tractor_Red_01", "Tractor, red", "vehicles/farm/tractor", "rural farm red new machine", "tractor")
_a("GV_Pickup_Blue_01", "Farm pickup, blue", "vehicles/farm/pickup", "rural farm truck blue new")
_a("SH_Scout_01", "Scout ship", "vehicles/ship/scout", "sci-fi alien ship flying saucer ufo violet glow new")
_a("SH_Dart_01", "Dart ship", "vehicles/ship/dart", "sci-fi alien ship flyer fast glow new")
# animals
_a("GN_Cow_faceted_01", "Cow", "animals/farm/cow", "rural farm livestock black white animal quadruped")
_a("GN_Horse_faceted_01", "Horse", "animals/farm/horse", "rural farm livestock brown animal quadruped")
_a("GN_ChickenHen_faceted_01", "Hen", "animals/farm/hen", "rural farm poultry bird chicken animal")
_a("GN_DogCollie_faceted_01", "Dog, collie", "animals/pet/dog", "rural farm pet dog animal quadruped collie")
_a("GN_DogHusky_faceted_01", "Dog, husky", "animals/pet/dog", "pet dog animal quadruped husky grey white")
_a("GN_CatTabby_faceted_01", "Cat, tabby", "animals/pet/cat", "pet cat animal quadruped tabby")
# people
_a("GP_Farmer_01", "Farmer", "people/civilian/farmer", "rural farm adult man cap beard flannel human")
_a("GP_FarmerKid_01", "Farmer's kid", "people/civilian/kid", "rural farm child kid human")
_a("GP_Waitress_01", "Waitress", "people/civilian/waitress", "diner retro adult woman red human")
_a("GP_Sheriff_01", "Sheriff", "people/law/sheriff", "rural law enforcement adult uniform tan hat human")
_a("GP_Grey_01", "Grey alien", "people/alien/grey", "sci-fi alien grey humanoid")
# appliances and storage that open
_a("GI_Fridge_01", "Fridge, classic", "appliances/kitchen/fridge", "classic kitchen white new cold", "fridge")
_a("GI_Fridge_Modern_01", "Fridge, modern", "appliances/kitchen/fridge", "modern kitchen steel new cold", "fridge")
_a("GI_Fridge_Retro_01", "Fridge, retro", "appliances/kitchen/fridge", "retro kitchen cream rounded new cold", "fridge")
_a("GI_Fridge_Damaged_01", "Fridge, rusty", "appliances/kitchen/fridge", "kitchen rusty damaged abandoned cold", "fridge")
_a("GI_Microwave_01", "Microwave", "appliances/kitchen/microwave", "classic kitchen new")
_a("GI_Wardrobe_01", "Wardrobe", "furniture/storage/wardrobe", "classic bedroom wood new", "wardrobe")
_a("GI_Wardrobe_Damaged_01", "Wardrobe, ruined", "furniture/storage/wardrobe", "bedroom wood damaged abandoned", "wardrobe")
_a("GI_Dresser_01", "Dresser", "furniture/storage/dresser", "classic bedroom wood new drawers")
_a("GI_Chest_01", "Chest", "furniture/storage/chest", "classic wood new lid trunk")
_a("GI_Locker_01", "Locker", "furniture/storage/locker", "classic metal new school gym")
_a("GI_Toolbox_01", "Toolbox", "farm/tools/toolbox", "rural workshop red metal new lid")
_a("GI_Mailbox_01", "Mailbox", "farm/structures/mailbox", "rural outdoor post new flap")
# furniture and decor in their styles
_a("GH_Sofa_Modern_01", "Sofa, modern", "furniture/seating/sofa", "modern living-room grey new", "sofa")
_a("GH_Sofa_Retro_01", "Sofa, retro", "furniture/seating/sofa", "retro living-room tufted new", "sofa")
_a("GH_Sofa_Damaged_01", "Sofa, slashed", "furniture/seating/sofa", "living-room damaged abandoned", "sofa")
_a("GH_Armchair_Retro_01", "Armchair, retro", "furniture/seating/armchair", "retro living-room new")
_a("GH_Bed_Double_Modern_01", "Double bed, modern", "furniture/bedroom/bed", "modern bedroom new")
_a("GH_Bookcase_Modern_01", "Bookcase, modern", "furniture/storage/bookcase", "modern living-room shelves books new")
_a("GD_TV_Flat_Modern_01", "Flat-screen TV", "decor/electronics/tv", "modern living-room screen electronics new")
_a("GD_TableLamp_Retro_01", "Table lamp, retro", "decor/lighting/lamp", "retro lamp light new")
_a("GD_NeonSign_01", "Neon sign", "decor/lighting/neon-sign", "retro diner glow light red cyan new")
_a("GD_Clock_Wall_Retro_01", "Wall clock, retro", "decor/wall/clock", "retro wall time new")
_a("GD_PottedPlant_01", "Potted plant", "decor/plants/potted-plant", "plant green terracotta new")
# food
_a("FD_Apple_01", "Apple", "food/produce/apple", "fruit red fresh", "apple")
_a("FD_Apple_Rotten_01", "Apple, rotten", "food/produce/apple", "fruit rotten mould spoiled", "apple")
_a("FD_BreadLoaf_01", "Loaf of bread", "food/bakery/bread", "baked fresh brown")
_a("FD_Pie_01", "Pie", "food/bakery/pie", "baked dessert fresh")
_a("FD_Hamburger_01", "Hamburger", "food/prepared/hamburger", "fast-food diner fresh")
# farm
_a("GT_Barrel_01", "Barrel", "farm/props/barrel", "rural wood container new")
_a("GT_Wheelbarrow_01", "Wheelbarrow", "farm/tools/wheelbarrow", "rural tool new")
_a("GT_HayBale_Round_01", "Round hay bale", "farm/props/hay-bale", "rural hay yellow new")
_a("FM_Scarecrow_01", "Scarecrow", "farm/props/scarecrow", "rural field straw")
_a("FM_DogHouse_01", "Doghouse", "farm/structures/doghouse", "rural wood new")
# building kit and nature
_a("GK_Wall_Window_Clapboard_01", "Window wall, clapboard", "building/kit/wall-window", "rural white siding new modular", "wall-window")
_a("GK_Wall_Window_Brick_01", "Window wall, brick", "building/kit/wall-window", "urban brick red new modular", "wall-window")
_a("GK_Wall_Window_Barn_01", "Window wall, barn", "building/kit/wall-window", "rural barn red new modular", "wall-window")
_a("GK_Door_Exterior_01", "Exterior door", "building/kit/door", "classic wood new modular")
_a("FM_TreeOak_01", "Oak tree", "nature/trees/oak", "rural tree green plant big")
_a("FM_TreePine_01", "Pine tree", "nature/trees/pine", "rural tree green plant conifer")
