"""What the first slice of the asset browser contains: how each model is built (BUILD) and how the browser describes it (ASSETS).

Plain data, no Blender: tools/build_site_assets.py (in Blender) reads BUILD, tools/make_manifest.py reads ASSETS.
"""

CARS_PY = "cars.py"
SHIPS_PY = "ships.py"
INTERACTIVE_PY = "interactive.py"
CONTENTS_PY = "contents.py"
BUILDINGS_PY = "buildings.py"
SPORTS_PY = "sports.py"
OFFICE_PY = "office.py"
INSECT_BROWN_TAGS = "wild garden insect bug brown tiny"
CUBICLE_PANEL = "furniture/cubicle/panel"
FRIDGE = "appliances/kitchen/fridge"
SOFA = "furniture/seating/sofa"


# ===== Ids ===========================================================================================================
# The generators (art/scripts) name a model after its paint as built: GV_Tractor_Green_01. In the browser a colour is a paint, so a model whose colour is only
# a paint has an id without it. SITE_IDS maps the generator's name to the browser's (BUILD keeps the generator's names; ASSETS, PAINTS and the files in site/
# use the browser's, tools/rename_glb.py moves a build into place); the old ids stay as `aliases` in the manifest, so old links and downloads still resolve.
SITE_IDS = {
    "GV_Sedan_Blue_01": "GV_Sedan_01", "GV_Sedan_Red_Damaged_01": "GV_Sedan_Damaged_01", "GV_Van_Brown_01": "GV_Van_01", "GV_Motorcycle_Red_01": "GV_Motorcycle_01",
    "GV_Tractor_Green_01": "GV_Tractor_01", "GV_Pickup_Blue_01": "GV_Pickup_01", "GN_Butterfly_Blue_01": "GN_Butterfly_01", "FD_Grapes_Green_01": "FD_Grapes_01",
    "FM_Farmhouse_White_01": "FM_Farmhouse_01",
    "FM_Farmhouse_White_Damaged_01": "FM_Farmhouse_Damaged_01",
    "FM_Barn_Red_01": "FM_Barn_01",
    "FM_Barn_Red_Damaged_01": "FM_Barn_Damaged_01",
    "FM_Workshop_Metal_01": "FM_Workshop_01",
    "FM_Workshop_Metal_Damaged_01": "FM_Workshop_Damaged_01",
    "FM_Shed_Weathered_01": "FM_Shed_01",
    "FM_Shed_Weathered_Damaged_01": "FM_Shed_Damaged_01",
    "FM_ChickenCoop_Red_01": "FM_ChickenCoop_01",
    "FM_Outhouse_Weathered_01": "FM_Outhouse_01",
    "FM_Well_Stone_01": "FM_Well_01",
    "FM_Silo_Metal_01": "FM_Silo_01",
    "FM_Windmill_White_01": "FM_Windmill_01",
    "GB_Trailer_Beige_01": "GB_Trailer_01",
    "GB_Trailer_Beige_Damaged_01": "GB_Trailer_Damaged_01",
    "GB_Garage_White_01": "GB_Garage_01",
    "GB_Garage_White_Damaged_01": "GB_Garage_Damaged_01",
    "GB_TownHouse_Brick_01": "GB_TownHouse_01",
    "GB_TownHouse_Brick_Damaged_01": "GB_TownHouse_Damaged_01",
    "GB_Diner_Cream_01": "GB_Diner_01",
    "GB_Diner_Cream_Damaged_01": "GB_Diner_Damaged_01",
}
ALIASES = {new: old for old, new in SITE_IDS.items()}        # browser id -> the id it had before


def site_id(generator_id):
    """The browser's id of a model the generator calls generator_id."""
    return SITE_IDS.get(generator_id, generator_id)


