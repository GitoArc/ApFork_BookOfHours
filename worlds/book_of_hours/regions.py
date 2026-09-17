from __future__ import annotations

import Utils
from BaseClasses import Region
from ._generate_locations import WISDOMS_GENERIC_PROGRESSION_NAMES, WISDOMS_TIERS_NAMES, \
    WISDOMS_PATHS_REGIONS_NAMES
from .enums import BOHStrEnums
from .functions import Roman, find_roman
from .items import BOHItem
from .jsondump import terrains, books, wisdomtree
from typing import TYPE_CHECKING, Any

from .locations import BOHLocation

if TYPE_CHECKING:
    from .world import BOHWorld


def create_and_connect_regions(world: BOHWorld) -> None:
    create_all_regions(world)
    connect_regions(world)
    if True:
        Utils.visualize_regions(world.get_region(BOHStrEnums.OriginRegionName), "boh.puml")


def create_all_regions(world: BOHWorld) -> None:
    region_names:set[str] = {BOHStrEnums.OriginRegionName}  # because of 'region_names' being a Set, I don't have to check "if exists, do not add"

    # Independant of options; minimum AP-game content
    region_names.update([BOHStrEnums.StBrandansCove, BOHStrEnums.BrancrugVillage, BOHStrEnums.CrowcrossSands, BOHStrEnums.CucurbitBridge,
                         BOHStrEnums.KeepersLodge, BOHStrEnums.WatchmansTowerGatehouse])
    #
    if False:
        for t in terrains:
            region_names.add(t.Label)
    #
        region_names.add("Master Books")
    #
    if world.options.insanitree:
        region_names.add(BOHStrEnums.TreeOfWisdoms)

    regions = [Region(n, world.player, world.multiworld) for n in region_names]
    world.multiworld.regions += regions


def create_book_regions(world: BOHWorld) -> list[Region]:
    master = Region("Master Books", world.player, world.multiworld)
    world.get_region(BOHStrEnums.OriginRegionName).connect(master)
    regions = [master]
    for b in books:
        r = Region(b.Label, world.player, world.multiworld)
        ent = master.connect(r, rule=lambda state: state.has(b.Label, world.player))
        regions.append(r)
    return regions

def connect_regions(world: BOHWorld) -> None:
    origin_region = world.get_region(BOHStrEnums.OriginRegionName)


    for t in terrains:
        try:
            r = world.get_region(t.Label)
            _ = origin_region.connect(r, f"Entr_{r.name}")
        except KeyError as e:
            pass

    if world.options.insanitree:
        wt = world.get_region(BOHStrEnums.TreeOfWisdoms)
        origin_region.connect(wt, rule=lambda state: state.has(BOHStrEnums.DriedJournal, world.player))
        # Bc any fireplace can dry the book, village is technically not a hard requirement
