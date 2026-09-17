import typing
from dataclasses import dataclass

from schema import Schema, And

from BaseClasses import LocationProgressType
from Options import Choice, PerGameCommonOptions, Range, Toggle, OptionDict, DefaultOnToggle, OptionList, OptionCounter, \
    OptionSet
from worlds.book_of_hours.enums import BOHStrEnums
from worlds.book_of_hours.locations import TERRAINS_SPECIFIC


class MemoriesAsLocations_GenericProgression(OptionCounter):
    """
    Which memories count towards 'Memory Progression'.
    Will be enabled if locations > 0 and any chance is between 0 and 100.

    locations: How many locations to create.
        This is a hard number and will be fulfilled.

    goal: On what index the "goal" item will be placed.
        Must be <= locations

    *_chance: Any memory found will be rolled against their set category-chance (see below).
        If the roll was <= chance, it will count towards progression.
        Maybe the best is either 0 or 100, but if you want to 50/50 here ya go.

    basics: Easily acquired memories like 'Memory: Touch'

    weathers: The daily weather-memories;
        Clouds, Earthquake, Fog, Gale, Hail, Rain, Snow, Storm, Sunny

    weather.earthquake: A weather-memory that is not in the daily occurences, but a possible result by Considering 'Sovereign Treasures' in unmodded game.

    weather.numa: The weather-memory 'Nume-Brume', received from the arrival of Numa.
        Separated from weather bc of rng.

    lessons: The 74 Lessons, rewarded when mastering a book.

    musics: Memories with the "sound" aspect;
        Ascendant Harmony, Bittersweet Certainty, Beguiling Melody, Cheerful Ditty, Hive's Lament, Savage Hymn, Thunderskin's Paean, Wistful Air

    leftovers: Memories that did not fit any of the above categories;
        Confounding Parable, Old Moment, Nameday Riddle, Secret Threshold, Wild Surmise, Wind-Rumour, Winning Move
    """
    display_name = "Memory Progression"
    default = {
        "locations": 10,
        "goal": 5,
        "basics_chance": 40,
        "weathers_chance": 100,
        "weather_earthquake_chance": 100,
        "weather_numa_chance": 100,
        "lessons_chance": 100,
        "musics_chance": 100,
        "persistents_chance": 100,
        "leftovers_chance": 100
    }

    def __init__(self, value: dict[str, int]):
        pass
        # if smth not set, use default
        for d_key in self.default:
            if d_key not in value:
                value[d_key] = self.default[d_key]

        super().__init__(value)

        self.locations = self.value["locations"]
        self.goal = self.value["goal"]
        self.basics_chance = self.value["basics_chance"]
        self.weathers_chance = self.value["weathers_chance"]
        self.weather_earthquake_chance = self.value["weather_earthquake_chance"]
        self.weather_numa_chance = self.value["weather_numa_chance"]
        self.lessons_chance = self.value["lessons_chance"]
        self.musics_chance = self.value["musics_chance"]
        self.persistents_chance = self.value["persistents_chance"]
        self.leftovers_chance = self.value["leftovers_chance"]

        chances = [v for k, v in self.value.items() if "chance" in k and 0 < v <= 100]
        self.any_chance = len(chances) > 0
        self.is_enabled = self.locations > 0 and 0 < self.goal <= self.locations


class MemoriesAsLocations_Specific(OptionDict):
    """
    Earning Memories becomes a location.
    Does not trigger if the memory was received as multiworld item.
    Rolls each memory in that category against their chance; Will become a location if succeeded.
    Mostly intended for either 0 or 100, but this "tunable bool"-way supports randomisation.
    """
    display_name = "MemorInsanity"
    default = {
        "mem.":100,
        "weather":10,
        "weather.earthquake,weather.numa":0,
        #"sound,persistent,@leftovers":100,
    }

    def __init__(self, value: dict[str, int]):
        super().__init__(value)

        chances = [v for k, v in value.items()]
        self.is_enabled = any([True for e in chances if e > 0])


class MemoriesAsLocations_SpecificGoals(OptionList):  # need order preserved, so not a set
    """
    Specify which memory locations become mandatory goal checks.
    That location can not send a multiworld item, but will reward a local event item instead.
    """
    default = [
         "ouch:1", #  enables all cards where "memory" in JsonParsed
        # "__any>5:1",  # enables cards where "" in card and any aspect > 5
        # "weather__all<3:1",  # searches for and enables cards that contains "weather" and all aspects < 3
        # "arthquake,idumos,uma:0",  # searches for and disables cards that contain "arthquake" or "idumos"
        # or "uma" (allows "Numa", "numa", "aeiouma" etc)
        # I don't wanna check the lower/upper casing, and implicitly converting the search clause might mess things up
    ]

    def __init__(self, value: list[str]):
        super().__init__(value)
        non_zeros = [a for a in value if a.split(":")[1] == "1"]
        self.is_enabled = len(non_zeros) > 0


