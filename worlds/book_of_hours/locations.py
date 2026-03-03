from __future__ import annotations

from BaseClasses import Location, ItemClassification
from rule_builder.rules import Has
from . import items
from .generate_locations import *
from .items import BoHItem
from .jsondump import terrains

if TYPE_CHECKING:
    from .world import BoHWorld

# Every location must have a unique integer ID associated with it.
# We will have a lookup from location name to ID here that, in world.py, we will import and bind to the world class.
# Even if a location doesn't exist on specific options, it must be present in this lookup.
LOCATION_NAME_TO_ID = (MEMORIES_SPECIFIC | MEMORIES_PILE
                       | SOULS_SPECIFIC | SOULS_PILE
                       | TERRAINS_SPECIFIC | TERRAINS_PILE
                       | BOOKS_SPECIFIC | BOOKS_PILE
                       | CATALOG_PILE_ANY | CATALOG_PILE_DAWN | CATALOG_PILE_SOLAR | CATALOG_PILE_BARONIAL | CATALOG_PILE_CURIA | CATALOG_PILE_NOCTURNAL
                       | WISDOMS_SPECIFIC | WISDOMS_PILE
                       | LESSONS_SPECIFIC | LESSONS_PILE
                       | SKILLS_SPECIFIC | SKILLS_PILE)
pass


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


def extract_roman(a: str):
    i = 0

    core = a.split("'")
    if len(core) == 1:
        return 0

    core = a.split("'")[1]
    num = core.split(" ")[1]
    match num:
        case "I":
            i = 1
        case "II":
            i = 2
        case "III":
            i = 3
        case "IV":
            i = 4
        case "V":
            i = 5
        case "VI":
            i = 6
        case "VII":
            i = 7
        case "VIII":
            i = 8
        case "IX":
            i = 9
        case _:
            i = 0
    return i


def create_locations(world: BoHWorld) -> None:
    menu = world.get_region("Menu")

    def create_locations_option_memories() -> None:
        locations_wanted: int = world.options.memory_progression["locations"]
        rewards_per_loc: int = world.options.memory_progression["rewards_per_location"]

        if locations_wanted == 0:
            return
        if world.options.memory_progression.any_chance is False:
            raise ValueError(f"No progression possible when every chance is 0. Aborting...")

        # Time only starts after your introduction to the village acquantance.
        # Meaning 'weathers' are theoretically locked behind 'Brancrug Village Acquaintance'
        #  but basic, musics, ESPECIALLY lessons, etc... require the library rooms (or at MINIMUM the lodge)
        # just streamline everything post-lodge? or stick in menu?
        locs = {k: v
                for k, v in MEMORIES_PILE.items()
                for l in range(1, 1 + locations_wanted)
                for r in range(1, 1 + rewards_per_loc)
                if (f"Remember {l} " in k and f"Reward {r}" in k)}
        pass
        # The exact goal-number is checked in client
        goal = BoHLocation(world.player, "Goal - Remember X memories", None, menu)
        goal.place_locked_item(BoHItem("Victory Shard", ItemClassification.progression, None, world.player))
        menu.locations.append(goal)

        menu.add_locations(locs, BoHLocation)
        for k, v in MEMORIES_SPECIFIC.items():
            menu.locations.append(BoHLocation(world.player, k, v, menu))
        pass
        ### Verifaction"UniqueOnly" and Chance roll can only happen in client:
        # basics_chance = [world.options.memory_progression["basics_chance"] for i in range(0, len(memories_basic))]
        # weathers_chance = [world.options.memory_progression["weathers_chance"] for i in range(0, len(memories_weather)-2)]
        # weather_earthquake_chance = world.options.memory_progression["weather_earthquake_chance"]
        # weather_numa_chance = world.options.memory_progression["weather_numa_chance"]
        # lessons_chance = [world.options.memory_progression["lessons_chance"] for i in range(0, len(lessons))]
        # musics_chance = [world.options.memory_progression["musics_chance"]  for i in range(0, len(memories_music))]
        # persistents_chance = [world.options.memory_progression["persistents_chance"] for i in range(0, len(memories_persistent))]
        # leftovers_chance = [world.options.memory_progression["leftovers_chance"] for i in range(0, len(memories_leftovers))]
        # equake = [a for a in memories_weather if "quake" in a.Label][0]
        # numa = [a for a in memories_weather if "Nume-Brume" in a.Label][0]
        # normal_weathers = [a for a in memories_weather if not ("quake" in a.IdStr or "numa" in a.IdStr)]

        # pop = [*memories_basic, *normal_weathers, equake, numa, *lessons, *memories_music, *memories_persistent, *memories_leftovers]
        # weights = [*basics_chance, *weathers_chance, weather_earthquake_chance, weather_numa_chance, *lessons_chance, *musics_chance, *persistents_chance, *leftovers_chance]
        # sam = world.random.sample(pop, counts=weights, k=40)

    def create_locations_option_wisdoms() -> None:
        wt = world.get_region("The Tree of Wisdoms")
        reward_per_new_tier = 1
        reward_per_accum_progression = 1
        allowed_tiers_for_node_locations = "012"
        rewards_per_tier_reached = "012000000"
        rewards_per_node_location = "023000000"

        wt.add_locations({k: v for k, v in WISDOMS_PILE.items()}, BoHLocation)
        wt.add_locations({k: v for k, v in WISDOMS_TIERS.items()}, BoHLocation)
        wt.add_locations({k: v for k, v in WISDOMS_SPECIFIC.items()}, BoHLocation)

    ###menu.add_locations(get_location_names_with_ids([k for k in BOOKS.keys()]), BoHLocation)

    village = world.get_region("Brancrug Village")
    acquaint = BoHLocation(world.player, "Brancrug Village Acquaintance", None, village)
    acquaint.place_locked_item(
        BoHItem("Brancrug Village Acquaintance", ItemClassification.progression, None, world.player))
    village.locations.append(acquaint)
    journal = BoHLocation(world.player, "Dried Journal", None, village)
    journal.place_locked_item(BoHItem("Dried Journal", ItemClassification.progression, None, world.player))
    village.locations.append(journal)

    create_locations_option_memories()
    create_locations_option_wisdoms()

    # JSUT FOR DEBUG; THEY NEED PROPER CHAINING
    for k, v in TERRAINS_SPECIFIC.items():
        menu.locations.append(BoHLocation(world.player, k, v, menu))

    if False:
        for unlockname, apid in TERRAINS_SPECIFIC.items():
            normname = unlockname.replace("Unlocked the ", "")
            region = world.get_region(normname)
            if normname == "St Brandan’s Cove" and 1 == 0:
                region.add_event(normname, None, None, BoHLocation, BoHItem)
                #world.set_rule(world.get_location(normname), True_())
            else:
                # find what room can connect to this
                roads: list[str] = [c.Label for e in terrains for c in e.ConnectsTo if c == normname]
                region.add_event(normname, None, None, BoHLocation, BoHItem, False)
                #world.set_rule(world.get_location(normname), HasAny(*roads))

            region.add_locations({unlockname: apid}, BoHLocation)
            #world.set_rule(world.get_location(unlockname), Has(unlockname))


