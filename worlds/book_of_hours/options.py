from dataclasses import dataclass

from schema import Schema, And

from Options import Choice, OptionGroup, PerGameCommonOptions, Range, Toggle, OptionDict

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
    option_books_catlogged_any = 53
    option_books_catlogged_dawn = 54
    option_books_catlogged_solar = 55
    option_books_catlogged_baronial = 56
    option_books_catlogged_curia = 57
    option_books_catlogged_nocturnal = 58

    option_skill_specific = 71
    option_skills = 72

    default = option_room_specific


class Memories(Toggle):
    """
    Add 'acquiring memories' as locations.
    """
    display_name = "MemorInsanity"


class MemoriesAllowArchipelago(Toggle):
    """
    If true, memories received through the Multiworld count for checks; This can happen repeatedly, and will speed up checks.
    If false, you have to get memories the normal way: Through 'Consider' or reading or weather.
    Does nothing if MemorInsanity is not enabled.
    """


class MemoriesWeather(Toggle):
    """
    If true, adds the different weather memories as locations.
    You are at the mercy of rng.
    Does nothing if MemorInsanity is not enabled.
    Adds 9 locations.
    """


class MemoriesWeatherNuma(Toggle):
    """
    If true, Numa is a location.
    """


class SoulParts(Toggle):
    """
    Add 'collecting parts of the human soul' as locations.
    Added locations depend on "Soul tier rewards" and "Soul parts individual".
    """
    display_name = "InSoulnity"


class SoulRewardPerTier(OptionDict):
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


class SoulRewardPerTierIndividualParts(Toggle):
    """
    If true, +Health is a different location than +Chor, +Ereb, etc.
    If false, each Tier will only have its own 'Tier achieved' location.
    Will do nothing if InSoulnity is not enabled.
    Adds nine times the sum of SoulRewards as locations.
    """
    display_name = "Soul parts individual?"


class TreeOfWisdom(Toggle):
    """
    Adds up to X additional locations for the Tree of Wisdoms and its Paths.
    Tweaked by xxx
    """
    display_name = "InsaniTree of Wisdoms"


# generate the room choices cuz I ain't typing 110 lines by hand
rooms = {f"option_{a["IdStr"].replace("terrain", "").replace("-", "").replace(".", "").replace("'", "")}": a["ApId"]
         for a in terrains.values()}
rooms = {k: v for k, v in rooms.items() if "brancrug" not in k}

RoomGoal = type("RoomGoal", (Choice,), {
    "__module__": __name__,
    "auto_display_name": False,
    "display_name": "Room Goal",
    "__doc__": "Choose your start location. "
               "This is currently only locked to King's Pass.",
    **rooms,
    "default": 3060
})


#del rooms

@dataclass
class BoHOptions(PerGameCommonOptions):
    goal: Goal
    room_goal: RoomGoal
    memorinsanity: Memories
    insoulnity: SoulParts
    insanitree: TreeOfWisdom
