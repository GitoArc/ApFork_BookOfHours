from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Callable

from BaseClasses import Location, ItemClassification, CollectionState, LocationProgressType, Region, CollectionRule, \
    DEFAULT_COLLECTION_RULE
from . import items, enums
from ._generate_locations import *
from .enums import BOHStrEnums, occult_aspects
from .functions import predicate_with, Roman, find_roman
from .items import BOHItem
from .jsondump import terrains, JsonParsed, memories, SimplePredicate, lessons, wisdom_paths

if TYPE_CHECKING:
    from .world import BOHWorld

# Every location must have a unique integer ID associated with it.
# We will have a lookup from location name to ID here that, in world.py, we will import and bind to the world class.
# Even if a location doesn't exist on specific options, it must be present in this lookup.
LOCATION_NAME_TO_ID = (MEMORIES_SPECIFIC | MEMORIES_PILE
                       | SOULS_SPECIFIC | SOULS_PILE
                       | TERRAINS_SPECIFIC | TERRAINS_PILE
                       | BOOKS_MASTER_SPECIFIC | BOOKS_MASTER_ANY
                       #| CATALOG_PILE_ANY | CATALOG_PILE_DAWN | CATALOG_PILE_SOLAR | CATALOG_PILE_BARONIAL | CATALOG_PILE_CURIA | CATALOG_PILE_NOCTURNAL
                       | WISDOMS_PATHS | WISDOMS_GENERIC_PROGRESSION
                       #| LESSONS_SPECIFIC | LESSONS_PILE
                       | SKILLS_SPECIFIC | SKILLS_PILE)
pass


class BOHLocation(Location):
    game = "Book of Hours"

    def __init__(self, player: int, name: str, address: Optional[int] = None, parent: Optional[Region] = None,
                 prog_type: LocationProgressType = LocationProgressType.DEFAULT,
                 rule: CollectionRule = DEFAULT_COLLECTION_RULE):
        super().__init__(player, name, address, parent)
        self.progress_type = prog_type
        self.access_rule = rule


# Let's make one more helper method before we begin actually creating locations.
# Later on in the code, we'll want specific subsections of LOCATION_NAME_TO_ID.
# To reduce the chance of copy-paste errors writing something like {"Chest": LOCATION_NAME_TO_ID["Chest"]},
# let's make a helper method that takes a list of location names and returns them as a dict with their IDs.
# Note: There is a minor typing quirk here. Some functions want location addresses to be an "int | None",
# so while our function here only ever returns dict[str, int], we annotate it as dict[str, int | None].
def get_location_names_with_ids(location_names: list[str]) -> dict[str, int | None]:
    return {location_name: LOCATION_NAME_TO_ID[location_name] for location_name in location_names}


def create_all_locations(world: BOHWorld) -> None:
    create_locations(world)
    create_events(world)


def create_locations_memory_progression(world: BOHWorld) -> None:
    menu = world.get_region("Menu")
    locations_wanted: int = world.options.memory_progression["locations"]
    rewards_per_loc: int = world.options.memory_progression.get("rewards_per_location", 1)

    # Time only starts after your introduction to the village acquantance.
    # Meaning 'weathers' are theoretically locked behind 'Brancrug Village Acquaintance'
    #  but basic, musics, ESPECIALLY lessons, etc... require the library rooms (or at MINIMUM the village acquaintance)
    # just streamline everything post-village? post-lodge? or stick in menu?
    locs = {k: v
            for k, v in MEMORIES_PILE.items()
            for l in range(1, 1 + locations_wanted)
            if f" {l} " in k}
    menu.add_locations(locs, BOHLocation)
    # placing goal item transforms the location to event, check create_events()