# ===== How to build ==============================================================================================
# kind "static": run the art script `script` with `globals`, keep the models in `ids`.
# kind "people" / "animals" / "critters": one model at a time, then its clips; the dict maps the art script's key to the model id.
BUILD = {
    "cars_sedan": {"script": CARS_PY, "globals": {"CAR_LIST": ["Sedan"], "VARIANT_LIST": ["Blue", "Red"]},
                       "ids": ["GV_Sedan_Blue_01", "GV_Sedan_Red_Damaged_01"]},
    "cars_taxi": {"script": CARS_PY, "globals": {"CAR_LIST": ["Taxi"], "VARIANT_LIST": ["Yellow"], "CONDITIONS": ["New"]}, "ids": ["GV_Taxi_Yellow_01"]},
    "cars_van": {"script": CARS_PY, "globals": {"CAR_LIST": ["Van"], "VARIANT_LIST": ["Brown"], "CONDITIONS": ["New"]}, "ids": ["GV_Van_Brown_01"]},
    "cars_police": {"script": CARS_PY, "globals": {"CAR_LIST": ["Police"], "VARIANT_LIST": ["Sheriff"], "CONDITIONS": ["New"]}, "ids": ["GV_Police_Sheriff_01"]},
    "cars_ambulance": {"script": CARS_PY, "globals": {"CAR_LIST": ["Ambulance"], "CONDITIONS": ["New"]}, "ids": ["GV_Ambulance_White_01"]},
    "cars_moto": {"script": CARS_PY, "globals": {"CAR_LIST": ["Motorcycle"], "VARIANT_LIST": ["Red"], "CONDITIONS": ["New"]}, "ids": ["GV_Motorcycle_Red_01"]},
    "cars_tractor": {"script": CARS_PY, "globals": {"CAR_LIST": ["Tractor"], "VARIANT_LIST": ["Green", "Red"], "CONDITIONS": ["New"]},
                         "ids": ["GV_Tractor_Green_01"]},
    "cars_pickup": {"script": CARS_PY, "globals": {"CAR_LIST": ["Pickup"], "VARIANT_LIST": ["Blue"], "CONDITIONS": ["New"]}, "ids": ["GV_Pickup_Blue_01"]},
    "ships": {"script": SHIPS_PY, "globals": {"SHIP_LIST": ["Scout", "Dart"]}, "ids": ["SH_Scout_01", "SH_Dart_01"]},
    "ship_parts": {"script": SHIPS_PY, "globals": {"SHIP_LIST": ["parts"]},
                       "ids": ["SH_PowerCell_01", "SH_HullPanel_01", "SH_NavCrystal_01", "SH_EngineCoil_01", "SH_ThrusterNozzle_01", "SH_FuelCanister_01", "SH_ShieldEmitter_01",
                            "SH_CommsArray_01", "SH_BlackBox_01", "SH_WarpRingSegment_01", "SH_LandingLeg_01", "SH_ConsoleModule_01", "SH_Beacon_01", "SH_SpecimenJar_01",
                            "SH_ContainmentPod_01"]},
    "ship_tools": {"script": SHIPS_PY, "globals": {"SHIP_LIST": ["tools", "debris"]},
                       "ids": ["SH_RepairTool_01", "SH_Scanner_01", "SH_Translator_01", "SH_HullShard_A_01", "SH_HullShard_B_01", "SH_CableTangle_01", "SH_ScorchedGround_01"]},
    "ships_more": {"script": SHIPS_PY, "globals": {"SHIP_LIST": ["Cigar", "Triangle", "EscapePod", "ProbeDrone", "DropShip", "MIBCraft", "Mothership"]},
                       "ids": ["SH_Cigar_01", "SH_Triangle_01", "SH_EscapePod_01", "SH_ProbeDrone_01", "SH_DropShip_01", "SH_MIBCraft_01", "SH_Mothership_01"]},
    "ship_ufo": {"script": "ufo.py", "ids": ["SH_AbductionUfo_01"]},
    "ship_saucer": {"script": "vehicles.py", "globals": {"VEHICLE_LIST": ["ship"]}, "ids": ["GV_CrashedShip_01"]},
    "ship_hulls": {"script": "ship_hulls.py", "ids": ["GV_ShipEgg_01", "GV_ShipFreighter_01"]},
    "ship_props": {"script": "ship_props.py", "ids": ["GV_ShipLockers_01", "GV_ShipPod_01", "GV_ShipJars_01", "GV_ShipConduit_01", "GV_ShipHoloTable_01", "GV_ShipCouch_01",
                                                    "GV_ShipToolRack_01", "GV_ShipSampleRack_01", "GV_ShipHelm_01", "GV_ShipNavScreen_01", "GV_ShipRadarPost_01",
                                                    "GV_ShipCrates_01", "GV_ShipDrums_01", "GV_ShipBunk_01", "GV_ShipMess_01"]},
    "ship_terminals": {"script": "terminals.py", "globals": {"STATE_LAMPS": False}, "ids": ["GV_ShipConsole_01", "GV_ShipTerminalBank_01", "GV_ShipTerminalLaunch_01"]},
    "int_fridge": {"script": INTERACTIVE_PY, "globals": {"INTERACTIVE_LIST": ["Fridge"]},
                       "ids": ["GI_Fridge_01", "GI_Fridge_Modern_01", "GI_Fridge_Retro_01", "GI_Fridge_Damaged_01"]},
    "int_fridge_dispenser": {"script": INTERACTIVE_PY, "globals": {"INTERACTIVE_LIST": ["FridgeDispenser"], "STYLE_LIST": ["Classic"]}, "ids": ["GI_Fridge_Dispenser_01"]},
    "int_wardrobe": {"script": INTERACTIVE_PY, "globals": {"INTERACTIVE_LIST": ["Wardrobe"], "STYLE_LIST": ["Classic", "Damaged"]},
                         "ids": ["GI_Wardrobe_01", "GI_Wardrobe_Damaged_01"]},
    "int_dresser": {"script": INTERACTIVE_PY, "globals": {"INTERACTIVE_LIST": ["Dresser", "Toolbox", "Microwave", "Chest", "Mailbox", "Locker"], "STYLE_LIST": ["Classic"]},
                        "ids": ["GI_Dresser_01", "GI_Toolbox_01", "GI_Microwave_01", "GI_Chest_01", "GI_Mailbox_01", "GI_Locker_01"]},
    "home_sofa": {"script": "home_styles.py", "globals": {"STYLE_PIECES": ["Sofa", "Armchair", "Bookcase", "Bed_Double"]},
                      "ids": ["GH_Sofa_Modern_01", "GH_Sofa_Retro_01", "GH_Sofa_Damaged_01", "GH_Armchair_Retro_01", "GH_Bookcase_Modern_01", "GH_Bed_Double_Modern_01"]},
    "home_misc": {"script": "home_styles.py", "globals": {"STYLE_PIECES": ["TV_Flat", "TableLamp", "Clock_Wall"]},
                      "ids": ["GD_TV_Flat_Modern_01", "GD_TableLamp_Retro_01", "GD_Clock_Wall_Retro_01"]},
    "decor": {"script": "decor.py", "globals": {"DECOR_LIST": ["PottedPlant", "NeonSign"]}, "ids": ["GD_PottedPlant_01", "GD_NeonSign_01"]},
    "food": {"script": CONTENTS_PY, "globals": {"CONTENT_LIST": ["Apple", "BreadLoaf", "Pie", "Hamburger"]},
                 "ids": ["FD_Apple_01", "FD_BreadLoaf_01", "FD_Pie_01", "FD_Hamburger_01"]},
    "food_produce2": {"script": CONTENTS_PY, "globals": {"CONTENT_LIST": ['Orange', 'Banana', 'Carrot', 'Tomato', 'Potato', 'Onion', 'Corn', 'Lettuce', 'Cabbage', 'Pumpkin', 'Watermelon'], "EXPORT": True}, "ids": ['FD_Orange_01', 'FD_Banana_01', 'FD_Carrot_01', 'FD_Tomato_01', 'FD_Potato_01', 'FD_Onion_01', 'FD_Corn_01', 'FD_Lettuce_01', 'FD_Cabbage_01', 'FD_Pumpkin_01', 'FD_Watermelon_01']},
    "food_bakery2": {"script": CONTENTS_PY, "globals": {"CONTENT_LIST": ['Baguette', 'Cake', 'Donut', 'CookieJar'], "EXPORT": True}, "ids": ['FD_Baguette_01', 'FD_Cake_01', 'FD_Donut_01', 'FD_CookieJar_01']},
    "food_dairy2": {"script": CONTENTS_PY, "globals": {"CONTENT_LIST": ['MilkCarton', 'MilkBottle', 'EggCarton', 'CheeseWedge', 'Butter', 'JuiceBox'], "EXPORT": True}, "ids": ['FD_MilkCarton_01', 'FD_MilkBottle_01', 'FD_EggCarton_01', 'FD_CheeseWedge_01', 'FD_Butter_01', 'FD_JuiceBox_01']},
    "food_prepared2": {"script": CONTENTS_PY, "globals": {"CONTENT_LIST": ['Steak', 'Sausages', 'Drumstick', 'TurkeyRoast', 'Fish', 'HotDog', 'PizzaBox', 'Sandwich', 'TVDinner'], "EXPORT": True}, "ids": ['FD_Steak_01', 'FD_Sausages_01', 'FD_Drumstick_01', 'FD_TurkeyRoast_01', 'FD_Fish_01', 'FD_HotDog_01', 'FD_PizzaBox_01', 'FD_Sandwich_01', 'FD_TVDinner_01']},
    "food_drinks": {"script": CONTENTS_PY, "globals": {"CONTENT_LIST": ['SodaCan_Red', 'BeerCan', 'BeerBottle', 'WaterBottle', 'WineBottle', 'WhiskeyBottle', 'CoffeeCan']}, "ids": ['FD_SodaCan_Red_01', 'FD_BeerCan_01', 'FD_BeerBottle_01', 'FD_WaterBottle_01', 'FD_WineBottle_01', 'FD_WhiskeyBottle_01', 'FD_CoffeeCan_01']},
    "food_canned": {"script": CONTENTS_PY, "globals": {"CONTENT_LIST": ['Can_Soup', 'Can_Beans', 'Jar_Pickles', 'Jar_Jam', 'Ketchup', 'Mustard', 'PeanutButter']}, "ids": ['FD_Can_Soup_01', 'FD_Can_Beans_01', 'FD_Jar_Pickles_01', 'FD_Jar_Jam_01', 'FD_Ketchup_01', 'FD_Mustard_01', 'FD_PeanutButter_01']},
    "food_boxed": {"script": CONTENTS_PY, "globals": {"CONTENT_LIST": ['CerealBox', 'PastaBox', 'CrackerBox', 'FlourSack', 'SugarBag', 'ChipsBag', 'CandyBar']}, "ids": ['FD_CerealBox_01', 'FD_PastaBox_01', 'FD_CrackerBox_01', 'FD_FlourSack_01', 'FD_SugarBag_01', 'FD_ChipsBag_01', 'FD_CandyBar_01']},
    "food_pet": {"script": CONTENTS_PY, "globals": {"CONTENT_LIST": ['DogBone', 'CatFoodTin', 'HayFlake', 'SeedBag']}, "ids": ['FD_DogBone_01', 'FD_CatFoodTin_01', 'FD_HayFlake_01', 'FD_SeedBag_01']},
    "food_clothes": {"script": CONTENTS_PY, "globals": {"CONTENT_LIST": ['Shirt_Hanger', 'Jacket_Hanger', 'Dress_Hanger', 'Pants_Folded', 'Towel_Folded', 'Shoes_Pair', 'Scarf']}, "ids": ['FD_Shirt_Hanger_01', 'FD_Jacket_Hanger_01', 'FD_Dress_Hanger_01', 'FD_Pants_Folded_01', 'FD_Towel_Folded_01', 'FD_Shoes_Pair_01', 'FD_Scarf_01']},
    "food_produce": {"script": CONTENTS_PY, "globals": {"CONTENT_LIST": ["Apple_Green", "Apple_Yellow", "BananaBunch", "Lemon", "Pear", "Grapes_Purple", "Grapes_Green", "Strawberry"]},
                         "ids": ["FD_BananaBunch_01", "FD_Lemon_01", "FD_Pear_01",
                              "FD_Grapes_Green_01", "FD_Strawberry_01"]},
    "farm": {"script": "props_farm.py", "globals": {"PROP_LIST": ["barrel", "wheelbarrow", "scarecrow", "hay_round", "doghouse"]},
                 "ids": ["GT_Barrel_01", "GT_Wheelbarrow_01", "FM_Scarecrow_01", "GT_HayBale_Round_01", "FM_DogHouse_01"]},
    "hand_tools": {"script": "hand_tools.py", "ids": ['GT_Hammer_01', 'GT_Sledgehammer_01', 'GT_Axe_01', 'GT_HandSaw_01', 'GT_Wrench_01', 'GT_Screwdriver_01', 'GT_Pliers_01', 'GT_Hoe_01', 'GT_Spade_01', 'GT_WateringCan_01']},
    "tools_more": {"script": "tools_more.py", "ids": ['GT_Plunger_01', 'GT_RopeCoil_01', 'GT_Sawhorse_01', 'GT_PaintCan_01', 'GT_PruningShears_01', 'GT_FirePoker_01', 'GT_HoseCoil_01', 'GT_Sprinkler_01', 'GT_CordReel_01', 'GT_HandTruck_01']},
    "tools_extra": {"script": "tools_extra.py", "ids": ['GT_Mallet_01', 'GT_ClothesIron_01', 'GT_BathroomScale_01', 'GT_CordlessDrill_01', 'GT_BenchVise_01', 'GT_SnowShovel_01', 'GT_CarBattery_01', 'GT_BootScraper_01', 'GT_ToiletBrush_01', 'GT_WorkLight_01']},
    "farm_props2": {"script": "props_farm.py", "globals": {"PROP_LIST": ['rake', 'shovel', 'pitchfork', 'crate', 'milk_can', 'hay_square', 'jerrycan', 'feed_sack', 'stool', 'firewood', 'firewood_triangle', 'firewood_small', 'firewood_loose', 'chopping_block', 'fence', 'gate', 'mailbox', 'bare_bulb', 'pole_lamp', 'phone', 'utility_pole', 'utility_pole_corner', 'utility_pole_transformer', 'service_entry', 'floodlight_stand', 'generator', 'trough']}, "ids": ['GT_Rake_01', 'GT_Shovel_01', 'GT_Pitchfork_01', 'GT_Crate_01', 'GT_MilkCan_01', 'GT_HayBale_Square_01', 'GT_Jerrycan_01', 'GT_FeedSack_01', 'GT_Stool_01', 'GT_FirewoodStack_01', 'GT_FirewoodStack_Triangle_01', 'GT_FirewoodStack_Small_01', 'GT_FirewoodPile_Loose_01', 'GT_ChoppingBlock_01', 'GI_FenceSection_01', 'GI_Gate_01', 'GT_MailboxPost_01', 'GL_BareBulb_01', 'GL_PoleLamp_01', 'GE_LandlinePhone_01', 'GL_UtilityPole_01', 'GL_UtilityPoleCorner_01', 'GL_UtilityPoleTransformer_01', 'GL_ServiceEntry_01', 'GL_FloodlightStand_01', 'FM_Generator_01', 'FM_WaterTrough_01']},
    "bld_farmhouse": {"script": BUILDINGS_PY, "globals": {"BUILDING_LIST": ["farmhouse"], "SKIN_LIST": ["White"], "CONDITIONS": ["New", "Damaged"]},
                      "ids": ["FM_Farmhouse_White_01", "FM_Farmhouse_White_Damaged_01"]},
    "bld_barn": {"script": BUILDINGS_PY, "globals": {"BUILDING_LIST": ["barn"], "SKIN_LIST": ["Red"], "CONDITIONS": ["New", "Damaged"]},
                      "ids": ["FM_Barn_Red_01", "FM_Barn_Red_Damaged_01"]},
    "bld_workshop": {"script": BUILDINGS_PY, "globals": {"BUILDING_LIST": ["workshop"], "SKIN_LIST": ["Metal"], "CONDITIONS": ["New", "Damaged"]},
                      "ids": ["FM_Workshop_Metal_01", "FM_Workshop_Metal_Damaged_01"]},
    "bld_shed": {"script": BUILDINGS_PY, "globals": {"BUILDING_LIST": ["shed"], "SKIN_LIST": ["Weathered"], "CONDITIONS": ["New", "Damaged"]},
                      "ids": ["FM_Shed_Weathered_01", "FM_Shed_Weathered_Damaged_01"]},
    "bld_coop": {"script": BUILDINGS_PY, "globals": {"BUILDING_LIST": ["coop"], "SKIN_LIST": ["Red"], "CONDITIONS": ["New"]},
                      "ids": ["FM_ChickenCoop_Red_01"]},
    "bld_outhouse": {"script": BUILDINGS_PY, "globals": {"BUILDING_LIST": ["outhouse"], "SKIN_LIST": ["Weathered"], "CONDITIONS": ["New"]},
                      "ids": ["FM_Outhouse_Weathered_01"]},
    "bld_well": {"script": BUILDINGS_PY, "globals": {"BUILDING_LIST": ["well"], "SKIN_LIST": ["Stone"], "CONDITIONS": ["New"]},
                      "ids": ["FM_Well_Stone_01"]},
    "bld_silo": {"script": BUILDINGS_PY, "globals": {"BUILDING_LIST": ["silo"], "SKIN_LIST": ["Metal"], "CONDITIONS": ["New"]},
                      "ids": ["FM_Silo_Metal_01"]},
    "bld_windmill": {"script": BUILDINGS_PY, "globals": {"BUILDING_LIST": ["windmill"], "SKIN_LIST": ["White"], "CONDITIONS": ["New"]},
                      "ids": ["FM_Windmill_White_01"]},
    "bld_trailer": {"script": BUILDINGS_PY, "globals": {"BUILDING_LIST": ["trailer"], "SKIN_LIST": ["Beige"], "CONDITIONS": ["New", "Damaged"]},
                      "ids": ["GB_Trailer_Beige_01", "GB_Trailer_Beige_Damaged_01"]},
    "bld_garage": {"script": BUILDINGS_PY, "globals": {"BUILDING_LIST": ["garage"], "SKIN_LIST": ["White"], "CONDITIONS": ["New", "Damaged"]},
                      "ids": ["GB_Garage_White_01", "GB_Garage_White_Damaged_01"]},
    "bld_town_house": {"script": BUILDINGS_PY, "globals": {"BUILDING_LIST": ["town_house"], "SKIN_LIST": ["Brick"], "CONDITIONS": ["New", "Damaged"]},
                      "ids": ["GB_TownHouse_Brick_01", "GB_TownHouse_Brick_Damaged_01"]},
    "bld_diner": {"script": BUILDINGS_PY, "globals": {"BUILDING_LIST": ["diner"], "SKIN_LIST": ["Cream"], "CONDITIONS": ["New", "Damaged"]},
                      "ids": ["GB_Diner_Cream_01", "GB_Diner_Cream_Damaged_01"]},
    "kit": {"script": "kit.py", "globals": {"KIT_LIST": ["Wall_Window"], "SKIN_LIST": ["Brick", "Clapboard", "Barn"]},
                "ids": ["GK_Wall_Window_Brick_01", "GK_Wall_Window_Barn_01"]},
    "kit_door": {"script": "kit.py", "globals": {"KIT_LIST": ["Door_Exterior"]}, "ids": ["GK_Door_Exterior_01"]},
    "veg": {"script": "vegetation.py", "globals": {"VEG_LIST": ["oak", "pine"]}, "ids": ["FM_TreeOak_01", "FM_TreePine_01"]},
    "insects": {"kind": "critters", "clips": ["Idle"],      # the clips come from art/scripts/insect_anim.py: Fly, Walk or Hop as well, by what the insect does
                    "critters": {"Ladybug": "GN_Ladybug_01", "Beetle": "GN_Beetle_01", "Firefly": "GN_Firefly_01", "Honeybee": "GN_Honeybee_01", "Butterfly_Blue": "GN_Butterfly_Blue_01",
                              "Moth": "GN_Moth_01", "Dragonfly": "GN_Dragonfly_01", "Ant": "GN_Ant_01", "Grasshopper": "GN_Grasshopper_01", "Caterpillar": "GN_Caterpillar_01",
                              "Spider": "GN_Spider_01",
                              "StinkBug": "GN_StinkBug_01", "Housefly": "GN_Housefly_01", "Mosquito": "GN_Mosquito_01", "Wasp": "GN_Wasp_01", "Cockroach": "GN_Cockroach_01", "Cricket": "GN_Cricket_01", "Mantis": "GN_Mantis_01", "Earwig": "GN_Earwig_01",
                              "Aphid": "GN_Aphid_01", "Weevil": "GN_Weevil_01", "StagBeetle": "GN_StagBeetle_01", "Scarab": "GN_Scarab_01", "Scorpion": "GN_Scorpion_01", "WolfSpider": "GN_WolfSpider_01", "OrbWeaver": "GN_OrbWeaver_01", "JumpingSpider": "GN_JumpingSpider_01"},
                    "ids": ['GN_Ladybug_01', 'GN_Beetle_01', 'GN_Firefly_01', 'GN_Honeybee_01', 'GN_Butterfly_Blue_01', 'GN_Moth_01', 'GN_Dragonfly_01', 'GN_Ant_01', 'GN_Grasshopper_01', 'GN_Caterpillar_01', 'GN_Spider_01', 'GN_StinkBug_01', 'GN_Housefly_01', 'GN_Mosquito_01', 'GN_Wasp_01', 'GN_Cockroach_01', 'GN_Cricket_01', 'GN_Mantis_01', 'GN_Earwig_01', 'GN_Aphid_01', 'GN_Weevil_01', 'GN_StagBeetle_01', 'GN_Scarab_01', 'GN_Scorpion_01', 'GN_WolfSpider_01', 'GN_OrbWeaver_01', 'GN_JumpingSpider_01']},
    "sports_balls": {"script": SPORTS_PY, "globals": {"SPORT_LIST": ["balls"]}, "ids": ['GS_Basketball_01', 'GS_Soccerball_01', 'GS_Baseball_01', 'GS_TennisBall_01', 'GS_Football_01', 'GS_Volleyball_01', 'GS_GolfBall_01', 'GS_BowlingBall_01', 'GS_HockeyPuck_01']},
    "sports_nets": {"script": SPORTS_PY, "globals": {"SPORT_LIST": ["nets"]}, "ids": ['GS_BasketballHoop_01', 'GS_SoccerGoal_01', 'GS_HockeyGoal_01', 'GS_TennisNet_01', 'GS_VolleyballNet_01']},
    "sports_gear": {"script": SPORTS_PY, "globals": {"SPORT_LIST": ["gear"]}, "ids": ['GS_BaseballBat_Metal_01', 'GS_BaseballGlove_01', 'GS_HomePlate_01', 'GS_BaseballBase_01', 'GS_TennisRacket_01', 'GS_HockeyStick_01', 'GS_GolfClub_01', 'GS_FootballHelmet_01', 'GS_Skateboard_01', 'GS_Dumbbell_01', 'GS_TrainingCone_01', 'GS_Frisbee_01']},
    "office_furniture": {"script": OFFICE_PY, "globals": {"OFFICE_LIST": ["desks", "seating", "FilingCabinet", "Whiteboard_Stand"]}, "ids": ['GO_Desk_Wood_01', 'GO_Desk_Steel_01', 'GO_Desk_L_01', 'GO_ConferenceTable_01', 'GO_Chair_Office_01', 'GO_FilingCabinet_01', 'GO_Whiteboard_Stand_01']},
    "office_cubicle": {"script": OFFICE_PY, "globals": {"OFFICE_LIST": ["cubicle"]}, "ids": ['GO_Cubicle_Panel_Low_01', 'GO_Cubicle_Panel_High_01', 'GO_Cubicle_Panel_Glass_01', 'GO_Cubicle_Worksurface_01', 'GO_Cubicle_OverheadBin_01', 'GO_Cubicle_Pod_01']},
    "office_equipment": {"script": OFFICE_PY, "globals": {"OFFICE_LIST": ["Copier", "Printer_Desktop", "WaterCooler", "Shredder", "Wastebasket", "desktop"]}, "ids": ['GO_Copier_01', 'GO_Printer_Desktop_01', 'GO_WaterCooler_01', 'GO_Shredder_01', 'GO_Wastebasket_01', 'GO_Workstation_01', 'GO_Phone_01']},
    "people": {"kind": "people", "clips": ["Idle", "Walk", "Run", "Sit"],
                   "people": {"farmer": "GP_Farmer_01", "sheriff": "GP_Sheriff_01", "farmer_kid": "GP_FarmerKid_01", "waitress": "GP_Waitress_01", "grey": "GP_Grey_01",
                           "farmer_spouse": "GP_FarmerSpouse_01", "grandparent": "GP_Grandparent_01", "worker": "GP_Worker_01", "deputy": "GP_Deputy_01",
                           "fbi_agent": "GP_FbiAgent_01", "fbi_agent_f": "GP_FbiAgentF_01", "mib": "GP_Mib_01",
                           "nordic": "GP_Nordic_01", "shadow": "GP_Shadow_01", "reptilian": "GP_Reptilian_01"}},
    "animals": {"kind": "animals", "clips": ["Idle", "Walk"], "dog_clips": ["Trot", "Run"],
                    "animals": {"cow": "GN_Cow_faceted_01", "horse": "GN_Horse_faceted_01", "dog_collie": "GN_DogCollie_faceted_01",
                             "dog_husky": "GN_DogHusky_faceted_01", "cat_tabby": "GN_CatTabby_faceted_01",
                             "sheep": "GN_Sheep_faceted_01", "pig": "GN_Pig_faceted_01", "goat": "GN_Goat_faceted_01"}},
    "birds": {"kind": "animals", "birds": True, "clips": [], "animals": {"chicken_hen": "GN_ChickenHen_faceted_01"}},
}