def create_events(world: BoHWorld) -> None:
    menu = world.get_region("Menu")
    lodge = world.get_region("Keeper's Lodge")
    goal = world.options.memory_progression["goal"]
    #menu.add_event("Victory Shard", "Victory Shard", None, BoHLocation, BoHItem)
    #world.set_rule(world.get_location("Victory Shard"), Has("progressive_memory", count=goal))

    if world.options.memory_progression.is_enabled:
        locations_wanted = world.options.memory_progression["locations"]
        for i in range(1, locations_wanted + 1):
            loc_name = f"event_memory_progression_{i}"
            menu.add_event(loc_name, "progressive_memory",
                           location_type=BoHLocation, item_type=items.BoHItem,
                           show_in_spoiler=False)
            world.set_rule(world.get_location(loc_name), Has("progressive_memory", count=i - 1))

        goal = world.options.memory_progression["goal"]
    if True: #wisdom tree
        wt = world.get_region("The Tree of Wisdoms")

        l = [a for a in jsondump.wisdomtree if "locus" not in a.IdStr]
        _root = [a for a in jsondump.wisdomtree if a.IdStr == "wt.memorylocus"][0]

        wt.add_event("__event_wt.memorylocus", "__event_wt.memorylocus", lambda state: state.can_reach_region("The Tree of Wisdoms", world.player), BoHLocation, BoHItem)
        for i in range(0, 9): # == 9 paths
            _current_idstr = l[0].IdStr[:-1]
            _all_of_path = [a for a in l if _current_idstr in a.IdStr]
            assert len(_all_of_path) == 9
            e = [a for a in _all_of_path if ".1" in a.IdStr][0]
            l.remove(e)
            wt.add_event("__event_"+e.IdStr, "__event_"+e.IdStr, lambda state: state.has("__event_wt.memorylocus", world.player), BoHLocation, BoHItem)
            for j in range (1+1, 1+9):
                e_next = [a for a in _all_of_path if str(j) in a.IdStr][0]
                l.remove(e_next)
                wt.add_event("__event_"+e_next.IdStr, "__event_"+e_next.IdStr, lambda state, s="__event_"+e.IdStr: state.has(s, world.player), BoHLocation, BoHItem)
                e = e_next
        assert len(l) == 0
