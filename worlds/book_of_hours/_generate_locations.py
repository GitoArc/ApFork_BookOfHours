from __future__ import annotations

import random

from . import jsondump
from .functions import slice_off_category_from_int, starts_vowel, Roman


def __process_label_memory(s: str):
    s = s.replace("Memory: ", "")
    # if vowel: 'a' or 'an'
    matches = ["a", "e", "i", "o", "u"]
    f = s[0:1].lower()
    if any([a in f for a in matches]):
        s = "an " + s
    else:
        s = "a " + s
    return s


def __process_label_soul(s: str):
    return f"a Part: {s}"


def __process_label_lesson(s: str):
    # no access to world.random ... ¯\_(ツ)_/¯
    s = s.replace("Lesson:", "")
    s = random.choice(["of", "in", "about"]) + s
    return s


def __last_subid_of(d: dict[any, int]):
    i = max(d.values())
    i = slice_off_category_from_int(i)
    return i


#################
MEMORIES_SPECIFIC = {f"Remember an '{o.Label}'" if starts_vowel(o.Label) else f"Remember a '{o.Label}'"
                     : int(f"10{i + 1}")
                     for i, o in enumerate(jsondump.memories)}
# I would've liked to create these dependant on the options, BUT location_name_to_id IS STATIC -> even generate_early is too late, this HAS to be set before AP calls BoHWorld, but then I don't have the option values...
# MEMORIES_PILE = {f"Remember {x} memories - Reward {y}"
#                 : int(f"10{__last_subid_of(MEMORIES_SPECIFIC) + 1+i}")
#                 for i, (x, y) in enumerate([(a, b) for a in range(1, 1 + 333) for b in range(1, 1 + 3)])
#                 }
MEMORIES_PILE = {f"Remember {1} memory" if m == 1 else f"Remember {m} memories"
                 : int(f"10{__last_subid_of(MEMORIES_SPECIFIC) + m}")
                 for m in range(1, 1 + 333)}
##############
SOULS_SPECIFIC = {f"Acquire a '{o.Label}'": int(f"20{i + 1}")
                  for i, o in enumerate(jsondump.souls)}
SOULS_TIERS = {
    f"Acquire a {"+" * (n + 1)}Soul - Reward {r + 1}": int(f"20{__last_subid_of(SOULS_SPECIFIC) + n * 3 + r}")
    for n in range(0, 3) for r in range(1, 1 + 3)}
SOULS_PILE = {f"Acquire {i} part of the human soul" if i == 1 else f"Acquire {i} parts of the human soul"
              : int(f"20{__last_subid_of(SOULS_TIERS) + i}")
              for i in range(1, 1 + 36)}
#################
TERRAINS_SPECIFIC = {f"{o.Label} - Reward {r} ": int(f"30{i + 1}")
                     for i, (r, o) in enumerate([(r, a) for a in jsondump.terrains for r in range(1, 1 + 9)])}
TERRAINS_PILE = {f"Access {i} terrain" if i == 1 else f"Access {i} terrains"
                 : int(f"30{__last_subid_of(TERRAINS_SPECIFIC) + i}")
                 for i in range(1, 1 + 109)}  # 109 bc ocean and cove dont count
################
WISDOMS_GENERIC_PROGRESSION_NAMES = [f"Commit {n} skill to The Tree of Wisdoms" if n == 1
                                     else f"Commit {n} skills to The Tree of Wisdoms" for n in range(1, 82)]
WISDOMS_GENERIC_PROGRESSION = {o : int(f"40{1 + i}") for i, o in enumerate(
    [f"{name} - Reward {r}" for name in WISDOMS_GENERIC_PROGRESSION_NAMES for r in range(1,10)])} # difficulty increases, allow more rewards
WISDOMS_TIERS_NAMES = [f"Commit your Journal to 'The Roots of Memory'"] + [f"Commit a skill to any Tier {Roman(i)} Wisdom" for i in range(1,10)]
WISDOMS_TIERS = { o : int(f"40{__last_subid_of(WISDOMS_GENERIC_PROGRESSION) + 1 + i}") for i, o in enumerate(
        [f"{name} - Reward {r}" for name in WISDOMS_TIERS_NAMES for r in range(1, 10)])} # difficulty increases, allow more rewards
WISDOMS_PATHS_REGIONS_NAMES = [f"Commit a skill to '{a.Label}'" for a in jsondump.wisdomtree if "Root" not in a.Label]
WISDOMS_PATHS = { o : int(f"40{__last_subid_of(WISDOMS_TIERS) + 1 + j}") for j, o in enumerate(
    [f"{name} - Reward {r}" for name in WISDOMS_PATHS_REGIONS_NAMES for r in range(1, 10)])} # difficulty increases, allow more rewards
