from __future__ import annotations

import re
from typing import TYPE_CHECKING

from BaseClasses import ItemClassification, CollectionState, Location, Entrance, DEFAULT_COLLECTION_RULE
from .enums import BOHStrEnums
from .items import BOHItem
from .jsondump import terrains, memories, memories_post_house, books
from ..generic.Rules import add_rule
from ..sc2 import DEFAULT_LOCATION_LIST

if TYPE_CHECKING:
    from .world import BOHWorld


def set_all_rules(world: BOHWorld) -> None:
    # Note: Regions do not have rules, the Entrances connecting them do!
    set_all_entrance_rules(world)
    set_all_location_rules(world)
    set_completion_condition(world)
    pass


def set_all_entrance_rules(world: BOHWorld) -> None:

    for t in terrains:
        try:
            r = world.get_entrance(f"Entr_{t.Label}")
            r.access_rule = lambda state: state.has(BOHStrEnums.VillagerAssistance, world.player)
        except KeyError as E:
            pass

    world.get_entrance(f"Entr_{BOHStrEnums.StBrandansCove}").access_rule = DEFAULT_COLLECTION_RULE
    world.get_entrance(f"Entr_{BOHStrEnums.KeepersLodge}").access_rule = DEFAULT_COLLECTION_RULE
    world.get_entrance(f"Entr_{BOHStrEnums.BrancrugVillage}").access_rule = lambda state: state.has(BOHStrEnums.FishermanAssistance,world.player) and state.has(BOHStrEnums.VillageFriend, world.player)
    world.get_entrance(f"Entr_{BOHStrEnums.WatchmansTowerGatehouse}").access_rule = lambda state: state.has(BOHStrEnums.HushHouseKey, world.player)


def get_books_in_state(world: BOHWorld):
    bs = [book
          for item_name in world.multiworld.state.prog_items[world.player]
          for book in books
          if item_name == book.Label]
    pass

def set_location_rules_for_books(world: BOHWorld) -> None:
    pass
    # User qwint: '... logic does not differentiate between "can reach" and "has reached" '
    # If I try smth like Loc{i}.rule = state.has("BOOKS", i-1)
    # the logic will instantly jump from 0 to end (collects 1 BOOK -> "Master 2 books" is now accessible (and thus also accessed)) -> has now 2 BOOKS -> "Master 3 books" unlocked,
    # - rendering this whole rule setup irrelevant.
    # No rules until it becomes a problem?

    #if world.options.booksanity.generic_progression_locations:
    #    for i in range(2, world.options.booksanity.generic_progression_locations):
    #        loc = world.get_location(f"Master {i} books")
    #        loc.access_rule = lambda state, l=i-1: state.has(f"EVENT_PROGRESSIVE_BOOKS_MASTERED_ANY", world.player, l)


def set_all_location_rules(world: BOHWorld) -> None:
    locations = [a for a in world.get_locations()]
    if world.options.memories.is_enabled:
        # basic memories (talk with villager / weather) can be acquired pre-house, but everything else requires read/craft/the HOUSE
        for m in memories_post_house:
            # !! f"Remember a {m.Label}" IN a.name  finds EarthquakeName/WeatherEquake; Find fix to avoid that
            for loc in [a for a in locations if re.match(f'Remember an? {m.Label}' , a.name)]:
                loc.access_rule = lambda state: state.can_reach(BOHStrEnums.WatchmansTowerGatehouse, "Region", world.player)

    if world.options.memory_progression.is_enabled:
        pass # event rules assigned on creation, check locations.py
    if world.options.booksanity:
        set_location_rules_for_books(world)

def set_completion_condition(world: BOHWorld) -> None:

    goals_sum = len([a for a in world.get_locations() if a.item and a.item.name == "Victory Shard"])
    world.set_completion_rule(lambda state: state.has("Victory Shard", world.player, goals_sum))
