from dataclasses import dataclass

from Options import Choice, OptionGroup, PerGameCommonOptions, Range, Toggle

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
    Adds up to X additional locations for acquiring memories; They only proc if you get them by yourself; AP rewards will be ignored.
    Tweaked by xxx
    """
    display_name = "MemorInsanity"


class SoulParts(Toggle):
    """
    Enables up to X additional locations by collecting parts of the human soul.
    Tweaked by xxx
    """
    display_name = "InSoulnity"


class TreeOfWisdom(Toggle):
    """
    Adds up to X additional locations for the Tree of Wisdoms and its Paths.
    Tweaked by xxx
    """
    display_name = "InsaniTree of Wisdoms"


# generate the room choices cuz I ain't typing 110 lines by hand
rooms = {f"option_{a["IdStr"].replace("terrain","").replace("-","").replace(".","").replace("'","")}":a["ApId"]
         for a in terrains.values()}
rooms = {k:v for k,v in rooms.items() if "brancrug" not in k}

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