def create_locations_memories(world: BOHWorld) -> None:
    #assume this runs AFTER create_locations_memorinsanity_goals() "might" have added locations
    origin_region = world.get_region(BOHStrEnums.OriginRegionName)
    world_locs = {l.name: l.address for l in world.get_locations()}
    options = dict(world.options.memories)
    for loc_substr_wildcard, loc_chance in options.items():
        jsons = [a for a in memories + lessons if a.contains_substr(loc_substr_wildcard)]
        locs = {k: v for k, v in MEMORIES_SPECIFIC.items() for j in jsons if k.endswith(f"'{j.Label}'")}
        for lk, lv in locs.items():
            if lk in world_locs:
                pass
            else:
                if world.random.randint(0, 100) < loc_chance:
                    origin_region.locations.append(BOHLocation(world.player, name=lk, address=lv, parent=origin_region))
    pass


def create_locations_memory_goals(world: BOHWorld):
    op = world.options.memory_goals
    s: str
    # first, accumulate the enabled locs
    dumped_loc_names: set[str] = set()
    for s in op:
        filterstring = s.split(":")[0]
        add = s.split(":")[1] == "1"
        filtersplits = filterstring.split("__")
        names = filtersplits[0].split(",")
        pred = filtersplits[1] if len(filtersplits) > 1 else "any>0"
        pred = SimplePredicate(pred)
        jl = {a.Label for a in memories for nam in names
              if a.contains_substr(nam) and pred.evaluate_on_dict(a.Aspects)}
        if add:
            dumped_loc_names.update(jl)
        else:
            dumped_loc_names -= jl
    pass
    # ...then, translate the list[str] to BOHLocations
    aa = {k: v for k, v in MEMORIES_SPECIFIC.items()
          for name in dumped_loc_names
          if name in k}
    # ...and add to world
    origin_region = world.get_region(BOHStrEnums.OriginRegionName)
    for k, v in aa.items():
        loc = BOHLocation(world.player, name=k, address=None, parent=origin_region)
        loc.place_locked_item(BOHItem("Victory Shard", ItemClassification.progression, None, world.player))
        origin_region.locations.append(loc)


def create_locations_books(world: BOHWorld):
    opt = world.options.booksanity
    if not opt:
        return
    # book mastering CAN be succesful via "Consider" # may not need a table?
    book_origin_region = world.get_region("Master Books")
    if opt.generic_progression_enabled:
        pass
        #lim = opt.generic_progression_locations
        #locs = {k:v for k,v in BOOKS_MASTER_ANY.items() if int(k.split(" ")[1]) <= lim}
        #book_origin_region.add_locations(locs, BOHLocation)

    if opt.specific_mastery_enabled:
        for jb in jsondump.books:
            amount_rewards = 0
            match jb.IfBook_MysteryLvl:
                case 4: amount_rewards = 1
                case 6: amount_rewards = 2
                case 8: amount_rewards = 3
                case 10: amount_rewards = 4
                case 12: amount_rewards = 5
                case 14: amount_rewards = 6
                case 16: amount_rewards = 7
                case 18: amount_rewards = 8
                case 21: amount_rewards = 9
            locs_dic = {k:v for k,v in BOOKS_MASTER_SPECIFIC.items() if f"'{jb.Label}'" in k and int(k[-1]) <= amount_rewards }
            reg = world.get_region(jb.Label)
            reg.add_locations(locs_dic, BOHLocation)
            skill_aspects = jb.IfBook_MasterySkillReward.IfSkill_OccultAspects
            for k,v in skill_aspects.items():
                skill_name = f"skill_{k}"
                for i in range(v):
                    reg.add_event(f" EVENT VANILLA {jb.Label} {skill_name} {i+1}",skill_name,
                                  None, BOHLocation, BOHItem, False)
            pass

