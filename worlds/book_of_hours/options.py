from dataclasses import dataclass

from schema import Schema, And

from Options import Choice, OptionGroup, PerGameCommonOptions, Range, Toggle, OptionDict, DefaultOnToggle, OptionSet, \
    OptionList

from .jsondump import terrains


class Goal(Choice):
    display_name = "Goal"
    option_remember_specific = 11
    option_remember = 12
    option_soul_specific = 21
    option_souls = 22
    option_room_specific = 31
    option_rooms = 32
    option_wisdom_specific = 41
    option_wisdoms = 42
    option_book_mastered_specific = 51
    option_books_mastered = 52
    option_books_catlog_any = 53
    option_books_catlog_dawn = 54
    option_books_catlog_solar = 55
    option_books_catlog_baronial = 56
    option_books_catlog_curia = 57
    option_books_catlog_nocturnal = 58

    option_skill_specific = 71
    option_skills = 72

    default = option_room_specific


class MemoriesAsLocations(Toggle):
    """
    Add 'acquiring memories' as locations.
    """
    display_name = "MemorInsanity"


class MemoriesAsLocationsAllowArchipelago(Toggle):
    """
    If true, Memories received through the multiworld count for checks; This can trigger repeatedly and can speed up your playthrough.
    If false, you have to get memories the normal way: Through 'Consider' or reading or weather.
    Does nothing if MemorInsanity is not enabled.
    """


class MemoriesAsRewards(OptionList):
    """
    Can fail generation if not enough locations.
    If "MemorInsanity" is enabled, ItemClassification will be (ignored and) forced to "Progression".
    """
    verify_item_name = False # Use own validation in 'generate_early(self)'
    default = [
        "any__all<2__filler__50",           # apply to all memories                                         __ all aspects must be < 2 __ set classification to 'filler' __ add 50 into draw-pool
        "knock__all<4__filler__20",         # apply to all memories where it can find "knock"               __ all aspects must be < 4 __ set classification to 'filler' __ add 10 into draw-pool
        "persistent__any>2__useful__5",     # apply to all memories where it can find "persistent"          __ any aspect  must be > 2 __ set classification to 'useful' __ add  5 into draw-pool
        "persistent__any<3__useful__10",    # apply to all memories where it can find "persistent"          __ any aspect  must be < 3 __ set classification to 'useful' __ add 10 into draw-pool
        "hindsight,salt__any>0__trap__30"   # apply to all memories where it can find "hindsight" OR "salt" __ any aspect  must be > 0 __ set classification to 'trap'   __ add 30 into draw-pool
    ]
    total = 30
# Adds everything into the draw-pool and draw {total} times.
# The list will go from top to bottom "first-come-first-serverd; If the "memory-key" (as above, "persistent") was already processed,
# "apply to all memories ... where it can find" :: searches the id-string, the label, and its aspects
# Aspect "memory:1" will be ignored, since the jsondump can already provide a list with only memories
# any>0 is a formality so that I can make a generic '[any|all] [<|>] int' pattern


class MemoriesWeathersAsLocations(Toggle):
    """
    If true, adds the different weather memories as locations.
    You are at the mercy of rng.
    Does nothing if MemorInsanity is not enabled.
    Adds 9 locations.
    """


class MemoriesWeathersAsLocationsIncludeNuma(Toggle):
    """
    If true, Numa is a location.
    """


class SoulParts(Toggle):
    """
    Add 'collecting parts of the human soul' as locations.
    Added locations depend on "Soul tier rewards" and "Split Soul Parts".
    """
    display_name = "InSoulnity"


class SoulPartsRewardPerTier(OptionDict):
    """
    Adjust the amount of locations per soul tier.
    Does nothing if InSoulnity is not enabled.
    Adds n locations per tier.
    """
    display_name = "Soul tier rewards"
    default = {"Soul": 1, "+Soul": 1, "++Soul": 1, "+++Soul": 1}
    schema = Schema(
        {
            str: And(int, lambda n: n >= 0,
                     error="amount of soul rewards has to be >= 0")
        }
    )


class SoulPartsRewardPerTierSplit(Toggle):
    """
    If true, +Health is a different location than +Chor, +Ereb, etc.
    If false, each Tier will only have its own 'Tier achieved' location.
    Does nothing if InSoulnity is not enabled.
    Adds nine times the sum of SoulRewards as locations.
    """
    display_name = "Split Soul Parts"


class Terrains(DefaultOnToggle):
    """
    Add 'unlocking terrains/rooms' as location.
    Adds 110 locations.
    """
    display_name = "Terrainsanity"


class TerrainsConnectRandom(Toggle):
    """
    The revealed connections of terrains become random.
    Does nothing if Terrainsanity is not enabled.
    """
    display_name = "Terrain Connection Randomiser"


class TerrainsConnectRandomMinimum(Range):
    """
    Does nothing if Terrainsanity is not enabled.
    """
    display_name = "Minimum Connections per Terrain"
    range_start = 1
    range_end = 5
    default = 1


