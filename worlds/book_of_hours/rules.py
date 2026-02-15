from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import CollectionState
from rule_builder.rules import HasAny, Has
from worlds.generic.Rules import add_rule, set_rule
from .jsondump import terrains
from .options import RoomGoal

if TYPE_CHECKING:
    from .world import BoHWorld


def set_all_rules(world: BoHWorld) -> None:
    # In order for AP to generate an item layout that is actually possible for the player to complete,
    # we need to define rules for our Entrances and Locations.
    # Note: Regions do not have rules, the Entrances connecting them do!
    # We'll do entrances first, then locations, and then finally we set our victory condition.
    set_all_entrance_rules(world)
    set_all_location_rules(world)
    set_completion_condition(world)
    from rule_builder.rules import Has, And, Or, CanReachRegion
    all_state = world.multiworld.get_all_state(False)
    all_state.sweep_for_advancements()
    rule_a = Has("St Brandan’s Cove")
    rule_b = CanReachRegion("Brancrug Village")
    rule1 = And(rule_a, rule_b)
    rule0 = Or(rule_a, rule_b)
    w = world.multiworld.worlds[1]
    r1 = rule1.resolve(w)
    r0 = rule0.resolve(w)
    #print(r1.explain_str(all_state))
    #print(r0.explain_str(all_state))
    r = {a:a.access_rule for a in world.get_locations()}
    for l in world.get_locations():
        #print(l)
        x=0


def set_all_entrance_rules(world: BoHWorld) -> None:
    entrances = [n for n in world.get_entrances() if "Menu" not in n.name]

    for n in entrances:
        # since every terrain has its name as event-item; require it to proceed
        #world.set_rule(n, HasAny(n.parent_region.name))
        pass

def set_all_location_rules(world: BoHWorld) -> None:
    x=0

def set_completion_condition(world: BoHWorld) -> None:
    # Finally, we need to set a completion condition for our world, defining what the player needs to win the game.
    # You can just set a completion condition directly like any other condition, referencing items the player receives:
    world.multiworld.completion_condition[world.player] = lambda state: state.has_all(("Sword", "Shield"), world.player)

    # In our case, we went for the Victory event design pattern (see create_events() in locations.py).
    # So lets undo what we just did, and instead set the completion condition to:
    world.multiworld.completion_condition[world.player] = lambda state: state.has("Victory", world.player)

    if world.options.goal.option_room_specific:
        #get event-item at location ~roomId~
        room_ap_id = world.options.room_goal.numerator
        name = [k for k,v in terrains.items() if v["ApId"] == room_ap_id][0]
        world.multiworld.completion_condition[world.player] = lambda state: state.has(name, world.player)

    if world.options.goal.option_rooms:
        pass