##############
BOOKS_MASTER_SPECIFIC_NAMES = [o for o in jsondump.books]
BOOKS_MASTER_SPECIFIC = {o: int(f"50{i + 1}") for i, o in enumerate(
    [f"Master '{name}' - Reward {r}" for name in BOOKS_MASTER_SPECIFIC_NAMES for r in range(1, 10)])} # difficulty depends on book, allow more rewards
BOOKS_MASTER_ANY_NAMES = [f"Master {i} book" if i == 1 else f"Master {i} books" for i in range(1, 1 + 281)] # jsondump "t.*" finds 281 matches (i.e. unique books)
BOOKS_MASTER_ANY = {o: int(f"50{__last_subid_of(BOOKS_MASTER_SPECIFIC) + i}") for i, o in enumerate(
    [f"{name}" for name in BOOKS_MASTER_ANY_NAMES])} # no set difficulty/progression curve, only reward 1 per
##### catalogging is kinda iffy for rule-writing, since the game decides at runtime what results out of it
# keep these "at the back" so i wont have empty id blocks if/when i remove them
# or "fake" them? make a "ap.uncatbook.adviceoncontainment", which has the shell of an uncatalogued book but can only reward "t.adviceoncontainment"?
BOOKS_CATALOG_ANY = {f"Catalogue {i} book" if i == 1 else f"Catalogue {i} books"
                    : int(f"50{__last_subid_of(BOOKS_MASTER_ANY) + i}")
                     for i in range(1, 1 + 281)}
    # cost always 1 soul, only reward 1
BOOKS_CATALOG_PILE_DAWN = {f"Catalogue {i} book of the Dawn Period" if i == 1 else f"Catalogue {i} books of the Dawn Period"
                     : int(f"50{__last_subid_of(BOOKS_CATALOG_ANY) + i}")
                           for i in range(1, 1 + 60)} # 60 = Where o.Aspects["period.dawn"] is == 1
    # cost always 1 soul, only reward 1
BOOKS_CATALOG_SOLAR = {
    f"Catalogue {i} book of the Solar Period" if i == 1 else f"Catalogue {i} books of the Solar Period"
    : int(f"50{__last_subid_of(BOOKS_CATALOG_PILE_DAWN) + i}")
    for i in range(1, 1 + 49)} # 49 = ... "period.solar": 1
    # cost always 1 soul, only reward 1
BOOKS_CATALOG_BARONIAL = {
    f"Catalogue {i} book of the Baronial Period" if i == 1 else f"Catalogue {i} books of the Baronial Period"
    : int(f"50{__last_subid_of(BOOKS_CATALOG_SOLAR) + i}")
    for i in range(1, 1 + 60)} # 60 = ... "period.baronial": 1
    # cost always 1 soul, only reward 1
BOOKS_CATALOG_CURIA = {
    f"Catalogue {i} book of the Curia Period" if i == 1 else f"Catalogue {i} books of the Curia Period"
    : int(f"50{__last_subid_of(BOOKS_CATALOG_BARONIAL) + i}")
    for i in range(1, 1 + 69)} # 69 = ..."period.curia": 1
    # cost always 1 soul, only reward 1
BOOKS_CATALOG_NOCTURNAL = {
    f"Catalogue {i} book of the Nocturnal Period" if i == 1 else f"Catalogue {i} books of the Nocturnal Period"
    : int(f"50{__last_subid_of(BOOKS_CATALOG_CURIA) + i}")
    for i in range(1, 1 + 43)} # 4´3 = ... "period.nocturnal": 1
    # cost always 1 soul, only reward 1
################ I think skills are better for locations since you can use lessons as memories:
# If you want a skill location you have to use up the lesson
# ..and since books do/will reward (random) lessons after mastering, it would just be a double location for mastery (in a sense)
# LESSONS_SPECIFIC = {}
# LESSONS_PILE = {}
###############
SKILLS_SPECIFIC = {f"Learn '{o.Label}'": int(f"70{i + 1}")
                   for i, o in enumerate(jsondump.skills)}
SKILLS_PILE = {f"Learn {i} skill" if i == 1 else f"Learn {i} skills"
               : int(f"70{__last_subid_of(SKILLS_SPECIFIC) + i}")
               for i in range(1, 1 + 73)}

pass