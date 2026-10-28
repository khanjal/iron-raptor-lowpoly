"""Lights, sounds and switches on props: what makes a lamp a lamp the crew can turn off, a radio an alien can possess, a fridge hum.

Every prop built by props_lib.Prop is checked against SPECS when it finishes (Prop.finish calls apply()): the spec for its base name
(GD_TableLamp_Modern_01 -> "TableLamp") adds marker empties to the exported model and entries to art/data/interactions.json. Nothing
here makes a sound or lights anything in Blender: the markers say WHERE and the info says WHAT, and a Unity component (`PropRuntime`, Assets/Scripts/Props) reads them: a `Light_<name>` empty becomes a Light, a `Sound_<name>` an AudioSource, a `Switch_<name>` an
interaction point that toggles what it `controls`.

Marker kinds
  light   colour (a name: warm, cool, red, green, pink, flame), range (m), intensity, shape (point/spot), flicker, when
  sound   event (the clip's name), loop, loudness (0..1: how far it carries; humans within it investigate), when
  switch  controls (names of the lights and sounds it toggles, or "power" / "room_lights" for the building), action (toggle/press/pull),
          by (who can use it: human, alien, energy_being, shadow_entity, grey)
`when` is "on" (while the thing is switched on), "trigger" (a one-off: a ding, a ring), "door_open" (a fridge light) or "always".

Traits (on the whole prop, for the alien abilities in game.md)
  power     needs electricity: the fuse box switches it all off
  possess   an Energy Being can take control of it (radios, phones, cameras, TVs, cars)
  jam       an Energy Being can jam it (a phone cannot call for backup)
  blackout  a Shadow Entity can switch it off from a distance (lights)
  noisy     it makes noise when it runs: sounds carry to humans

Positions are `frac` = (fx, fy, fz) of the model's bounding box (fy = 0 is the front, -Y), so a spec does not depend on the exact size or
style; the Damaged styles add working = False to every marker (a broken lamp, a dead TV).
"""

import re

L = "light"
S = "sound"
W = "switch"


def light(name, frac, colour="warm", range=4.0, intensity=1.0, flicker=False, when="on", shape="point"):
    return (L, name, frac, {"colour": colour, "range": range, "intensity": intensity, "flicker": flicker, "when": when, "shape": shape})


def sound(name, frac, event, loop=False, loudness=0.3, when="on"):
    return (S, name, frac, {"event": event, "loop": loop, "loudness": loudness, "when": when})


def switch(name, frac, controls, action="toggle", by=("human", "alien")):
    return (W, name, frac, {"controls": list(controls), "action": action, "by": list(by)})


LAMP = ("power", "blackout")
SCREEN = ("power", "possess", "noisy")
RADIO = ("power", "possess", "jam", "noisy")
PHONE = ("possess", "jam", "noisy")
FIRE = ("noisy",)