def create_locations_wisdomtree(world: BOHWorld) -> None:
    wt = world.get_region(BOHStrEnums.TreeOfWisdoms)
    if world.options.insanitree.generic_progression_enabled:
        opt_genprog_location_count = world.options.insanitree.generic_progression_count
        opt_rewards_per_location = world.options.insanitree.generic_progression_rewards_per_loc
        opt_locprogtype = LocationProgressType.EXCLUDED  # bit stupid if prog-item sits at "Commit 81"
        for i in range(1, 1 + opt_genprog_location_count):
            wt.add_event(f"EVENT-WT-G-{i}", "WT G",
                         lambda state, li=i: state.has("WT G", world.player, li - 1),
                         BOHLocation, BOHItem, False)
            locs = {k: v for k, v in WISDOMS_GENERIC_PROGRESSION.items() if
                    f"Commit {i} " in k and int(k[-1]) <= opt_rewards_per_location}
            for k, v in locs.items():
                wt.locations.append(BOHLocation(world.player, k, v, wt, opt_locprogtype,
                                                rule=lambda state, li=i-1: state.has("WT G", world.player, li)))


    if world.options.insanitree.tiered_progression_enabled:
        for t in range(10):
            loc_amount = world.options.insanitree.tiered_progression_rewards_for_tier[t]
            loc_prog_type = LocationProgressType(world.options.insanitree.tiered_progression_locprogtype_for_tier[t])

            s: str
            if t == 0:
                s = "Commit your Journal to 'The Roots of Memory'"
            else:
                s = f" {Roman(t)} "
            t_locs = {k: v for k, v in WISDOMS_TIERS.items() if s in k and int(k[-1]) <= loc_amount}
            for k, v in t_locs.items():
                wt.locations.append(BOHLocation(world.player, name=k, address=v, parent=wt, prog_type=loc_prog_type,
                                                rule=lambda state, li=t: state.has("WT T Token", world.player, li - 1)))
                wt.add_event(f"EVENT-WT-{k}", "WT T Token",
                             lambda state, li=t: state.has("WT T Token", world.player, li - 1),
                             BOHLocation, BOHItem, False)

    if world.options.insanitree.path_progression_enabled:
        pathnode_names = [a.Label for a in jsondump.wisdomtree if "Root" not in a.Label]
        for n in pathnode_names:
            num = find_roman(n)
            pathname_only = n.split(" ")[0]
            loc_amount = world.options.insanitree.path_progression_rewards_per_loc[num]
            loc_prog_type = world.options.insanitree.path_progression_locprogtype_for_tier[num]
            p_locs = {k: v for k, v in WISDOMS_PATHS.items() if f"'{n}'" in k and int(k[-1]) <= loc_amount}
            # add a eventitem corresponding to its required tier: If "Birdsong IV", add "Birdsong" and set rule "requires 3 Birdsong"
            wt.add_event(f"EVENT-P-{n}", f"EVENT-{pathname_only}", lambda state, l1=num: state.has(f"EVENT-{pathname_only}", world.player, l1-1),
                         BOHLocation, BOHItem, False)
            for k,v in p_locs.items():
                wt.locations.append(BOHLocation(world.player, k, v, wt, loc_prog_type,
                                                lambda state, l1=num: state.has(f"EVENT-{pathname_only}", world.player, l1)))

        pass


def modify_terrain_locations_to_goals(world: BOHWorld):
    # run this AFTER the normal locs are created
    for str_ in world.options.terrain_goals:
        ter = [a for a in terrains if a.contains_substr(str_)]
        locations = world.get_locations()
        for t in ter:
            l = [a for a in locations if t.Preface in a.name and " 1 " in a.name]
            pass

        pass
    pass


def create_locations_terrains(world: BOHWorld):
    locs = {}
    for str_ in world.options.terrain_goals:
        regions = [r for r in world.get_regions() for t in terrains if r.name == t.Label and t.contains_substr(str_)]
        #for r in regions:
        #    # bc for hinting, TERRAINS_SPECIFIC Locs use the Preface
        #    locations_for_region_limited_by_diff = {k: v
        #                                            for k, v in TERRAINS_SPECIFIC.items()
        #                                            for t in terrains
        #                                            for i in range(1, 1 + (t.MaxUnlockReq * .51).__ceil__())
        #                                            if r.name == t.Label
        #                                            and t.Preface in k
        #                                            and f" {i} " in k
        #                                            }
        #    locs |= {(r, locations_for_region_limited_by_diff) }