class MemoriesAsItems(OptionDict):
    """
    Insert memories into the itempool via pattern-string.
    ItemClassification can not be "progression" and, if received, will NOT count towards memory goals.

    Pattern is "aspect__quantity(comparer)intensity__itemClassification__amountInsertedInto
    List is applied "in order", later changes will overwrite previous setting
    """
    display_name = "Add Memories to itempool?"
    default = {
        "downgrade_trap_chance": 50,
        "predicates": {
            # "__all<5": "filler",                          # apply to all memories where "knock"               __ all aspects must be < 4 __ set classification to 'filler'
            #"hindsight,salt,regret,loss__any>0": "trap",    # apply to all memories where "hindsight" OR "salt" __ any aspect  must be > 0 __ set classification to 'trap'
            "__all<2": "trap",
        }
    }

    def __init__(self, value: typing.Dict[str, int]):
        # if smth not set, use default
        for d_key in self.default:
            if d_key not in value:
                value[d_key] = self.default[d_key]
        super().__init__(value)
        self.downgrade_trap_chance = value["downgrade_trap_chance"]
        self.predicates = value["predicates"]
        self.is_enabled = len(value) > 0


# Adds everything into the draw-pool and draw {total} times.
# The list will go from top to bottom "first-come-first-serverd; If the "memory-key" (as above, "persistent") was already processed,
# "apply to all memories ... where it can find" :: searches the id-string, the label, and its aspects
# Aspect "memory:1" will always be true / return all memories
# any>0 is a formality so that I can make a generic '[any|all] [<|>] int' pattern


class SoulParts(Toggle):
    """
    Add 'collecting parts of the human soul' as locations.
    Added locations depend on "Soul tier rewards" and "Split Soul Parts".
    """
    display_name = "InSoulnity"


class SoulPartsRewardPerTier(OptionDict):
    """
    Adjust the amount of locations per soul tier.
    Does nothing if InSoulnity is disabled.
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
    Does nothing if InSoulnity is disabled.
    Adds nine times the sum of SoulRewards as locations.
    """
    display_name = "Split Soul Parts"


class TerrainGoals(OptionDict):
    display_name = "TerraInsanity"
    default = {
        "curia": 1,
        "vault": 1,
    }
    #def __bool__(self):
    #    return True


class Terrains(OptionDict):
    """
    Add 'unlocking terrains/rooms' as location.
    Adds 110 locations.
    """
    display_name = "TerraInsanity"
    default = {
        "" : 1,
        "winter" : 0
    }

    #def __bool__(self):
    #    return True


class TreeOfWisdoms(OptionDict):
    """
    Add locations to The Tree of Wisdoms and its many nodes.
    """
    display_name = "InsaniTree of Wisdoms"
    default = {
        "generic_progression_enabled": 1,
        "generic_progression_locations": 27,
        "generic_progression_rewards_per_location": 2,
        "tiered_progression_enabled": 1,
        "tiered_progression_rewards_per_":      "1123456789",
        "tiered_progression_locprogtypes_per_": "2211333333",
        "path_progression_enabled": 1,
        "path_progression_rewards_per_":        "222111222",
        "path_progression_locprogtypes_per_":   "211133333",
    }

    def __init__(self, dic: dict[str, typing.Any]):
        # if smth not set, use default
        for d_key in self.default:
            if d_key not in dic:
                dic[d_key] = self.default[d_key]
        super().__init__(dic)
        self.generic_progression_enabled:bool = dic["generic_progression_enabled"] == 1
        self.generic_progression_count:int = dic["generic_progression_locations"]
        self.generic_progression_rewards_per_loc:int = dic["generic_progression_rewards_per_location"]

        self.tiered_progression_enabled:bool = dic["tiered_progression_enabled"] == 1
        self.tiered_progression_rewards_for_tier:list[int] = [int(a) for a in dic["tiered_progression_rewards_per_"]]
        self.tiered_progression_locprogtype_for_tier:list[LocationProgressType] = [LocationProgressType(int(a)) for a in dic["tiered_progression_locprogtypes_per_"]]

        self.path_progression_enabled:bool = dic["path_progression_enabled"] == 1
        self.path_progression_rewards_per_loc:list[int] = [0] + [int(a) for a in dic["path_progression_rewards_per_"]]
        # pad the list
        self.path_progression_locprogtype_for_tier:list[LocationProgressType] = [LocationProgressType.EXCLUDED] + [LocationProgressType(int(a)) for a in dic["path_progression_locprogtypes_per_"]]

    def __bool__(self):
        return self.generic_progression_enabled or self.tiered_progression_enabled or self.path_progression_enabled