# ===== How the browser describes each model =====================================================================
# id -> name, type (ONE primary category path), tags (space separated: the setting, colour, condition, and whatever helps a search),
# group (models in one group are variants of each other: the same model in another skin, style or colour).
ASSETS = {}

# Colour variants that are not models of their own, per base model: `parts` are its paintable parts (a part = a palette swatch the model uses only for
# that part), `presets` the named paints. A preset's `set` gives a swatch name or a #RRGGBB per part; `was` is the id of the GLB that used to be built for
# it (tools/paints.py check compares the two while that GLB is around, and the viewer keeps old links to it working). Only the base is built and shipped:
# the viewer recolours a copy of the palette image, and a person can paint any part any colour. See tools/paints.py.
PAINTS = {
    "GV_Sedan_01": {"base": "Blue", "parts": {"Body": "truck_blue"}, "presets": {
        "Red": {"was": "GV_Sedan_Red_01", "set": {"Body": "cloth_red"}}, "White": {"set": {"Body": "paint_white"}}, "Tan": {"set": {"Body": "tan"}},
        "Grey": {"set": {"Body": "fabric_grey"}}, "Green": {"set": {"Body": "tractor_green"}}, "Black": {"set": {"Body": "black"}}}},
    "GV_Tractor_01": {"base": "Green", "parts": {"Body": "tractor_green"}, "presets": {
        "Red": {"was": "GV_Tractor_Red_01", "set": {"Body": "cloth_red"}}, "Orange": {"set": {"Body": "orange_cat"}},
        "Blue": {"set": {"Body": "truck_blue"}}, "Yellow": {"set": {"Body": "paint_yellow"}}}},
    "FD_Apple_01": {"base": "Red", "parts": {"Skin": "cloth_red", "Leaf": "plant_green"}, "presets": {
        "Green": {"was": "FD_Apple_Green_01", "set": {"Skin": "#8FBF3A"}}, "Yellow": {"was": "FD_Apple_Yellow_01", "set": {"Skin": "#E8D25A"}},
        "Rotten": {"was": "FD_Apple_Rotten_01", "set": {"Skin": "#6F7F4A", "Leaf": "#6F7F4A"}}}},
    "FD_BananaBunch_01": {"base": "Fresh", "parts": {"Skin": "paint_yellow", "Stem": "banana_green"}, "presets": {
        "Rotten": {"was": "FD_BananaBunch_Rotten_01", "set": {"Skin": "#7A5A44", "Stem": "#6F7F4A"}}}},
    "FD_Orange_01": {"base": "Fresh", "parts": {"Skin": "food_orange", "Leaf": "plant_green"}, "presets": {"Rotten": {"was": "FD_Orange_Rotten_01", "set": {"Leaf": "#6F7F4A", "Skin": "#6F7F4A"}}}},
    "FD_Banana_01": {"base": "Fresh", "parts": {"Skin": "banana_yellow", "Neck": "corn_green", "Stalk end": "bark", "Tip": "black"}, "presets": {"Rotten": {"was": "FD_Banana_Rotten_01", "set": {"Neck": "#6F7F4A", "Skin": "#7A5A44"}}}},
    "FD_Carrot_01": {"base": "Fresh", "parts": {"Root": "food_orange", "Leaves": "plant_green"}, "presets": {"Rotten": {"was": "FD_Carrot_Rotten_01", "set": {"Leaves": "#6F7F4A", "Root": "#6F7F4A"}}}},
    "FD_Tomato_01": {"base": "Fresh", "parts": {"Skin": "cloth_red", "Calyx": "plant_green"}, "presets": {"Rotten": {"was": "FD_Tomato_Rotten_01", "set": {"Skin": "#6F7F4A", "Calyx": "#6F7F4A"}}}},
    "FD_Potato_01": {"base": "Fresh", "parts": {"Skin": "tan"}, "presets": {"Rotten": {"was": "FD_Potato_Rotten_01", "set": {"Skin": "#7A7064"}}}},
    "FD_Onion_01": {"base": "Fresh", "parts": {"Skin": "golden", "Roots and tip": "dead_wood"}, "presets": {"Rotten": {"was": "FD_Onion_Rotten_01", "set": {"Skin": "#7A7064"}}}},
    "FD_Corn_01": {"base": "Fresh", "parts": {"Stalk and outer husk": "corn_green", "Inner husk": "corn_leaf", "Kernels": "corn_cob"}, "presets": {"Rotten": {"was": "FD_Corn_Rotten_01", "set": {"Stalk and outer husk": "#6F7F4A", "Inner husk": "#7A7064", "Kernels": "#7A5A44"}}}},
    "FD_Lettuce_01": {"base": "Fresh", "parts": {"Leaves": "corn_leaf", "Heart": "lettuce_heart", "Outer leaf edges": "corn_green"}, "presets": {"Rotten": {"was": "FD_Lettuce_Rotten_01", "set": {"Outer leaf edges": "#6F7F4A", "Leaves": "#7A7064", "Heart": "#7A7064"}}}},
    "FD_Cabbage_01": {"base": "Fresh", "parts": {"Outer leaves": "leaf_dark", "Core, stem and ribs": "siding_green", "Middle leaves": "grass", "Second leaves": "corn_green", "Innermost leaves": "corn_leaf"}, "presets": {"Rotten": {"was": "FD_Cabbage_Rotten_01", "set": {"Middle leaves": "#6F7F4A", "Second leaves": "#6F7F4A", "Innermost leaves": "#7A7064", "Outer leaves": "#6F7F4A", "Core, stem and ribs": "#6F7F4A"}}}},
    "FD_Watermelon_01": {"base": "Fresh", "parts": {"Rind": "grass", "Stripes": "leaf_dark"}, "presets": {"Rotten": {"was": "FD_Watermelon_Rotten_01", "set": {"Rind": "#6F7F4A", "Stripes": "#6F7F4A"}}}},
    "FD_Pumpkin_01": {"base": "Fresh", "parts": {"Rind": "food_orange", "Stem": "plant_green"}, "presets": {"Rotten": {"was": "FD_Pumpkin_Rotten_01", "set": {"Stem": "#6F7F4A", "Rind": "#6F7F4A"}}}},
    "FD_Baguette_01": {"base": "Fresh", "parts": {"Crust": "crust", "Cuts": "dough"}, "presets": {"Rotten": {"was": "FD_Baguette_Rotten_01", "set": {"Crust": "#7A7064", "Cuts": "#7A5A44"}}}},
    "FD_Cake_01": {"base": "Fresh", "parts": {"Top tier": "fabric_pink", "Base tier": "paint_white", "Plate": "metal_galv", "Cherry": "cloth_red", "Candles": "paint_yellow"}, "presets": {"Rotten": {"was": "FD_Cake_Rotten_01", "set": {"Base tier": "#7A7064", "Cherry": "#6F7F4A", "Candles": "#7A5A44", "Top tier": "#7A7064"}}}},
    "FD_Donut_01": {"base": "Fresh", "parts": {"Dough": "crust", "Icing": "fabric_pink", "Hole": "black"}, "presets": {"Rotten": {"was": "FD_Donut_Rotten_01", "set": {"Icing": "#7A7064", "Dough": "#7A7064"}}}},
    "FD_CheeseWedge_01": {"base": "Fresh", "parts": {"Cut face": "cheese_cut", "Rind": "cheese_rind", "Holes": "cheese_hole"}, "presets": {"Rotten": {"was": "FD_CheeseWedge_Rotten_01", "set": {"Cut face": "#6F7F4A", "Rind": "#7A7064", "Holes": "#7A5A44"}}}},
    "FD_Butter_01": {"base": "Fresh", "parts": {"Butter": "paint_yellow", "Wrapper": "paint_white"}, "presets": {"Rotten": {"was": "FD_Butter_Rotten_01", "set": {"Wrapper": "#7A7064", "Butter": "#7A5A44"}}}},
    "FD_Steak_01": {"base": "Fresh", "parts": {"Meat": "meat_red", "Plate and fat": "paint_white"}, "presets": {"Rotten": {"was": "FD_Steak_Rotten_01", "set": {"Plate and fat": "#7A7064", "Meat": "#6F7F4A"}}}},
    "FD_Sausages_01": {"base": "Fresh", "parts": {"Sausages": "rust", "Plate": "paint_white"}, "presets": {"Rotten": {"was": "FD_Sausages_Rotten_01", "set": {"Sausages": "#6F7F4A", "Plate": "#7A7064"}}}},
    "FD_Drumstick_01": {"base": "Fresh", "parts": {"Meat": "crust", "Bone": "horn_cream"}, "presets": {"Rotten": {"was": "FD_Drumstick_Rotten_01", "set": {"Meat": "#7A7064"}}}},
    "FD_TurkeyRoast_01": {"base": "Fresh", "parts": {"Skin": "crust", "Tray": "metal_galv", "Leg bones": "paint_white"}, "presets": {"Rotten": {"was": "FD_TurkeyRoast_Rotten_01", "set": {"Leg bones": "#7A7064", "Skin": "#7A7064"}}}},
    "FD_Fish_01": {"base": "Fresh", "parts": {"Body": "fabric_grey", "Tail fin": "metal_galv"}, "presets": {"Rotten": {"was": "FD_Fish_Rotten_01", "set": {"Body": "#6F7F4A"}}}},
    "FD_HotDog_01": {"base": "Fresh", "parts": {"Bun": "dough", "Sausage": "meat_red", "Mustard": "paint_yellow"}, "presets": {"Rotten": {"was": "FD_HotDog_Rotten_01", "set": {"Mustard": "#7A5A44", "Bun": "#7A5A44", "Sausage": "#6F7F4A"}}}},
    "FD_Sandwich_01": {"base": "Fresh", "parts": {"Bread": "dough", "Lettuce": "plant_green", "Filling": "meat_red"}, "presets": {"Rotten": {"was": "FD_Sandwich_Rotten_01", "set": {"Lettuce": "#6F7F4A", "Bread": "#7A5A44", "Filling": "#6F7F4A"}}}},
    "FD_SodaCan_Red_01": {"base": "Red", "parts": {"Label": "label_red", "Can": "metal_galv", "Lid": "metal_dark"}, "presets": {"Blue": {"was": "FD_SodaCan_Blue_01", "set": {"Label": "#2F6F9F"}}, "Green": {"was": "FD_SodaCan_Green_01", "set": {"Label": "#3F7A3A"}}}},
    "FD_Grapes_01": {"base": "Green", "parts": {"Fruit": "grape_green"}, "presets": {"Purple": {"was": "FD_Grapes_Purple_01", "set": {"Fruit": "#5A2E6B"}}}},
    "GN_Butterfly_01": {"base": "Blue", "parts": {"Wings": "wing_blue"}, "presets": {"Monarch": {"was": "GN_Butterfly_Monarch_01", "set": {"Wings": "#E8922A"}}}},
    "GK_Wall_Window_Barn_01": {"base": "Barn red", "parts": {"Siding": "barn_red"}, "presets": {"Clapboard": {"was": "GK_Wall_Window_Clapboard_01", "set": {"Siding": "#E6E2D6"}}}},
    "GS_BaseballBat_Metal_01": {"base": "Metal", "parts": {"Barrel": "truck_blue", "Grip": "rubber"}, "presets": {
        "Wood": {"was": "GS_BaseballBat_Wood_01", "set": {"Barrel": "#C9A06A", "Grip": "#1B1B1E"}}}},
}