def create_locations(world: BOHWorld) -> None:
    ##if world.options.memory_progression.is_enabled:
    ##    create_locations_memory_progression(world)
    # since memorinsanity could roll NOT creating a loc but it is a memorinsanity_goal;
    #       mIns did not create loc -> InsGoal has to create
    #       mIns did create loc     -> Ins must check and modify loc instead
    # Instead, create the goals first and let memorinsanity "fill" its normal locations:
    #       InsGoal can create any locs
    #       mIns check if already exists before adding
    # Nr2 seems simpler; do memorinsanity_goals first:
    ##if world.options.memory_goals.is_enabled:
    ##    create_locations_memory_goals(world)
    ##if world.options.memories.is_enabled:
    ##    create_locations_memories(world)
    ##if world.options.terrain_locations:
    ##    create_locations_terrains(world)
    ##if world.options.terrain_goals:
    ##    modify_terrain_locations_to_goals(world)
    #if world.options.booksanity:
    #    create_locations_books(world)
    #if world.options.insanitree:
    #    create_locations_wisdomtree(world)

    cove = world.get_region(BOHStrEnums.StBrandansCove)
    village = world.get_region(BOHStrEnums.BrancrugVillage)
    beach2 = world.get_region(BOHStrEnums.CrowcrossSands)
    bridge = world.get_region(BOHStrEnums.CucurbitBridge)
    lodge = world.get_region(BOHStrEnums.KeepersLodge)

    #cove.add_locations({"Cove1": 3001, "Cove2":3002}, BOHLocation)
    village.add_locations({"Village1": 3011, "Village2":3012, "Village3":3013}, BOHLocation)
    beach2.add_locations({"CrowSands1": 3021, "CrowSands2":3022}, BOHLocation)
    bridge.add_locations({"Bridge1": 3031, "Bridge2":3032, "Bridge3":3033}, BOHLocation)
    lodge.add_locations({"Lodge Book1": 401, "Lodge Book2":402}, BOHLocation)

    gate = world.get_region(BOHStrEnums.WatchmansTowerGatehouse)
    loc = BOHLocation(world.player,f"Subgoal: {gate.name}", 33, gate)
    loc.place_locked_item(BOHItem("Victory Shard", ItemClassification.progression, 4, world.player))
    gate.locations.append(loc)


def create_events(world: BOHWorld) -> None:
    origin_region = world.get_region(BOHStrEnums.OriginRegionName)
    cove = world.get_region(BOHStrEnums.StBrandansCove)
    village = world.get_region(BOHStrEnums.BrancrugVillage)
    lodge = world.get_region(BOHStrEnums.KeepersLodge)

    # The "Onboarding" at the start; rewards different souls exclusive to each other
    # but tracking an indiviual result will force player to make that choice too?:
    #       If the generation says "Chor+Ereb" but player chooses "Shapt+Wist" - what then?
    #cove.add_event("Journal-Setup #1 Fet","Fet",lambda state: not (state.has("Chor") or state.has("Shapt")),BOHLocation,BOHItem,False)
    #cove.add_event("Journal-Setup #1 Cho","Chor",lambda state: not (state.has("Fet") or state.has("Shapt")),BOHLocation,BOHItem,False)
    #cove.add_event("Journal-Setup #1 Sha","Shapt",lambda state: not (state.has("Fet") or state.has("Chor")),BOHLocation,BOHItem,False)

    village.add_event("Met the Acquaintance",BOHStrEnums.VillagerAssistance,
                      lambda state: state.has(BOHStrEnums.DriedJournal, world.player),
                      BOHLocation,BOHItem,False)

    # required for accessing the Tree of Wisdoms
    # any fireplace works, but these SHOULD (may be not?) the earliest ones
    origin_region.add_event("Dried the Journal", BOHStrEnums.DriedJournal,
                            lambda state: (village.can_reach(state) and state.has(BOHStrEnums.VillageFriend, world.player)) or lodge.can_reach(state),
                            BOHLocation, BOHItem, False)

    if False and world.options.memory_progression:
        loc = world.get_location(f"Remember {world.options.memory_progression.goal} memories")
        loc.place_locked_item(BOHItem("Victory Shard", ItemClassification.progression, 4, world.player))