class TerrainsConnectRandomMaximum(TerrainsConnectRandomMinimum):
    """
    Does nothing if Terrainsanity is not enabled.
    """
    display_name = "Maximum Connections per Terrain"
    default = 3


class TerrainsConnectRandomConsideration(Choice):
    """
    Randomization will try to acommodate revealed connections.
    Does nothing if Terrainsanity is not enabled.

    All - connections have a similar difficulty
    At least one - connection is of similar difficulty
    No - It is totally random what connects to where; Your first room could require 14 Lantern. Generation can fail. Numa.
    """
    display_name = "Terrain Connection Randomiser Consideration"
    option_all_ = 0
    option_at_least_one = 1
    option_no = 2


class TreeOfWisdoms(Toggle):
    """
    Add the Tree of Wisdoms and a general progression 'Level 1 to 9' as location.
    Adds 10 locations.
    """
    display_name = "InsaniTree of Wisdoms"


class TreeOfWisdomsSplit(Toggle):
    """
    Every Path of the Tree gets its own progressive locations.
    Does nothing if 'InsaniTree of Wisdoms' is not enabled.
    Increases the previous 10 locations to 82.
    """
    display_name = "Split Wisdoms"


class BooksCatalog(OptionDict):
    """
    How often cataloguing is a location.
    Overlap is possible; For example, with "Any:4" and "Curia:2",
    if you catalogue 1 Curia and 1 Baronial,
      you check the locations "Catalogue any 1 book", "... any 2 books", and "... 1 Curia"
    """
    display_name = "Catalogue n books from ___ period"  # no wordplay w insanity :(
    default = {
        "Any": 20,
        "Dawn": 4,
        "Solar": 4,
        "Baronial": 8,
        "Curia": 8,
        "Nocturnal": 8
    }
    schema = Schema(
        {
            str: And(int, lambda n: n >= 0,
                     error="amount of catalogue locations has to be >= 0")
        }
    )
    # !! """theoretically ok bc every "d.books.*" has a defaultcard, thus can draw 90 cards when there's only, like, 40
    # BUT this requires to insert that many items in the multiworld;
    #   there might be not enough locations; generation may fail
    #   (but the amount of locations are increasing with it, 1:1? idk
    #   !! validate in generate_early !!


class BooksCatalogRewards(OptionDict):
    """
    How many rewards after cataloging a book.
    """
    display_name = "Catalog Locations Reward Amount"  # no wordplay w insanity :(
    default = {
        "Any": 0,
        "Dawn": 2,
        "Solar": 2,
        "Baronial": 1,
        "Curia": 1,
        "Nocturnal": 0
    }
    schema = Schema(
        {
            str: And(int, lambda n: n >= 0,
                     error="amount of catalogue rewards has to be >= 0")
        }
    )


class BooksMasterAny(Range):
    """
    How often mastering a book is a location.
    """
    display_name = "Master __ books"
    range_end = 99
    ## there's 281 uniques, but via defaultcard, could be inf
    # for sanity, limit to 99 (tho even 50 could be too much?)


class BooksRequirementsRandom(Toggle):
    """"""


class BooksMasterSplit(Toggle):
    """
    Every single book gets its own location.
    Adds 281 locations.
    """


class BooksMasterSplitStyle(Choice):
    """
    Modify BookSplit: Decides randomly if a book has a 'Mastered' location.
    """
    option_set_for_all = 0
    option_scaling = 1
    option_scale_inverse = 10
    default = option_set_for_all

class BooksMasterSplitChance(Range):
    """
    Set the chance of a book becoming a location.
    Does nothing if BooksMasterSplitStyle is not 'Set for all'
    """
    range_end = 100

class BooksRewardRandom(Toggle):
    """"""


class Lessons(Toggle):
    """
    Receiving lessons become a location.
    """
    display_name = "Lesssanity"

class SkillsLocationChance(Range):
    """
    Learning a skill becomes a location.
    Rolls each skill against this chance.
    Adds up to 73 locations.
    """
    range_end = 100


# generate the room choices cuz I ain't typing 110 lines by hand
rooms = {f"option_{a["IdStr"].replace("terrain", "").replace("-", "").replace(".", "").replace("'", "")}": a["ApId"]
         for a in terrains.values()}
rooms = {k: v for k, v in rooms.items() if "brancrug" not in k}

RoomGoal = type("RoomGoal", (Choice,), {
    "__module__": __name__,
    "auto_display_name": False,
    "display_name": "Room Goal",
    "__doc__": "Choose your goal room to fix.",
    **rooms,
    "default": 3060
})


#del rooms

@dataclass
class BoHOptions(PerGameCommonOptions):
    goal: Goal
    room_goal: RoomGoal
    memorinsanity: MemoriesAsLocations
    insoulnity: SoulParts
    insanitree: TreeOfWisdoms
    #NOT ALL HERE YET!!