def _a(id, name, type, tags, group=None):
    ASSETS[id] = {"name": name, "type": type, "tags": tags.split(), "group": group}


# vehicles

# Style variants that are only a colour theme of art/scripts/home_styles.py THEMES: base id -> {theme: id of the GLB that used to be built for it}. The viewer
# applies the theme to the palette image (the manifest carries the themes once); Damaged is never listed: it also drops parts and tilts (see docs/style-audit.md).
THEMED = {}

_a("GV_Sedan_01", "Sedan", "vehicles/road/sedan", "modern urban suburban car blue red new civilian", "sedan")
_a("GV_Sedan_Damaged_01", "Sedan, wrecked", "vehicles/road/sedan", "modern urban suburban car damaged wreck rusty abandoned", "sedan")
_a("GV_Taxi_Yellow_01", "Taxi", "vehicles/road/taxi", "modern urban car yellow new cab service")
_a("GV_Van_01", "Delivery van", "vehicles/road/van", "modern urban brown new delivery service")
_a("GV_Police_Sheriff_01", "Sheriff's cruiser", "vehicles/road/police", "rural law enforcement car white new emergency sheriff")
_a("GV_Ambulance_White_01", "Ambulance", "vehicles/road/ambulance", "modern urban white new emergency medical van")
_a("GV_Motorcycle_01", "Motorcycle", "vehicles/road/motorcycle", "modern red new bike two-wheeler")
_a("GV_Tractor_01", "Tractor", "vehicles/farm/tractor", "rural farm green red new machine")
_a("GV_Pickup_01", "Farm pickup", "vehicles/farm/pickup", "rural farm truck blue new")
_a("SH_Scout_01", "Scout ship", "vehicles/ship/scout", "sci-fi alien ship flying saucer ufo violet glow new")
_a("SH_Dart_01", "Dart ship", "vehicles/ship/dart", "sci-fi alien ship flyer fast glow new")
# sci-fi: alien ship parts, devices and wreckage (the landed ship's interior and its terminals are under vehicles)
_a("SH_PowerCell_01", "Power cell", "sci-fi/ship-part/power-cell", "glow cylinder energy carriable sci-fi alien ship new")
_a("SH_HullPanel_01", "Hull panel", "sci-fi/ship-part/hull-panel", "hull plate hexagonal grey carriable sci-fi alien ship new")
_a("SH_NavCrystal_01", "Nav crystal", "sci-fi/ship-part/nav-crystal", "navigation crystal glow cyan carriable sci-fi alien ship new")
_a("SH_EngineCoil_01", "Engine coil", "sci-fi/ship-part/engine-coil", "engine coil ring glow carriable sci-fi alien ship new")
_a("SH_ThrusterNozzle_01", "Thruster nozzle", "sci-fi/ship-part/thruster-nozzle", "thruster engine nozzle glow carriable sci-fi alien ship new")
_a("SH_FuelCanister_01", "Fuel canister", "sci-fi/ship-part/fuel-canister", "fuel canister tank carriable sci-fi alien ship new")
_a("SH_ShieldEmitter_01", "Shield emitter", "sci-fi/ship-part/shield-emitter", "shield emitter dish glow carriable sci-fi alien ship new")
_a("SH_CommsArray_01", "Comms array", "sci-fi/ship-part/comms-array", "communications antenna array carriable sci-fi alien ship new")
_a("SH_BlackBox_01", "Black box", "sci-fi/ship-part/black-box", "flight recorder box dark carriable sci-fi alien ship new")
_a("SH_WarpRingSegment_01", "Warp ring segment", "sci-fi/ship-part/warp-ring", "warp drive ring arc glow sci-fi alien ship new")
_a("SH_LandingLeg_01", "Landing leg", "sci-fi/ship-part/landing-leg", "landing leg strut pad sci-fi alien ship new")
_a("SH_ConsoleModule_01", "Console module", "sci-fi/ship-part/console-module", "console module buttons screen carriable sci-fi alien ship new")
_a("SH_Beacon_01", "Beacon", "sci-fi/device/beacon", "signal beacon light glow sci-fi alien ship new")
_a("SH_SpecimenJar_01", "Specimen jar", "sci-fi/device/specimen-jar", "specimen jar glass lab sci-fi alien ship new")
_a("SH_ContainmentPod_01", "Containment pod", "sci-fi/device/containment-pod", "containment pod capsule lab glow sci-fi alien ship new")
_a("SH_RepairTool_01", "Repair tool", "sci-fi/device/repair-tool", "repair handheld tool glow sci-fi alien ship new")
_a("SH_Scanner_01", "Alien scanner", "sci-fi/device/scanner", "scanner handheld screen glow sci-fi alien ship new")
_a("SH_Translator_01", "Translator", "sci-fi/device/translator", "translator handheld speaker glow sci-fi alien ship new")
_a("SH_HullShard_A_01", "Hull shard, flat", "sci-fi/debris/hull-shard", "wreckage shard hull crash broken sci-fi alien ship damaged")
_a("SH_HullShard_B_01", "Hull shard, upright", "sci-fi/debris/hull-shard-upright", "wreckage shard hull crash broken sci-fi alien ship damaged")
_a("SH_CableTangle_01", "Cable tangle", "sci-fi/debris/cable-tangle", "wreckage cables crash tangled sci-fi alien ship damaged")
_a("SH_ScorchedGround_01", "Scorched ground", "sci-fi/debris/scorched-ground", "crash scorch burn mark ground decal sci-fi alien ship damaged")