SPECS = {
    # ----- lamps (decor.py) -----
    "TableLamp": ([light("Bulb", (0.5, 0.5, 0.8), range=5), switch("Switch", (0.6, 0.5, 0.25), ["Bulb"])], LAMP),
    "FloorLamp": ([light("Bulb", (0.5, 0.5, 0.88), range=6), switch("Switch", (0.5, 0.5, 0.7), ["Bulb"])], LAMP),
    "DeskLamp": ([light("Bulb", (0.5, 0.3, 0.85), range=4, shape="spot"), switch("Switch", (0.5, 0.5, 0.1), ["Bulb"])], LAMP),
    "CeilingShade": ([light("Bulb", (0.5, 0.5, 0.3), range=6)], LAMP),
    "Fluorescent": ([light("Tube", (0.5, 0.5, 0.5), colour="cool", range=7, flicker=True), sound("Buzz", (0.5, 0.5, 0.5), "buzz", loop=True, loudness=0.1)], LAMP + ("noisy",)),
    "Chandelier": ([light("Bulbs", (0.5, 0.5, 0.4), range=8)], LAMP),
    "KeroseneLamp": ([light("Flame", (0.5, 0.5, 0.65), colour="flame", range=4, flicker=True)], ()),
    "Candle": ([light("Flame", (0.5, 0.5, 0.95), colour="flame", range=2.5, flicker=True)], ()),
    "NeonSign": ([light("Glow", (0.5, 0.5, 0.5), colour="pink", range=5, flicker=True), sound("Buzz", (0.5, 0.5, 0.5), "neon_buzz", loop=True, loudness=0.15)], LAMP + ("noisy",)),
    "LightSwitch": ([switch("Toggle", (0.5, 0.5, 0.5), ["room_lights"], by=("human", "alien", "shadow_entity"))], ("power",)),
    # ----- electronics (decor.py) -----
    "TV_CRT": ([light("Screen", (0.45, 0.0, 0.55), colour="cool", range=4, flicker=True), sound("Audio", (0.45, 0.3, 0.5), "tv", loop=True, loudness=0.4),
                switch("Power", (0.85, 0.0, 0.15), ["Screen", "Audio"])], SCREEN),
    "TV_Flat": ([light("Screen", (0.5, 0.0, 0.5), colour="cool", range=4), sound("Audio", (0.5, 0.3, 0.5), "tv", loop=True, loudness=0.4),
                 switch("Power", (0.9, 0.0, 0.05), ["Screen", "Audio"])], SCREEN),
    "Radio_Retro": ([sound("Audio", (0.5, 0.3, 0.5), "radio", loop=True, loudness=0.35), switch("Knob", (0.8, 0.0, 0.5), ["Audio"])], RADIO),
    "Radio_CB": ([sound("Audio", (0.5, 0.3, 0.5), "cb_chatter", loop=True, loudness=0.3), switch("Knob", (0.8, 0.0, 0.5), ["Audio"])], RADIO),
    "Radio_Handheld": ([sound("Audio", (0.5, 0.5, 0.6), "radio", loop=True, loudness=0.2), switch("Knob", (0.5, 0.5, 0.9), ["Audio"])], RADIO),
    "MobilePhone": ([sound("Ring", (0.5, 0.5, 0.5), "mobile_ring", loudness=0.45, when="trigger")], PHONE),
    "RotaryPhone": ([sound("Ring", (0.5, 0.5, 0.5), "bell_ring", loudness=0.6, when="trigger")], PHONE),
    "SecurityCamera": ([light("Led", (0.5, 0.0, 0.5), colour="red", range=0.5, intensity=0.3), sound("Servo", (0.5, 0.5, 0.5), "servo", loudness=0.1, when="trigger")], ("power", "possess")),
    "Monitor": ([light("Screen", (0.5, 0.0, 0.6), colour="cool", range=3), sound("Fan", (0.5, 0.6, 0.3), "fan", loop=True, loudness=0.05)], ("power", "possess")),
    "ComputerTower": ([light("Led", (0.5, 0.0, 0.8), colour="green", range=0.5, intensity=0.3), sound("Fan", (0.5, 0.5, 0.5), "fan", loop=True, loudness=0.1)], ("power", "possess")),
    "Laptop": ([light("Screen", (0.5, 0.8, 0.6), colour="cool", range=3)], ("power", "possess")),
    "Intercom": ([sound("Buzzer", (0.5, 0.0, 0.5), "buzzer", loudness=0.4, when="trigger"), switch("Button", (0.5, 0.0, 0.3), ["Buzzer"], action="press")], ("power", "possess", "jam")),
    # ----- kitchen and house (household.py, home_styles.py, interactive.py) -----
    "Fridge": ([light("Inside", (0.5, 0.4, 0.6), colour="cool", range=1.5, when="door_open"), sound("Hum", (0.5, 0.8, 0.3), "fridge_hum", loop=True, loudness=0.12)], ("power", "noisy")),
    "GH_Fridge": ([sound("Hum", (0.5, 0.8, 0.3), "fridge_hum", loop=True, loudness=0.12)], ("power", "noisy")),        # the household fridge has no door part
    "Stove": ([light("OvenLight", (0.5, 0.3, 0.4), range=1.0), sound("Click", (0.5, 0.0, 0.8), "knob_click", loudness=0.1, when="trigger"), switch("Knob", (0.5, 0.0, 0.8), ["OvenLight"], action="press")], ("power",)),
    "Microwave": ([light("Inside", (0.4, 0.4, 0.5), range=1.0), sound("Hum", (0.5, 0.5, 0.5), "microwave", loop=True, loudness=0.3), sound("Ding", (0.5, 0.5, 0.5), "ding", loudness=0.35, when="trigger"),
                   switch("Start", (0.85, 0.0, 0.5), ["Inside", "Hum", "Ding"], action="press")], ("power", "noisy")),
    "Toaster": ([light("Glow", (0.5, 0.5, 0.7), colour="red", range=0.5), sound("Pop", (0.5, 0.5, 0.8), "toast_pop", loudness=0.2, when="trigger")], ("power",)),
    "Washer": ([sound("Spin", (0.5, 0.5, 0.5), "washer", loop=True, loudness=0.35)], ("power", "noisy")),
    "Dryer": ([sound("Tumble", (0.5, 0.5, 0.5), "washer", loop=True, loudness=0.3)], ("power", "noisy")),
    "VendingMachine": ([light("Panel", (0.4, 0.0, 0.6), colour="cool", range=4), sound("Hum", (0.5, 0.5, 0.5), "vending_hum", loop=True, loudness=0.25), sound("Clunk", (0.4, 0.0, 0.1), "clunk", loudness=0.4, when="trigger")], ("power", "noisy", "jam")),
    "ArcadeUpright": ([light("Screen", (0.5, 0.1, 0.7), colour="cool", range=3), sound("Attract", (0.5, 0.3, 0.6), "arcade", loop=True, loudness=0.4)], ("power", "noisy")),
    "ArcadeCocktail": ([light("Screen", (0.5, 0.5, 0.93), colour="cool", range=3), sound("Attract", (0.5, 0.5, 0.6), "arcade", loop=True, loudness=0.4)], ("power", "noisy")),
    "Pinball": ([light("Backglass", (0.5, 0.75, 0.85), colour="warm", range=3), sound("Attract", (0.5, 0.5, 0.6), "pinball", loop=True, loudness=0.5)], ("power", "noisy")),
    "Jukebox": ([light("Glow", (0.5, 0.0, 0.6), colour="warm", range=4), sound("Music", (0.5, 0.3, 0.5), "jukebox", loop=True, loudness=0.7)], ("power", "noisy")),
    "CoffeeMachine": ([sound("Brew", (0.5, 0.5, 0.4), "brew", loop=True, loudness=0.2), light("Led", (0.5, 0.0, 0.5), colour="red", range=0.3, intensity=0.3)], ("power", "noisy")),
    "AirConditioner": ([sound("Hum", (0.5, 0.5, 0.5), "ac_hum", loop=True, loudness=0.3)], ("power", "noisy")),
    "Boiler": ([sound("Rumble", (0.5, 0.5, 0.4), "boiler", loop=True, loudness=0.25)], ("power", "noisy")),
    "WaterHeater": ([sound("Rumble", (0.5, 0.5, 0.4), "boiler", loop=True, loudness=0.2)], ("power", "noisy")),
    "Fireplace": ([light("Fire", (0.5, 0.5, 0.2), colour="flame", range=6, flicker=True), sound("Crackle", (0.5, 0.5, 0.2), "fire_crackle", loop=True, loudness=0.2)], FIRE),
    "WoodStove": ([light("Fire", (0.5, 0.0, 0.3), colour="flame", range=4, flicker=True), sound("Crackle", (0.5, 0.5, 0.3), "fire_crackle", loop=True, loudness=0.2)], FIRE),
    "FuseBox": ([sound("Clunk", (0.5, 0.0, 0.5), "breaker", loudness=0.3, when="trigger"),
                 switch("MainBreaker", (0.5, 0.0, 0.4), ["power", "Clunk"], action="pull", by=("human", "alien", "energy_being", "shadow_entity"))], ("power",)),
    "ServerRack": ([light("Leds", (0.5, 0.0, 0.6), colour="green", range=2, flicker=True), sound("Fans", (0.5, 0.5, 0.5), "server_fans", loop=True, loudness=0.3)], ("power", "possess", "noisy")),
    "Radiator": ([sound("Tick", (0.5, 0.5, 0.5), "radiator_tick", loudness=0.08, when="trigger")], ()),
    "Toilet": ([sound("Flush", (0.5, 0.8, 0.8), "flush", loudness=0.35, when="trigger"), switch("Handle", (0.5, 0.9, 0.8), ["Flush"], action="press")], ("noisy",)),
    "Sink_Bath": ([sound("Water", (0.5, 0.6, 0.8), "tap_water", loop=True, loudness=0.2), switch("Tap", (0.5, 0.8, 0.9), ["Water"])], ("noisy",)),
    "Sink_Kitchen": ([sound("Water", (0.3, 0.6, 0.9), "tap_water", loop=True, loudness=0.2), switch("Tap", (0.3, 0.8, 0.95), ["Water"])], ("noisy",)),
    "Shower": ([sound("Water", (0.5, 0.5, 0.8), "shower", loop=True, loudness=0.3), switch("Tap", (0.5, 0.9, 0.5), ["Water"])], ("noisy",)),
    "Tub": ([sound("Water", (0.5, 0.5, 0.5), "tap_water", loop=True, loudness=0.25), switch("Tap", (0.9, 0.5, 0.8), ["Water"])], ("noisy",)),
    "Microscope": ([light("Lamp", (0.5, 0.5, 0.2), range=1.0, intensity=0.5)], ("power",)),
    # ----- the farm (props_farm.py) -----
    "Generator": ([sound("Engine", (0.5, 0.5, 0.5), "generator", loop=True, loudness=0.7), switch("Pull", (0.5, 0.0, 0.7), ["Engine", "power"], action="pull")], ("noisy",)),
    "PoleLamp": ([light("Lamp", (0.5, 0.17, 0.95), range=12, intensity=1.4)], ("power", "blackout")),
    "BareBulb": ([light("Bulb", (0.5, 0.5, 0.05), range=5, intensity=0.9)], ("power", "blackout")),
    "LandlinePhone": ([sound("Ring", (0.5, 0.5, 0.5), "bell_ring", loudness=0.6, when="trigger")], PHONE),
    "Mailbox": ([sound("Flag", (0.8, 0.5, 0.8), "flag_clank", loudness=0.1, when="trigger")], ()),
}

