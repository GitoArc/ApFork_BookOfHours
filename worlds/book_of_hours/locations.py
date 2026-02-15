from __future__ import annotations

import random
from typing import TYPE_CHECKING

from BaseClasses import Location
from rule_builder.rules import HasAny, Has, True_
from . import items, jsondump
from .items import BoHItem
from .jsondump import terrains

if TYPE_CHECKING:
    from .world import BoHWorld

def process_label_memory(s:str):
    s = s.replace("Memory: ", "")
    # if vowel: 'a' or 'an'
    matches = ["a", "e", "i", "o", "u"]
    f = s[0:1].lower()
    if any([a in f for a in matches]):
        s = "an "+s
    else:
        s =  "a "+s
    return s
def process_label_soul(s:str):
    return f"a Part: {s}"
def process_label_lesson(s:str):
    #no access to world.random ... ¯\_(ツ)_/¯
    s = s.replace("Lesson:", "")
    s = random.choice(["of", "in", "about"]) + s
    return s

# Every location must have a unique integer ID associated with it.
# We will have a lookup from location name to ID here that, in world.py, we will import and bind to the world class.
# Even if a location doesn't exist on specific options, it must be present in this lookup.
LOCATION_NAME_TO_ID = {}

MEMORIES_SPECIFIC = {f"Remember a {a['Label']}" : a["ApId"] for a in jsondump.memories}
lastUsedId = max(MEMORIES_SPECIFIC.values())
MEMORIES_X = {f"Recall {i} memories": lastUsedId+i for i in range(1,21)} # essentially a daily progression

SOULS_SPECIFIC = {f"Acquire {a["Label"]}" : a["ApId"] for a in jsondump.souls}
lastUsedId = max(SOULS_SPECIFIC.values())
SOULS_X = {f"Acquire {i} Parts in total" : lastUsedId + i for i in range(1, 11)}

TERRAINS_SPECIFIC = {f"Unlocked the {a["Label"]}" : a["ApId"] for a in jsondump.terrains.values()}
lastUsedId = max(TERRAINS_SPECIFIC.values())
TERRAINS_X = {f"Unlock {i} terrains" : lastUsedId + i for i in range(1, 21)}

WISDOMS_SPECIFIC = {f"Attune {a["Label"]}" : a["ApId"] for a in jsondump.wisdomtree}
lastUsedId = max(WISDOMS_SPECIFIC.values())
WISDOMS_X = {f"Attune {i}" : lastUsedId + i for i in range(1, 19)}

BOOKS_SPECIFIC = {f"Mastered `{a["Label"]}`" : a["ApId"] for a in jsondump.books}
lastUsedId = max(BOOKS_SPECIFIC.values())
BOOKS_X = {f"Master {i} books": lastUsedId + i for i in range(1, 21)}
lastUsedId = max(BOOKS_X.values())
CATALOG_X_ANY = {f"Catalogue {i} books": lastUsedId + i for i in range(1, 21)}
lastUsedId = max(CATALOG_X_ANY.values())
CATALOG_X_DAWN = {f"Catalogue {i} books of the Dawn Period": lastUsedId+i for i in range(1, 3)}
lastUsedId = max(CATALOG_X_DAWN.values())
CATALOG_X_SOLAR = {f"Catalogue {i} books of the Solar Period": lastUsedId+i for i in range(1, 5)}
lastUsedId = max(CATALOG_X_SOLAR.values())
CATALOG_X_BARONIAL = {f"Catalogue {i} books of the Baronial Period": lastUsedId+i for i in range(1, 9)}
lastUsedId = max(CATALOG_X_BARONIAL.values())
CATALOG_X_CURIA = {f"Catalogue {i} books of the Curia period": lastUsedId+i for i in range(1, 17)}
lastUsedId = max(CATALOG_X_CURIA.values())
CATALOG_X_NOCTURNAL = {f"Catalogue {i} books of the Nocturnal period": lastUsedId+i for i in range(1, 33)}
lastUsedId = max(CATALOG_X_NOCTURNAL.values())

LESSONS_SPECIFIC = {f"{a["Label"]}" : a["ApId"] for a in jsondump.lessons}
LESSONS_X = {}

SKILLS_SPECIFIC = {"Skill: "+ a["Label"] : a["ApId"] for a in jsondump.skills}
SKILLS_X = {}

MEMORIES = MEMORIES_SPECIFIC | MEMORIES_X
SOULS = SOULS_SPECIFIC | SOULS_X
TERRAINS = TERRAINS_SPECIFIC | TERRAINS_X
BOOKS = BOOKS_SPECIFIC | BOOKS_X | CATALOG_X_ANY | CATALOG_X_DAWN | CATALOG_X_SOLAR | CATALOG_X_BARONIAL | CATALOG_X_CURIA | CATALOG_X_NOCTURNAL
WISDOMS = WISDOMS_SPECIFIC | WISDOMS_X
LESSONS = {}
# Lessons into Skill is sooo trivial (no condition; if you got the lesson, you got the skill in 30s)
# I think it's enough with either/or, but both seem redundant
SKILLS = SKILLS_SPECIFIC | SKILLS_X

LOCATION_NAME_TO_ID = LOCATION_NAME_TO_ID | MEMORIES | SOULS | TERRAINS | BOOKS | WISDOMS | LESSONS | SKILLS
x=0

class BoHLocation(Location):
    game = "Book of Hours"


# Let's make one more helper method before we begin actually creating locations.
# Later on in the code, we'll want specific subsections of LOCATION_NAME_TO_ID.
# To reduce the chance of copy-paste errors writing something like {"Chest": LOCATION_NAME_TO_ID["Chest"]},
# let's make a helper method that takes a list of location names and returns them as a dict with their IDs.
# Note: There is a minor typing quirk here. Some functions want location addresses to be an "int | None",
# so while our function here only ever returns dict[str, int], we annotate it as dict[str, int | None].
def get_location_names_with_ids(location_names: list[str]) -> dict[str, int | None]:
    return {location_name: LOCATION_NAME_TO_ID[location_name] for location_name in location_names}

def create_all_locations(world: BoHWorld) -> None:
    create_locations(world)
    create_events(world)

def create_locations(world: BoHWorld) -> None:
    # Finally, we need to put the Locations ("checks") into their regions.
    # Once again, before we do anything, we can grab our regions we created by using world.get_region()
    menu = world.get_region("Menu")
    menu.add_locations(get_location_names_with_ids([k for k in BOOKS.keys()]), BoHLocation)

    #beach1 = world.get_region("St Brandan’s Cove")
    #beach1.add_event("St Brandan’s Cove", "St Brandan’s Cove", lambda state: True, BoHLocation, BoHItem, False)
    #beach1.add_locations({"Unlocked St Brandan’s Cove": 1})

    for unlockname, apid in TERRAINS_SPECIFIC.items():
        normname = unlockname.replace("Unlocked the ", "")
        region = world.get_region(normname)
        if normname == "St Brandan’s Cove" and 1 == 0:
            region.add_event(normname, None, None, BoHLocation, BoHItem)
            #world.set_rule(world.get_location(normname), True_())
        else:
            # find what room can connect to this
            roads:list[str] = [e["Label"] for e in terrains.values() for c in e["ConnectsTo"] if c["Label"] == normname]
            region.add_event(normname, None, None, BoHLocation, BoHItem, False)
            #world.set_rule(world.get_location(normname), HasAny(*roads))

        region.add_locations({unlockname: apid}, BoHLocation)
        #world.set_rule(world.get_location(unlockname), Has(unlockname))


def create_events(world: BoHWorld) -> None:
    menu = world.get_region("Menu")