_a("SH_Cigar_01", "Cigar ship", "vehicles/ship/cigar", "sci-fi alien ship long cylinder craft glow new")
_a("SH_Triangle_01", "Triangle ship", "vehicles/ship/triangle", "sci-fi alien ship black triangle craft lights new")
_a("SH_EscapePod_01", "Escape pod", "vehicles/ship/escape-pod", "sci-fi alien ship small capsule pod landing legs new")
_a("SH_ProbeDrone_01", "Probe drone", "vehicles/ship/probe-drone", "sci-fi alien ship small floating scout drone new")
_a("SH_DropShip_01", "Drop ship", "vehicles/ship/drop-ship", "sci-fi alien ship transport landing craft new")
_a("SH_MIBCraft_01", "Agency craft", "vehicles/ship/agency-craft", "sci-fi ship government black agency craft new")
_a("SH_Mothership_01", "Mothership", "vehicles/ship/mothership", "sci-fi alien ship huge orbiting carrier new")
_a("SH_AbductionUfo_01", "Abduction UFO", "vehicles/ship/abduction-ufo", "sci-fi alien ship flying saucer ufo beam cyan small new")
_a("GV_CrashedShip_01", "Crashed saucer", "vehicles/ship/crashed-saucer", "sci-fi alien ship saucer landed crashed walkable interior ramp grey cyan damaged")
_a("GV_ShipEgg_01", "Egg ship", "vehicles/ship/egg", "sci-fi alien ship egg gold violet landed walkable interior ramp legs new")
_a("GV_ShipFreighter_01", "Freighter ship", "vehicles/ship/freighter", "sci-fi alien ship freighter cargo containers landed walkable interior ramp legs new")
_a("GV_ShipLockers_01", "Ship lockers", "vehicles/ship-interior/lockers", "sci-fi alien ship interior locker wall new")
_a("GV_ShipPod_01", "Stasis pod", "vehicles/ship-interior/pod", "sci-fi alien ship interior stasis sleep capsule glow new")
_a("GV_ShipJars_01", "Specimen jars", "vehicles/ship-interior/jars", "sci-fi alien ship interior lab specimen jar glass cow plant new")
_a("GV_ShipConduit_01", "Cable run", "vehicles/ship-interior/conduit", "sci-fi alien ship interior cable conduit wall new")
_a("GV_ShipHoloTable_01", "Holo-map table", "vehicles/ship-interior/holo-table", "sci-fi alien ship interior hologram map table glow new")
_a("GV_ShipCouch_01", "Medical couch", "vehicles/ship-interior/couch", "sci-fi alien ship interior lab medical bed couch new")
_a("GV_ShipToolRack_01", "Ship tool rack", "vehicles/ship-interior/tool-rack", "sci-fi alien ship interior lab tools wall new")
_a("GV_ShipSampleRack_01", "Sample rack", "vehicles/ship-interior/sample-rack", "sci-fi alien ship interior lab samples wall new")
_a("GV_ShipHelm_01", "Pilot's helm", "vehicles/ship-interior/helm", "sci-fi alien ship interior bridge pilot desk chair new")
_a("GV_ShipNavScreen_01", "Nav screen", "vehicles/ship-interior/nav-screen", "sci-fi alien ship interior bridge screen star chart new")
_a("GV_ShipRadarPost_01", "Radar post", "vehicles/ship-interior/radar-post", "sci-fi alien ship interior bridge radar new")
_a("GV_ShipCrates_01", "Cargo crates", "vehicles/ship-interior/crates", "sci-fi alien ship interior cargo crates pallet new")
_a("GV_ShipDrums_01", "Cargo drums", "vehicles/ship-interior/drums", "sci-fi alien ship interior cargo drums barrels pallet new")
_a("GV_ShipBunk_01", "Ship bunk", "vehicles/ship-interior/bunk", "sci-fi alien ship interior quarters bed bunk new")
_a("GV_ShipMess_01", "Mess table", "vehicles/ship-interior/mess-table", "sci-fi alien ship interior quarters table seats new")
_a("GV_ShipConsole_01", "Ship console", "vehicles/ship-interior/console", "sci-fi alien ship interior control desk buttons glow new")
_a("GV_ShipTerminalBank_01", "Bank terminal", "vehicles/ship-interior/terminal-bank", "sci-fi alien ship interior terminal green screen ledger new")
_a("GV_ShipTerminalLaunch_01", "Launch terminal", "vehicles/ship-interior/terminal-launch", "sci-fi alien ship interior terminal red screen lever warning new")
# animals
_a("GN_Cow_faceted_01", "Cow", "animals/farm/cow", "rural farm livestock black white animal quadruped")
_a("GN_Horse_faceted_01", "Horse", "animals/farm/horse", "rural farm livestock brown animal quadruped")
_a("GN_Sheep_faceted_01", "Sheep", "animals/farm/sheep", "rural farm livestock white wool animal quadruped")
_a("GN_Pig_faceted_01", "Pig", "animals/farm/pig", "rural farm livestock pink animal quadruped")
_a("GN_Goat_faceted_01", "Goat", "animals/farm/goat", "rural farm livestock horns animal quadruped")
_a("GN_ChickenHen_faceted_01", "Hen", "animals/farm/hen", "rural farm poultry bird chicken animal")
_a("GN_DogCollie_faceted_01", "Dog, collie", "animals/pet/dog", "rural farm pet dog animal quadruped collie")
_a("GN_DogHusky_faceted_01", "Dog, husky", "animals/pet/dog", "pet dog animal quadruped husky grey white")
_a("GN_CatTabby_faceted_01", "Cat, tabby", "animals/pet/cat", "pet cat animal quadruped tabby")
# insects (rigged for the browser: wings, legs and antennae move; real size in millimetres)
_a("GN_Ladybug_01", "Ladybug", "animals/insect/ladybug", "wild garden insect bug beetle red tiny")
_a("GN_Beetle_01", "Beetle", "animals/insect/beetle", "wild garden insect bug green tiny")
_a("GN_Firefly_01", "Firefly", "animals/insect/firefly", "wild night insect bug glow lightning-bug tiny")
_a("GN_Honeybee_01", "Honeybee", "animals/insect/bee", "wild garden farm insect bug bee yellow flying tiny")
_a("GN_Butterfly_01", "Butterfly", "animals/insect/butterfly", "wild garden insect blue flying wings")
_a("GN_Moth_01", "Moth", "animals/insect/moth", "wild night insect grey flying wings")
_a("GN_Dragonfly_01", "Dragonfly", "animals/insect/dragonfly", "wild pond insect teal flying wings")
_a("GN_Ant_01", "Ant", "animals/insect/ant", "wild garden insect bug black tiny")
_a("GN_Grasshopper_01", "Grasshopper", "animals/insect/grasshopper", "wild field rural insect bug green hopper")
_a("GN_Caterpillar_01", "Caterpillar", "animals/insect/caterpillar", "wild garden insect bug green larva")
_a("GN_Spider_01", "Spider", "animals/arachnid/spider", "wild cellar barn bug arachnid brown eight-legs spider")
_a("GN_StinkBug_01", "Stink bug", "animals/insect/stink-bug", INSECT_BROWN_TAGS)
_a("GN_Housefly_01", "Housefly", "animals/insect/fly", "wild house insect bug fly grey tiny flying")
_a("GN_Mosquito_01", "Mosquito", "animals/insect/mosquito", "wild insect bug mosquito grey tiny flying")
_a("GN_Wasp_01", "Wasp", "animals/insect/wasp", "wild garden insect bug yellow black tiny flying")
_a("GN_Cockroach_01", "Cockroach", "animals/insect/cockroach", "wild house insect bug brown")
_a("GN_Cricket_01", "Cricket", "animals/insect/cricket", INSECT_BROWN_TAGS)
_a("GN_Mantis_01", "Praying mantis", "animals/insect/mantis", "wild garden insect bug green")
_a("GN_Earwig_01", "Earwig", "animals/insect/earwig", INSECT_BROWN_TAGS)
_a("GN_Aphid_01", "Aphid", "animals/insect/aphid", "wild garden insect bug green tiny")
_a("GN_Weevil_01", "Weevil", "animals/insect/weevil", INSECT_BROWN_TAGS)
_a("GN_StagBeetle_01", "Stag beetle", "animals/insect/stag-beetle", "wild garden insect bug beetle brown black")
_a("GN_Scarab_01", "Scarab beetle", "animals/insect/scarab", "wild garden insect bug beetle black")
_a("GN_Scorpion_01", "Scorpion", "animals/arachnid/scorpion", "wild desert arachnid tan stinging bug eight-legs")
_a("GN_WolfSpider_01", "Wolf spider", "animals/arachnid/wolf-spider", "wild garden arachnid spider brown bug eight-legs")
_a("GN_OrbWeaver_01", "Orb-weaver spider", "animals/arachnid/orb-weaver", "wild garden arachnid spider brown orange bug eight-legs")
_a("GN_JumpingSpider_01", "Jumping spider", "animals/arachnid/jumping-spider", "wild garden arachnid spider black tiny bug eight-legs")
# sports: balls, nets and goals, equipment
_a("GS_Basketball_01", "Basketball", "sports/ball/basketball", "basketball orange new gym court playground")
_a("GS_Soccerball_01", "Soccer ball", "sports/ball/soccer-ball", "soccer football white black new field")
_a("GS_Baseball_01", "Baseball", "sports/ball/baseball", "baseball white red new field diamond")
_a("GS_TennisBall_01", "Tennis ball", "sports/ball/tennis-ball", "tennis yellow new court")
_a("GS_Football_01", "American football", "sports/ball/american-football", "football brown leather new field")
_a("GS_Volleyball_01", "Volleyball", "sports/ball/volleyball", "volleyball yellow blue new court beach")
_a("GS_GolfBall_01", "Golf ball", "sports/ball/golf-ball", "golf white new course tiny")
_a("GS_BowlingBall_01", "Bowling ball", "sports/ball/bowling-ball", "bowling purple new alley holes")
_a("GS_HockeyPuck_01", "Hockey puck", "sports/ball/hockey-puck", "hockey black new ice rink")
_a("GS_BasketballHoop_01", "Basketball hoop", "sports/net/basketball-hoop", "basketball hoop backboard rim new driveway court")
_a("GS_SoccerGoal_01", "Soccer goal", "sports/net/soccer-goal", "soccer football goal net new field")
_a("GS_HockeyGoal_01", "Hockey goal", "sports/net/hockey-goal", "hockey goal net red new rink")
_a("GS_TennisNet_01", "Tennis net", "sports/net/tennis-net", "tennis net posts new court")
_a("GS_VolleyballNet_01", "Volleyball net", "sports/net/volleyball-net", "volleyball net posts new court beach")
_a("GS_BaseballBat_Metal_01", "Baseball bat", "sports/equipment/baseball-bat", "baseball bat metal blue new field")
_a("GS_BaseballGlove_01", "Baseball glove", "sports/equipment/baseball-glove", "baseball glove leather brown new field")
_a("GS_HomePlate_01", "Home plate", "sports/equipment/home-plate", "baseball plate white new field diamond")
_a("GS_BaseballBase_01", "Base", "sports/equipment/base", "baseball base white new field diamond")
_a("GS_TennisRacket_01", "Tennis racket", "sports/equipment/tennis-racket", "tennis racket strings new court")
_a("GS_HockeyStick_01", "Hockey stick", "sports/equipment/hockey-stick", "hockey stick black new rink")
_a("GS_GolfClub_01", "Golf club", "sports/equipment/golf-club", "golf club driver new course")
_a("GS_FootballHelmet_01", "Football helmet", "sports/equipment/helmet", "football helmet blue new field protective")
_a("GS_Skateboard_01", "Skateboard", "sports/equipment/skateboard", "skateboard red wheels new street")
_a("GS_Dumbbell_01", "Dumbbell", "sports/equipment/dumbbell", "gym weights dumbbell black new fitness")
_a("GS_TrainingCone_01", "Training cone", "sports/equipment/cone", "cone orange training new field")
_a("GS_Frisbee_01", "Frisbee", "sports/equipment/frisbee", "frisbee disc blue new park")
# office: desks, a chair, the cubicle kit (1.5 m module), equipment
_a("GO_Desk_Wood_01", "Desk, wood", "furniture/office/desk", "office wood laminate new drawers pedestal", "office-desk")
_a("GO_Desk_Steel_01", "Desk, steel", "furniture/office/desk", "office steel grey black new drawers pedestal retro", "office-desk")
_a("GO_Desk_L_01", "Desk, corner", "furniture/office/corner-desk", "office modern white steel new")
_a("GO_ConferenceTable_01", "Conference table", "furniture/office/conference-table", "office meeting large laminate new")
_a("GO_Chair_Office_01", "Office chair", "furniture/office/chair", "office swivel casters seat new")
_a("GO_FilingCabinet_01", "Filing cabinet", "furniture/office/filing-cabinet", "office steel grey drawers storage new")
_a("GO_Whiteboard_Stand_01", "Whiteboard on stand", "furniture/office/whiteboard", "office meeting board wheels new")
_a("GO_Cubicle_Panel_Low_01", "Cubicle panel, low", CUBICLE_PANEL, "office cubicle partition modular fabric new", "cubicle-panel")
_a("GO_Cubicle_Panel_High_01", "Cubicle panel, high", CUBICLE_PANEL, "office cubicle partition modular fabric new", "cubicle-panel")
_a("GO_Cubicle_Panel_Glass_01", "Cubicle panel, glass top", CUBICLE_PANEL, "office cubicle partition modular glass new", "cubicle-panel")
_a("GO_Cubicle_Worksurface_01", "Cubicle worksurface", "furniture/cubicle/worksurface", "office cubicle desk modular corner new")
_a("GO_Cubicle_OverheadBin_01", "Cubicle overhead bin", "furniture/cubicle/overhead-bin", "office cubicle storage modular flap new")
_a("GO_Cubicle_Pod_01", "Cubicle, assembled", "furniture/cubicle/pod", "office cubicle desk partition drawers new")
_a("GO_Copier_01", "Copier", "appliances/office/copier", "office copier printer scanner trays lid new")
_a("GO_Printer_Desktop_01", "Desktop printer", "appliances/office/printer", "office printer laser tray cover new")
_a("GO_WaterCooler_01", "Water cooler", "appliances/office/water-cooler", "office water jug taps cabinet new")
_a("GO_Shredder_01", "Paper shredder", "appliances/office/shredder", "office paper bin black new")
_a("GO_Wastebasket_01", "Wastebasket", "furniture/office/wastebasket", "office bin trash paper new")
_a("GO_Workstation_01", "Monitor and keyboard", "decor/electronics/computer", "office computer monitor keyboard mouse screen new")
_a("GO_Phone_01", "Desk phone", "decor/electronics/phone", "office telephone handset keypad new")
# people
_a("GP_Farmer_01", "Farmer", "people/civilian/farmer", "rural farm adult man cap beard flannel human")
_a("GP_FarmerKid_01", "Farmer's kid", "people/civilian/kid", "rural farm child kid human")
_a("GP_Waitress_01", "Waitress", "people/civilian/waitress", "diner retro adult woman red human")
_a("GP_Sheriff_01", "Sheriff", "people/law/sheriff", "rural law enforcement adult uniform tan hat human")
_a("GP_Grey_01", "Grey alien", "people/alien/grey", "sci-fi alien grey humanoid")
_a("GP_FarmerSpouse_01", "Farmer's spouse", "people/civilian/spouse", "rural farm adult woman dress long-hair human")
_a("GP_Grandparent_01", "Grandparent", "people/civilian/grandparent", "rural farm elder fedora cardigan grey human")
_a("GP_Worker_01", "Worker", "people/civilian/worker", "town industrial adult man hard-hat hi-vis vest human")
_a("GP_Deputy_01", "Deputy", "people/law/deputy", "rural law enforcement adult man uniform tan badge human")
_a("GP_FbiAgent_01", "FBI agent, man", "people/law/fbi-agent", "urban government adult man suit tie navy human", "fbi-agent")
_a("GP_FbiAgentF_01", "FBI agent, woman", "people/law/fbi-agent", "urban government adult woman suit tie navy human", "fbi-agent")
_a("GP_Mib_01", "Man in Black", "people/law/mib", "urban government adult man suit tie black sunglasses conspiracy human")
_a("GP_Nordic_01", "Nordic alien", "people/alien/nordic", "sci-fi alien tall pale blond robe glow humanoid")
_a("GP_Shadow_01", "Shadow entity", "people/alien/shadow", "sci-fi alien tall dark glow horror humanoid")
_a("GP_Reptilian_01", "Reptilian alien", "people/alien/reptilian", "sci-fi alien green scaled tail crest humanoid")
# appliances and storage that open
_a("GI_Fridge_01", "Fridge, two-door", FRIDGE, "classic kitchen white new cold two-door freezer-top", "fridge")
_a("GI_Fridge_Modern_01", "Fridge, French door", FRIDGE, "modern kitchen steel new cold french-door bottom-freezer drawer", "fridge")
_a("GI_Fridge_Dispenser_01", "Fridge, ice and water dispenser", FRIDGE, "modern kitchen steel new cold french-door bottom-freezer drawer ice water dispenser", "fridge")
_a("GI_Fridge_Retro_01", "Fridge, retro", FRIDGE, "retro kitchen cream rounded new cold single-door", "fridge")
_a("GI_Fridge_Damaged_01", "Fridge, rusty", FRIDGE, "kitchen rusty damaged abandoned cold", "fridge")
_a("GI_Microwave_01", "Microwave", "appliances/kitchen/microwave", "classic kitchen new")
_a("GI_Wardrobe_01", "Wardrobe", "furniture/storage/wardrobe", "classic bedroom wood new", "wardrobe")
_a("GI_Wardrobe_Damaged_01", "Wardrobe, ruined", "furniture/storage/wardrobe", "bedroom wood damaged abandoned", "wardrobe")
_a("GI_Dresser_01", "Dresser", "furniture/storage/dresser", "classic bedroom wood new drawers")
_a("GI_Chest_01", "Chest", "furniture/storage/chest", "classic wood new lid trunk")
_a("GI_Locker_01", "Locker", "furniture/storage/locker", "classic metal new school gym")
_a("GI_Toolbox_01", "Toolbox", "farm/tools/toolbox", "rural workshop red metal new lid")
_a("GI_Mailbox_01", "Mailbox", "farm/structures/mailbox", "rural outdoor post new flap")
# furniture and decor in their styles
_a("GH_Sofa_Modern_01", "Sofa, modern", SOFA, "modern living-room grey new", "sofa")
_a("GH_Sofa_Retro_01", "Sofa, retro", SOFA, "retro living-room tufted new", "sofa")
_a("GH_Sofa_Damaged_01", "Sofa, slashed", SOFA, "living-room damaged abandoned", "sofa")
_a("GH_Armchair_Retro_01", "Armchair, retro", "furniture/seating/armchair", "retro living-room new")
_a("GH_Bed_Double_Modern_01", "Double bed, modern", "furniture/bedroom/bed", "modern bedroom new")
_a("GH_Bookcase_Modern_01", "Bookcase, modern", "furniture/storage/bookcase", "modern living-room shelves books new")
_a("GD_TV_Flat_Modern_01", "Flat-screen TV", "decor/electronics/tv", "modern living-room screen electronics new")
_a("GD_TableLamp_Retro_01", "Table lamp, retro", "decor/lighting/lamp", "retro lamp light new")
_a("GD_NeonSign_01", "Neon sign", "decor/lighting/neon-sign", "retro diner glow light red cyan new")
_a("GD_Clock_Wall_Retro_01", "Wall clock, retro", "decor/wall/clock", "retro wall time new")
_a("GD_PottedPlant_01", "Potted plant", "decor/plants/potted-plant", "plant green terracotta new")
# food
_a("FD_Apple_01", "Apple", "food/produce/apple", "fruit red fresh")
_a("FD_BananaBunch_01", "Bananas, bunch", "food/produce/banana", "fruit yellow bunch hand fresh")
_a("FD_Lemon_01", "Lemon", "food/produce/lemon", "fruit yellow citrus fresh")
_a("FD_Pear_01", "Pear", "food/produce/pear", "fruit green fresh")
_a("FD_Grapes_01", "Grapes", "food/produce/grapes", "fruit green bunch fresh")
_a("FD_Strawberry_01", "Strawberry", "food/produce/strawberry", "fruit red berry fresh")
_a("FD_BreadLoaf_01", "Loaf of bread", "food/bakery/bread", "baked fresh brown")
_a("FD_Pie_01", "Pie", "food/bakery/pie", "baked dessert fresh")
_a("FD_Hamburger_01", "Hamburger", "food/prepared/hamburger", "fast-food diner fresh")
_a("FD_SodaCan_Red_01", "Soda can", "food/drinks/soda-can", "drink soda can red metal new")
_a("FD_BeerCan_01", "Beer can", "food/drinks/beer-can", "drink beer can metal new")
_a("FD_BeerBottle_01", "Beer bottle", "food/drinks/beer-bottle", "drink beer bottle glass brown new")
_a("FD_WaterBottle_01", "Water bottle", "food/drinks/water-bottle", "drink water bottle plastic new")
_a("FD_WineBottle_01", "Wine bottle", "food/drinks/wine-bottle", "drink wine bottle glass green new")
_a("FD_WhiskeyBottle_01", "Whiskey bottle", "food/drinks/whiskey-bottle", "drink whiskey bottle glass brown new")
_a("FD_CoffeeCan_01", "Coffee can", "food/drinks/coffee-can", "coffee can metal red new")
_a("FD_Can_Soup_01", "Can of soup", "food/canned/soup", "canned soup can metal red new")
_a("FD_Can_Beans_01", "Can of beans", "food/canned/beans", "canned beans can metal new")
_a("FD_Jar_Pickles_01", "Jar of pickles", "food/canned/pickles", "canned pickles jar glass green new")
_a("FD_Jar_Jam_01", "Jar of jam", "food/canned/jam", "canned jam jar glass red new")
_a("FD_Ketchup_01", "Ketchup", "food/canned/ketchup", "condiment ketchup bottle red diner new")
_a("FD_Mustard_01", "Mustard", "food/canned/mustard", "condiment mustard bottle yellow diner new")
_a("FD_PeanutButter_01", "Peanut butter", "food/canned/peanut-butter", "canned peanut butter jar brown new")
_a("FD_CerealBox_01", "Cereal box", "food/boxed/cereal", "boxed cereal breakfast new")
_a("FD_PastaBox_01", "Pasta box", "food/boxed/pasta", "boxed pasta new")
_a("FD_CrackerBox_01", "Cracker box", "food/boxed/crackers", "boxed crackers snack new")
_a("FD_FlourSack_01", "Flour sack", "food/boxed/flour", "sack flour baking new")
_a("FD_SugarBag_01", "Sugar bag", "food/boxed/sugar", "bag sugar baking new")
_a("FD_ChipsBag_01", "Bag of chips", "food/boxed/chips", "bag chips snack new")
_a("FD_CandyBar_01", "Candy bar", "food/boxed/candy-bar", "candy bar sweet snack new")
_a("FD_DogBone_01", "Dog bone", "food/pet/dog-bone", "pet dog treat bone new")
_a("FD_CatFoodTin_01", "Cat food tin", "food/pet/cat-food", "pet cat tin new")
_a("FD_HayFlake_01", "Hay flake", "farm/feed/hay", "hay feed rural new")
_a("FD_SeedBag_01", "Seed bag", "food/pet/seed", "pet bird seed bag new")
_a("FD_Shirt_Hanger_01", "Shirt on a hanger", "clothing/garments/shirt", "clothes shirt hanger new")
_a("FD_Jacket_Hanger_01", "Jacket on a hanger", "clothing/garments/jacket", "clothes jacket hanger new")
_a("FD_Dress_Hanger_01", "Dress on a hanger", "clothing/garments/dress", "clothes dress hanger new")
_a("FD_Pants_Folded_01", "Stack of folded pants", "clothing/garments/pants", "clothes pants folded stack new")
_a("FD_Towel_Folded_01", "Stack of folded towels", "clothing/linen/towel", "towel folded stack bathroom new")
_a("FD_Shoes_Pair_01", "Pair of shoes", "clothing/footwear/shoes", "clothes shoes pair new")
_a("FD_Scarf_01", "Scarf", "clothing/accessories/scarf", "clothes scarf red new")
_a("FD_Orange_01", "Orange", "food/produce/orange", "fruit orange citrus fresh")
_a("FD_Banana_01", "Banana", "food/produce/banana", "fruit yellow single fresh")
_a("FD_Carrot_01", "Carrot", "food/produce/carrot", "vegetable orange root fresh")
_a("FD_Tomato_01", "Tomato", "food/produce/tomato", "vegetable fruit red fresh")
_a("FD_Potato_01", "Potato", "food/produce/potato", "vegetable brown root fresh")
_a("FD_Onion_01", "Onion", "food/produce/onion", "vegetable root fresh")
_a("FD_Corn_01", "Corn on the cob", "food/produce/corn", "vegetable yellow cob rural fresh")
_a("FD_Lettuce_01", "Lettuce", "food/produce/lettuce", "vegetable green salad fresh")
_a("FD_Cabbage_01", "Cabbage", "food/produce/cabbage", "vegetable green fresh")
_a("FD_Pumpkin_01", "Pumpkin", "food/produce/pumpkin", "vegetable orange rural fresh")
_a("FD_Watermelon_01", "Watermelon", "food/produce/watermelon", "fruit green large fresh")
_a("FD_Baguette_01", "Baguette", "food/bakery/baguette", "baked bread fresh brown")
_a("FD_Cake_01", "Cake", "food/bakery/cake", "baked dessert fresh")
_a("FD_Donut_01", "Donut", "food/bakery/donut", "baked dessert fresh diner")
_a("FD_CookieJar_01", "Cookie jar", "food/bakery/cookie-jar", "baked cookies jar fresh")
_a("FD_MilkCarton_01", "Milk carton", "food/dairy/milk-carton", "dairy milk white fresh")
_a("FD_MilkBottle_01", "Milk bottle", "food/dairy/milk-bottle", "dairy milk glass white fresh")
_a("FD_EggCarton_01", "Egg carton", "food/dairy/egg-carton", "dairy eggs carton fresh")
_a("FD_CheeseWedge_01", "Cheese wedge", "food/dairy/cheese", "dairy cheese yellow fresh")
_a("FD_Butter_01", "Butter", "food/dairy/butter", "dairy yellow fresh")
_a("FD_JuiceBox_01", "Juice box", "food/drinks/juice-box", "drink juice carton fresh")
_a("FD_Steak_01", "Steak", "food/prepared/steak", "meat red fresh")
_a("FD_Sausages_01", "Sausages", "food/prepared/sausages", "meat brown fresh")
_a("FD_Drumstick_01", "Drumstick", "food/prepared/drumstick", "meat chicken brown fresh")
_a("FD_TurkeyRoast_01", "Roast turkey", "food/prepared/turkey-roast", "meat turkey roast brown fresh")
_a("FD_Fish_01", "Fish", "food/prepared/fish", "fish grey fresh")
_a("FD_HotDog_01", "Hot dog", "food/prepared/hot-dog", "fast-food diner fresh")
_a("FD_PizzaBox_01", "Pizza box", "food/prepared/pizza-box", "fast-food box takeout fresh")
_a("FD_Sandwich_01", "Sandwich", "food/prepared/sandwich", "bread lunch fresh")
_a("FD_TVDinner_01", "TV dinner", "food/prepared/tv-dinner", "frozen meal tray fresh")
# farm
_a("GT_Barrel_01", "Barrel", "farm/props/barrel", "rural wood container new")
_a("GT_Wheelbarrow_01", "Wheelbarrow", "farm/tools/wheelbarrow", "rural tool new")
_a("GT_HayBale_Round_01", "Round hay bale", "farm/props/hay-bale", "rural hay yellow new")
_a("GT_Rake_01", "Rake", "tools/garden/rake", "rake garden steel wood new farm rural")
_a("GT_Shovel_01", "Shovel", "tools/garden/shovel", "shovel garden steel wood new farm rural")
_a("GT_Pitchfork_01", "Pitchfork", "tools/garden/pitchfork", "pitchfork hay steel wood new farm rural")
_a("GT_Crate_01", "Wooden crate", "farm/props/crate", "crate wood storage new farm rural")
_a("GT_MilkCan_01", "Milk can", "farm/props/milk-can", "milk can metal dairy new farm rural")
_a("GT_HayBale_Square_01", "Square hay bale", "farm/props/hay-bale-square", "hay bale square yellow new farm rural")
_a("GT_Jerrycan_01", "Jerrycan", "farm/props/jerrycan", "jerrycan fuel red metal new farm garage")
_a("GT_FeedSack_01", "Feed sack", "farm/props/feed-sack", "feed sack grain cream new farm rural")
_a("GT_Stool_01", "Stool", "farm/props/stool", "stool wood four-legged new farm rural")
_a("GT_FirewoodStack_01", "Firewood stack", "farm/props/firewood-stack", "firewood stack wood new farm cabin")
_a("GT_FirewoodStack_Triangle_01", "Firewood stack, triangular", "farm/props/firewood-stack-triangle", "firewood stack wood new farm cabin")
_a("GT_FirewoodStack_Small_01", "Firewood stack, small", "farm/props/firewood-stack-small", "firewood stack wood small new farm cabin")
_a("GT_FirewoodPile_Loose_01", "Firewood, loose pile", "farm/props/firewood-pile", "firewood pile wood loose new farm cabin")
_a("GT_ChoppingBlock_01", "Chopping block", "farm/props/chopping-block", "chopping block stump wood new farm cabin")
_a("GI_FenceSection_01", "Fence section", "farm/structures/fence-section", "fence section wood grey new farm rural")
_a("GI_Gate_01", "Gate", "farm/structures/gate", "gate fence wood tan new farm rural")
_a("GT_MailboxPost_01", "Mailbox on a post", "farm/structures/mailbox-post", "mailbox post metal new farm rural suburban")
_a("GL_BareBulb_01", "Bare bulb", "fixtures/outdoor/bare-bulb", "bulb light lamp barn shed new farm")
_a("GL_PoleLamp_01", "Pole lamp", "fixtures/outdoor/pole-lamp", "lamp pole light street yard new rural")
_a("GE_LandlinePhone_01", "Landline phone", "decor/electronics/landline-phone", "phone landline telephone desk kitchen new")
_a("GL_UtilityPole_01", "Utility pole", "fixtures/utilities/utility-pole", "utility pole power wood new rural")
_a("GL_UtilityPoleCorner_01", "Utility pole, corner", "fixtures/utilities/utility-pole-corner", "utility pole corner power wood new rural")
_a("GL_UtilityPoleTransformer_01", "Utility pole with transformer", "fixtures/utilities/utility-pole-transformer", "utility pole transformer power wood new rural")
_a("GL_ServiceEntry_01", "Electric service entry", "fixtures/utilities/service-entry", "service entry meter power electric new farm house")
_a("GL_FloodlightStand_01", "Floodlight stand", "fixtures/outdoor/floodlight-stand", "floodlight tripod light fbi new outdoor")
_a("FM_Generator_01", "Generator", "farm/props/generator", "generator power engine metal new farm rural")
_a("FM_WaterTrough_01", "Water trough", "farm/props/water-trough", "trough water animal wood new farm rural")
_a("GT_Hammer_01", "Claw hammer", "tools/hand/hammer", "hammer claw steel wood new workshop garage")
_a("GT_Sledgehammer_01", "Sledgehammer", "tools/hand/sledgehammer", "sledgehammer maul steel wood new workshop farm")
_a("GT_Axe_01", "Axe", "tools/hand/axe", "axe felling steel wood new woodshed cabin")
_a("GT_HandSaw_01", "Hand saw", "tools/hand/hand-saw", "saw handsaw steel wood new workshop")
_a("GT_Wrench_01", "Wrench", "tools/hand/wrench", "wrench spanner steel new workshop garage")
_a("GT_Screwdriver_01", "Screwdriver", "tools/hand/screwdriver", "screwdriver yellow steel new workshop")
_a("GT_Pliers_01", "Pliers", "tools/hand/pliers", "pliers steel rubber new workshop garage")
_a("GT_Hoe_01", "Hoe", "tools/garden/hoe", "hoe garden steel wood new farm")
_a("GT_Spade_01", "Spade", "tools/garden/spade", "spade shovel garden steel wood new farm")
_a("GT_WateringCan_01", "Watering can", "tools/garden/watering-can", "watering can galvanised garden new farm")
_a("GT_Plunger_01", "Plunger", "tools/household/plunger", "plunger rubber wood new bathroom kitchen")
_a("GT_RopeCoil_01", "Rope coil", "tools/workshop/rope-coil", "rope coil tan new barn farm")
_a("GT_Sawhorse_01", "Sawhorse", "tools/workshop/sawhorse", "sawhorse wood new workshop garage")
_a("GT_PaintCan_01", "Paint can", "tools/workshop/paint-can", "paint can yellow metal new garage shed")
_a("GT_PruningShears_01", "Pruning shears", "tools/garden/pruning-shears", "pruning shears secateurs red steel new garden")
_a("GT_FirePoker_01", "Fire poker", "tools/household/fire-poker", "poker fireplace iron new cabin")
_a("GT_HoseCoil_01", "Garden hose, coiled", "tools/garden/hose", "hose garden coiled green brass new farm")
_a("GT_Sprinkler_01", "Lawn sprinkler", "tools/garden/sprinkler", "sprinkler lawn garden yellow steel new suburban")
_a("GT_CordReel_01", "Extension cord reel", "tools/workshop/cord-reel", "extension cord reel orange yellow new garage")
_a("GT_HandTruck_01", "Hand truck", "tools/workshop/hand-truck", "hand truck dolly blue steel new warehouse")
_a("GT_Mallet_01", "Rubber mallet", "tools/hand/mallet", "mallet rubber wood new workshop garage")
_a("GT_ClothesIron_01", "Clothes iron", "tools/household/clothes-iron", "iron clothes steam white black new laundry")
_a("GT_BathroomScale_01", "Bathroom scale", "tools/household/bathroom-scale", "scale bathroom white weight new")
_a("GT_CordlessDrill_01", "Cordless drill", "tools/workshop/cordless-drill", "drill cordless power yellow black new workshop garage")
_a("GT_BenchVise_01", "Bench vise", "tools/workshop/bench-vise", "vise bench red cast-iron new workshop garage")
_a("GT_SnowShovel_01", "Snow shovel", "tools/garden/snow-shovel", "snow shovel blue wood new winter")
_a("GT_CarBattery_01", "Car battery", "tools/workshop/car-battery", "battery car black new garage")
_a("GT_BootScraper_01", "Boot scraper", "tools/household/boot-scraper", "boot scraper iron black new porch farm")
_a("GT_ToiletBrush_01", "Toilet brush", "tools/household/toilet-brush", "toilet brush white black new bathroom")
_a("GT_WorkLight_01", "Clip-on work light", "tools/workshop/work-light", "work light clamp steel yellow new garage")
_a("FM_Scarecrow_01", "Scarecrow", "farm/props/scarecrow", "rural field straw weathered")
_a("FM_DogHouse_01", "Doghouse", "farm/structures/doghouse", "rural wood new")
# buildings (art/scripts/buildings.py): one skin each (the other skins are not built and have no paints yet, see docs/assets/briefs/buildings.md); the New / Damaged pairs are variants of each other
_a("FM_Farmhouse_01", "Farmhouse", "building/farm/farmhouse", "rural farm house two-storey porch white siding exterior new", "farmhouse")
_a("FM_Farmhouse_Damaged_01", "Farmhouse, wrecked", "building/farm/farmhouse", "rural farm house two-storey porch exterior damaged abandoned ruined", "farmhouse")
_a("FM_Barn_01", "Barn", "building/farm/barn", "rural farm red hayloft livestock storage exterior new", "barn")
_a("FM_Barn_Damaged_01", "Barn, wrecked", "building/farm/barn", "rural farm hayloft livestock storage exterior damaged abandoned ruined", "barn")
_a("FM_Workshop_01", "Workshop", "building/farm/workshop", "rural farm garage metal tools exterior new", "workshop")
_a("FM_Workshop_Damaged_01", "Workshop, wrecked", "building/farm/workshop", "rural farm garage metal tools exterior damaged abandoned ruined", "workshop")
_a("FM_Shed_01", "Shed", "building/farm/shed", "rural farm garden storage exterior new", "shed")
_a("FM_Shed_Damaged_01", "Shed, wrecked", "building/farm/shed", "rural farm garden storage exterior damaged abandoned ruined", "shed")
_a("FM_ChickenCoop_01", "Chicken coop", "building/farm/coop", "rural farm livestock chickens red exterior new")
_a("FM_Outhouse_01", "Outhouse", "building/farm/outhouse", "rural farm toilet wood exterior new")
_a("FM_Well_01", "Well", "building/farm/well", "rural farm water stone exterior new")
_a("FM_Silo_01", "Silo", "building/farm/silo", "rural farm grain tower metal exterior new")
_a("FM_Windmill_01", "Windmill", "building/farm/windmill", "rural farm water pump tower white exterior new")
_a("GB_Trailer_01", "Mobile home", "building/town/trailer", "trailer-park home single-wide beige exterior new", "trailer")
_a("GB_Trailer_Damaged_01", "Mobile home, wrecked", "building/town/trailer", "trailer-park home single-wide exterior damaged abandoned ruined", "trailer")
_a("GB_Garage_01", "Garage", "building/town/garage", "suburban town car white exterior new", "garage")
_a("GB_Garage_Damaged_01", "Garage, wrecked", "building/town/garage", "suburban town car exterior damaged abandoned ruined", "garage")
_a("GB_TownHouse_01", "Town house", "building/town/house", "urban town brick two-storey exterior new", "town-house")
_a("GB_TownHouse_Damaged_01", "Town house, wrecked", "building/town/house", "urban town two-storey exterior damaged abandoned ruined", "town-house")
_a("GB_Diner_01", "Diner", "building/town/diner", "retro town restaurant cream exterior new", "diner")
_a("GB_Diner_Damaged_01", "Diner, wrecked", "building/town/diner", "retro town restaurant exterior damaged abandoned ruined", "diner")
# building kit and nature
_a("GK_Wall_Window_Brick_01", "Window wall, brick", "building/kit/wall-window", "urban brick red new modular", "wall-window")
_a("GK_Wall_Window_Barn_01", "Window wall, siding", "building/kit/wall-window", "rural barn red new modular", "wall-window")
_a("GK_Door_Exterior_01", "Exterior door", "building/kit/door", "classic wood new modular")
_a("FM_TreeOak_01", "Oak tree", "nature/trees/oak", "rural tree green plant big")
_a("FM_TreePine_01", "Pine tree", "nature/trees/pine", "rural tree green plant conifer")


# ===== Room and interior assets (tools/catalog_rooms.py) =============================================================
import catalog_rooms  # noqa: E402

BUILD.update(catalog_rooms.BUILD_ROOMS)
for _id, _r in catalog_rooms.ASSETS_ROOMS.items():
    _a(_id, _r["name"], _r["type"], _r["tags"], _r["group"])
