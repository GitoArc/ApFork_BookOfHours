from __future__ import annotations

from typing import TYPE_CHECKING

from rule_builder.rules import HasAny, Has
from worlds.generic.Rules import add_rule, set_rule
from .jsondump import terrains

if TYPE_CHECKING:
    from .world import BoHWorld


def set_all_rules(world: BoHWorld) -> None:
    # Note: Regions do not have rules, the Entrances connecting them do!
    # We'll do entrances first, then locations, and then finally we set our victory condition.
    set_all_entrance_rules(world)
    set_all_location_rules(world)
    set_completion_condition(world)


def set_all_entrance_rules(world: BoHWorld) -> None:
    entrances = [n for n in world.get_entrances() if "Menu" not in n.name]

    for n in entrances:
        # since every terrain has its name as event-item; require it to proceed
        #world.set_rule(n, HasAny(n.parent_region.name))
        pass

def set_all_location_rules(world: BoHWorld) -> None:
    if world.options.memory_progression.is_enabled:
        locs_memory_progression = [a for a in world.get_locations() if "Remember" in a.name and " memories" in a.name]
        max = world.options.memory_progression["locations"]
        goal = world.options.memory_progression["goal"]
        for i in range(2, 1+max):
            locs = [a for a in locs_memory_progression if f"Remember {i} memor" in a.name]
            for l in locs:
                # is such finely-grained detail necessary? If you can get 2 memories you can get 3/4/40... etc
                #world.set_rule(l, Has("Progressive Memory", count=i-1))
                pass
            pass
        [goal_memory_loc] = [a for a in world.get_locations() if "oal" in a.name]
        #world.set_rule(goal_memory_loc, Has("Progressive Memory", count=goal))
        pass



def set_completion_condition(world: BoHWorld) -> None:
    # Finally, we need to set a completion condition for our world, defining what the player needs to win the game.
    # You can just set a completion condition directly like any other condition, referencing items the player receives:
    world.multiworld.completion_condition[world.player] = lambda state: state.has_all(("Sword", "Shield"), world.player)

    # In our case, we went for the Victory event design pattern (see create_events() in locations.py).
    # So lets undo what we just did, and instead set the completion condition to:
    world.multiworld.completion_condition[world.player] = lambda state: True
    world.set_completion_rule(Has("Victory Shard", count=1))