class BookLocations(OptionDict):
    display_name = "Booksanity"

    def __init__(self, dic:dict[str, typing.Any]):
        super().__init__(dic)
        self.generic_progression_enabled:bool = dic.get("generic_progression_enabled", True)
        self.generic_progression_locations: int = dic.get("generic_progression_locations", 281)
        self.specific_mastery_enabled:bool = dic.get("specific_mastery_enabled", True)
        self.specific_mastery_rewards_if_mystery4 = dic.get("mystery4_rewards", 1)
        self.specific_mastery_rewards_if_mystery6 = dic.get("mystery6_rewards", 2)
        self.specific_mastery_rewards_if_mystery8 = dic.get("mystery8_rewards", 3)
        self.specific_mastery_rewards_if_mystery10 = dic.get("mystery10_rewards", 4)
        self.specific_mastery_rewards_if_mystery12 = dic.get("mystery12_rewards", 5)
        self.specific_mastery_rewards_if_mystery14 = dic.get("mystery14_rewards", 6)
        self.specific_mastery_rewards_if_mystery16 = dic.get("mystery16_rewards", 7)
        self.specific_mastery_rewards_if_mystery18 = dic.get("mystery18_rewards", 8)
        self.specific_mastery_rewards_if_mystery21 = dic.get("mystery21_rewards", 9)

        pass

    def __bool__(self):
        return self.generic_progression_enabled or self.specific_mastery_enabled


class BooksCatalogue(OptionDict):
    """
    How often cataloguing is a location.
    Does nothing if 'Booksanity' is disabled.
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


class BooksCatalogueRewards(OptionDict):
    """
    How many rewards after cataloging a book.
    Does not care about 'Booksanity'.
    """
    display_name = "Catalogue Locations Reward Amount"  # no wordplay w insanity :(
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


class BooksMaster(OptionDict):
    """
    How often mastering a book is a location.
    Does nothing if 'Booksanity' is disabled.
    """
    display_name = "Master n books from ___ period"  # no wordplay w insanity :(
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
                     error="amount of book-mastery locations has to be >= 0")
        }
    )


class BooksMasterRequirementsRandom(Toggle):
    """
    Does nothing if 'Booksanity' is disabled.
    """
    display_name = "Book RandoMysteries"


class BooksMasterSplit(Toggle):
    """
    Every single book gets its own location.
    Does nothing if 'Booksanity' is disabled.
    Adds 281 locations.
    Overlaps with any 'Master n books' setting.
    """
    display_name = "Book Splitsanity"


class BooksMasterSplitStyle(Choice):
    """
    Modify BookSplit: Decides randomly if a book has a 'Mastered' location.
    Does nothing if 'Booksanity' is disabled.
    """
    display_name = "Book Splitsanity - Split Style"
    option_set_for_all = 0
    option_scaling = 1
    option_scale_inverse = 10
    default = option_set_for_all


class BooksMasterSplitChance(Range):
    """
    Set the chance of a book becoming a location.
    Does nothing if 'Booksanity' is disabled.
    Does nothing if BooksMasterSplitStyle is not 'Set for all'
    """
    display_name = "Split Style SetAll - Chance"
    range_end = 100


class BooksRewardRandom(Toggle):
    """
    Does nothing if 'Booksanity' is disabled.
    """
    display_name = "Book Random Reward"


class LessonsAsLocations(Range):
    """
    'Receiving a lesson' becomes a location.
    Rolls each lesson against this chance.
    Adds up to 74 locations.
    """
    display_name = "Lesssanity"


class LessonAsLocationAllowArchipelago(Toggle):
    """
    Does nothing if 'Lesssanity' is disabled.
    If true, items received through the multiworld count for checks; This can trigger repeatedly and can speed up your playthrough.
    If false, you have to get lessons the normal way: mastering books (or maybe saloons if you own House of Light)
    """


class LessonsAsItems(OptionList):
    """
    Does not care about 'MemorInsanity'.
    If total is higher than 74, it will randomly duplicate items until full.
    Can fail generation if not enough locations.
    If "Lesssanity" is enabled, ItemClassification will be (ignored and) forced to "Progression".
    """
    display_name = "Add Lessons to itempool?"
    verify_item_name = False  # Use own validation in 'generate_early(self)'
    default = [
        "any__any>0__useful__50",
    ]
    total = 30  # max can not exceed 74, validate in 'generate_early(self)'


class SkillAsLocationChance(Range):
    """
    Learning a skill becomes a location.
    Rolls each skill against this chance.
    Adds up to 73 locations.
    """
    display_name = "Skillsanity"
    range_end = 100


# generate the room choices cuz I ain't typing 110 lines by hand
rooms = {f"option_{k}"
         : v
         for k, v in TERRAINS_SPECIFIC.items()}
rooms = {k: v for k, v in rooms.items() if "brancrug" not in k}

RoomGoal = type("RoomGoal", (Choice,), {
    "__module__": __name__,
    "auto_display_name": False,
    "display_name": "Room Goal",
    "__doc__": "Choose your goal room to fix.",
    **rooms,
    "default": 3060
})
del rooms


@dataclass
class BoHOptions(PerGameCommonOptions):
    memory_progression: MemoriesAsLocations_GenericProgression
    memories: MemoriesAsLocations_Specific
    memory_goals: MemoriesAsLocations_SpecificGoals
    memory_items: MemoriesAsItems
    terrain_goals: TerrainGoals
    terrain_locations: Terrains
    booksanity: BookLocations
    insanitree: TreeOfWisdoms
    local_items = [BOHStrEnums.FishermanAssistance, BOHStrEnums.VillageFriend]
