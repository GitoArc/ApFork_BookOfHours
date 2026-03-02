from __future__ import annotations

import Utils
from BaseClasses import Region, EntranceType
from .jsondump import terrains, wisdomtree
from typing import TYPE_CHECKING

from .options import RoomGoal

if TYPE_CHECKING:
    from .world import BoHWorld


def create_and_connect_regions(world: BoHWorld) -> None:
    create_all_regions(world)
    connect_regions(world)
    if False:
        Utils.visualize_regions(world.get_region("Menu"), "boh.puml")


def create_all_regions(world: BoHWorld) -> None:
    regions = []
    for e in terrains:
        region = Region(e.Label, world.player, world.multiworld)
        regions.append(region)

    #if world.options.rooms:
    #    x=0

    if True: #world.options.wisdomtree
        world.multiworld.regions += [Region("The Tree of Wisdoms", world.player, world.multiworld)]
        pass

    world.multiworld.regions += [Region("Menu", world.player, world.multiworld)]
    world.multiworld.regions += regions


def connect_regions(world: BoHWorld) -> None:
    start_name = "St Brandan’s Cove"
    world.get_region("Menu").connect(world.get_region(start_name),
                                     f"Menu -> {start_name}",None)

    world.get_region("Menu").connect(world.get_region("The Tree of Wisdoms"),
                                     f"Menu -> The Tree of Wisdoms", None)

    unhandled: list[str] = [start_name]
    done: list[str] = []
    while len(unhandled) > 0:
        currentName = unhandled[0]
        #add self -> others connectors
        region = world.get_region(currentName)
        nexts = [connection.Label for t in terrains for connection in t.ConnectsTo if t.Label == currentName]
        n:str
        for n in nexts:
            # do NOT add a -> b -> a connections; it clutters the logic, methinks
            if n not in done:
                x = region.connect(world.get_region(n), f"{currentName} -> {n}", None) #set in rules.py
                x.randomization_type = EntranceType.TWO_WAY
                if n not in unhandled:
                    unhandled.append(n)

        done.append(currentName)
        unhandled.remove(currentName)

    if False:
        o = world.options.room_goal == RoomGoal.option_lodge
        wt = [e for e in world.get_regions() if "Wisdoms:" in e.name]
        cache1 = [w for w in wt if "1" in w.name]
        match = next((x for x in wt if "1" in x.name), False)
        # assigns the 1-2, 2-3 ... 8-9 of the paths
        while match:
            nex = match.name[:-2]
            for level in range(1,9):
                lvl_region = [e for e in wt if e.name == f"{nex} {level}"][0]
                next_lvl_region = [e for e in wt if e.name == f"{nex} {level+1}"][0]
                lvl_region.connect(next_lvl_region, f"{lvl_region.name} -> {next_lvl_region.name}", None)
                wt.remove(lvl_region)
            match = next((x for x in wt if "1" in x.name), False)
        # remove lv9
        wt = [w for w in wt if "9" not in w.name]
        # the Root HAS to be the only one left
        root = wt[0]
        for i in cache1:
            root.connect(i, f"{root.name} -> {i.name}", None)
        #
        world.get_region("Brancrug Village").connect(root, f"{1} -> {1}", None)
        pass