_STYLES = "Modern|Retro|Damaged|Classic|Smashed|Fallen|Torn|Tipped|Overturned"
_TRAILING_STYLE = re.compile(r"_(" + _STYLES + r")$")
_BROKEN = ("_Damaged_", "_Smashed_", "_Fallen_", "_Torn_", "_Tipped_", "_Overturned_")


def candidates(name):
    """Names to look up in SPECS, most specific first: GD_Radio_Retro_Retro_01 -> GD_Radio_Retro_Retro, Radio_Retro_Retro, GD_Radio_Retro,
    Radio_Retro, GD_Radio, Radio (a style suffix is dropped one at a time, each with and without the two-letter prefix). So "Radio_Retro"
    is a prop of its own while "_Retro" on a Fridge is a style, and a key such as "GH_Fridge" can single out one script's version."""
    cur = re.sub(r"_01$", "", name)
    out = []
    while True:
        out.append(cur)
        if "_" in cur:
            out.append(cur.split("_", 1)[1])
        m = _TRAILING_STYLE.search(cur)
        if m is None:
            break
        cur = cur[:m.start()]
    return out


def apply(prop):
    """Add the emitters and traits that SPECS has for this prop (see candidates()). Called by Prop.finish()."""
    spec = next((SPECS[c] for c in candidates(prop.name) if c in SPECS), None)
    if spec is None or prop.emitters:
        return
    markers, traits = spec
    working = not any(token in prop.name for token in _BROKEN)
    for kind, name, frac, info in markers:
        info = dict(info)
        if not working:
            info["working"] = False                      # a broken lamp, a dead TV: the runtime leaves it off
        prop.emit(kind, name, frac=frac, **info)
    prop.trait(*traits)
