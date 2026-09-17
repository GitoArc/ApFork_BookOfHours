from __future__ import annotations
import json
import os.path
import re
from collections import Counter
from typing import Any

from worlds.book_of_hours.enums import BOHStrEnums, BOHQuantity, BOHCompare, occult_aspects


class JsonParsed:
    IdStr:str
    Label:str
    Preface:str
    Category: int
    Aspects:dict[str, int]
    IfRoom_Contents:list[str]
    IfRoom_ConnectsTo:list[JsonParsed]
    IfRoom_TerrainUnlockRequirements:dict[str, int]
    IfBook_Rewards_Vanilla_to_IdStr:dict[str,str]

    def __init__(self, obj:dict[str, Any]):
        self.IdStr = obj["IdStr"]
        self.Label = obj["Label"]
        self.Category = obj["Category"]
        self.Aspects = dict.get(obj, "Aspects", {})
        key_mystery = [a for a in self.Aspects if "mystery." in a]
        mystery = 0
        if key_mystery:
            key_mystery = key_mystery[0]
            mystery = self.Aspects[key_mystery]
        self.IfBook_MysteryLvl = mystery
        self.IfBook_MasterySkillReward:JsonParsed = None # cant fill yet
        self.IfSkill_OccultAspects = {k: v for k, v in self.Aspects.items() if k in occult_aspects}

        self.IfRoom_ConnectsTo = [JsonParsed(c) for c in dict.get(obj, "ConnectsTo", [])]
        self.IfRoom_Contents = dict.get(obj, "RoomContents", [])
        if self.IfRoom_Contents:
            pass
        self.IfRoom_TerrainUnlockRequirements = dict.get(obj, "Requires", {})
        self.MaxUnlockReq = max(self.IfRoom_TerrainUnlockRequirements.values(), default=0)
        self.Preface = dict.get(obj,"Preface", self.Label)
        if self.Preface == "Sealed Vault": # Iron/Ivory/Silver vaults have overlapping preface
            self.Preface = "Sealed "+self.Label
        self.IfBook_Rewards_Vanilla_to_IdStr = dict.get(obj, "Rewards", {})
        self.RoomAspectLabel = dict.get(obj, "RoomAspect", "")
        pass

    def __repr__(self):
        return self.Label

    def contains_substr(self, s:str, check_connections:bool = False):
        b = (s in self.IdStr
                or s in self.Label
                or s in self.Preface
                or s in self.RoomAspectLabel
                or any([True for k in self.Aspects if s in k])
                or any([True for k in self.IfRoom_TerrainUnlockRequirements if s in k])
                or s in self.IfBook_Rewards_Vanilla_to_IdStr
                )
        if b is False and check_connections:
            for c in self.IfRoom_ConnectsTo:
                b = b or c.contains_substr(s) # do not recurse
        return b


class SimplePredicate:
    All = False
    Any = False
    comparer:str
    number:int

    def __init__(self, s:str):
        slicedByMiddle = re.split("<|<=|==|>=|>", s)
        slice1 = slicedByMiddle[0]
        slice3 = slicedByMiddle[1] if len(slicedByMiddle) > 1 else "0"
        slice2 = s.replace(slice1, "").replace(slice3, "")
        if slice2 == "":
            pass

        self.All = slice1 == "all"
        self.Any = slice1 == "any"
        self.comparer = slice2
        self.number = int(slice3)

    def use_comparer(self, i:int) -> bool:
        if self.comparer == "<": return i < self.number
        if self.comparer == "<=": return i <= self.number
        if self.comparer == "==": return i == self.number
        if self.comparer == ">=": return i >= self.number
        if self.comparer == ">": return i > self.number
        return NotImplemented

    # to use on Aspect / requirements dict
    # [a for a in list:JsonParsed if evaluate_on_dict(a.Aspect)]
    def evaluate_on_dict(self, dic:dict[str, int]) -> bool:
        if len(dic) == 0: return False

        score = 0
        compar = self.use_comparer
        for v in dic.values():
            if compar(v):
                score += 1
        if self.All: return score == len(dic)
        elif self.Any: return score > 0
        return False

    def __repr__(self):
        quan = "ERROR"
        if self.All:
            quan = "All"
        elif self.Any:
            quan = "Any"

        return f"{quan} {self.comparer} {self.number}"

class ItemParsed:
    IdStr:str
    Label:str
    Aspects:dict[str,int]
    def __init__(self, o:dict[str, Any]):
        self.Inherits = o["inherits"]
        self.IdStr = o["ID"]
        self.Label = o["Label"]
        self.Aspects = o["aspects"]
    def __repr__(self):
        return self.Label

memories:list[JsonParsed]=[]
souls:list[JsonParsed]=[]
terrains:list[JsonParsed]=[]
books:list[JsonParsed]=[]
wisdomtree:list[JsonParsed]=[]
lessons:list[JsonParsed]=[]
skills:list[JsonParsed]=[]
items:list[ItemParsed]=[]


def load_from_dump():
    with open(os.path.join(".", "src_files", "dump.json"), mode='r', encoding='utf-8') as f:
        data = json.load(f)
        for a in data:
            j = JsonParsed(a)
            match j.Category:
                case 1: memories.append(j);
                case 2: souls.append(j);
                case 3: terrains.append(j);
                case 4: wisdomtree.append(j);
                case 5: books.append(j);
                case 6: lessons.append(j);
                case 7: skills.append(j);
load_from_dump()


def load_items():
    with open(os.path.join(".", "src_files", "aspecteditems.json"), mode='r', encoding='utf-8') as f:
        data = json.load(f)
        for a in data:
            items.append(ItemParsed(a))
load_items()
items_animals = [a for a in items if "beast" in a.Inherits]
items_things = [a for a in items if "_" in a.Inherits]
items_tools = [a for a in items if "tool" in a.Aspects]
items_beverages = [a for a in items if "beverage" in a.Inherits]
items_beverages_nontox = [a for a in items_beverages if "intoxicating" not in a.Aspects]
items_beverages_intox = [a for a in items_beverages if "intoxicating" in a.Aspects]
edge_drink = [a for a in items_beverages if "edge" in a.Aspects]
assert len(terrains) == 111 # check vanilla terrain.json / includes ocean
assert len(books) == 281 # check vanilla tomes.json

# assign the skill->book crossmatch
def do_extra_stuff():
    for b in books:
        [lesson_id] = [a for a in b.Aspects if "r." in a]
        skill_id = lesson_id.replace("r.", "s.", 1)
        [skill] = [a for a in skills if a.IdStr == skill_id]
        b.IfBook_MasterySkillReward = skill
        pass
do_extra_stuff()

memories_basic = [a for a in memories if "mem." in a.IdStr]
memories_basic_daily_weather = [a for a in memories if "weather" in a.Aspects and not "quake" in a.IdStr]
memories_music = [a for a in memories if "sound" in a.Aspects]
memories_persistent = [a for a in memories if "persistent" in a.Aspects]
memories_leftovers = [a for a in memories if a not in memories_basic and a not in memories_basic_daily_weather
                      and a not in memories_music and a not in memories_persistent]
memories_pre_house = memories_basic + memories_basic_daily_weather
memories_post_house = [a for a in memories if a not in memories_pre_house]
#memories += lessons
#######################
souls_t3 = [a for a in souls if a.Label.count("+") == 3]
souls_t2 = [a for a in souls if a.Label.count("+") == 2]
souls_t1 = [a for a in souls if a.Label.count("+") == 1]
souls_t0 = [a for a in souls if a.Label.count("+") == 0]
#######################
#terrains = [a for a in terrains if a.Label != BOHStrEnums.StBrandansCove]
# ignore Cove since it canNOT be excluded; Including it would proc items as "freebies"
# but better is not spawning the locations, since region logic depends on Cove
assert len(terrains) == 111
terrains = [a for a in terrains if a.Label != BOHStrEnums.Ocean] # more background than game element, also: can not be interacted with, so its best to fire and fhuget abbat id
assert len(terrains) == 110
terrains_always = [a for a in terrains if a.Label in [BOHStrEnums.StBrandansCove, BOHStrEnums.BrancrugVillage, BOHStrEnums.CucurbitBridge, BOHStrEnums.KeepersLodge, BOHStrEnums.WatchmansTowerGatehouse]]
terrains_house = [a for a in terrains if a not in terrains_always]
terrains_dawn = [a for a in terrains if a.RoomAspectLabel == BOHStrEnums.DawnPeriod]
terrains_solar = [a for a in terrains if a.RoomAspectLabel == BOHStrEnums.SolarPeriod]
terrains_baron = [a for a in terrains if a.RoomAspectLabel == BOHStrEnums.BaronialPeriod]
terrains_curia = [a for a in terrains if a.RoomAspectLabel == BOHStrEnums.CuriaPeriod]
terrains_noct = [a for a in terrains if a.RoomAspectLabel == BOHStrEnums.NocturnalPeriod]
terrains_open = [a for a in terrains if a.RoomAspectLabel == BOHStrEnums.OpenAir]
terrains_oob = [a for a in terrains if a.RoomAspectLabel == BOHStrEnums.OutOfBounds]
def get_terrain_where_unlock_requires(comp:BOHCompare, i:int, aspect_id:str="") -> list[JsonParsed]:
    match comp:
        case BOHCompare.LessThan:           comp = lambda a, b: a < b;
        case BOHCompare.LessOrEquals:       comp = lambda a, b: a <= b;
        case BOHCompare.EqualTo:            comp = lambda a, b: a == b;
        case BOHCompare.GreaterOrEquals:    comp = lambda a, b: a >= b;
        case BOHCompare.GreaterThan:        comp = lambda a, b: a > b;
    labels_uniq = {t.Label for t in terrains for a in t.IfRoom_TerrainUnlockRequirements if aspect_id in a and comp(t.IfRoom_TerrainUnlockRequirements[a], i)}
    res = [t for t in terrains if t.Label in labels_uniq]
    return res


aa = get_terrain_where_unlock_requires(BOHCompare.GreaterThan, 0)
highest = {a.Label : (max(a.IfRoom_TerrainUnlockRequirements.values())) for a in aa}
supposed_rewards = {a.Label : 1+(max(a.IfRoom_TerrainUnlockRequirements.values()) / 4).__ceil__() for a in aa}
#########################
bok_myst:dict[int, list[JsonParsed]] = {}
for i in range(1,30):
    _ = [a for a in books if a.IfBook_MysteryLvl == i]
    if _:
        bok_myst[i] = _
    del _
books_dawn = [a for a in books if "period.dawn" in a.Aspects]
books_solar = [a for a in books if "period.solar" in a.Aspects]
books_baronial = [a for a in books if "period.baronial" in a.Aspects]
books_curia = [a for a in books if "period.curia" in a.Aspects]
books_nocturnal = [a for a in books if "period.nocturnal" in a.Aspects]
#m6 = [a for a in books for k in a.Aspects if "mystery" in k and a.Aspects[k] == 6]
#tup = [(a.Label, k, k2) for a in m6 for k in a.Aspects for k2 in a.Aspects if "mystery" in k and "period" in k2]
def get_books_where_mystery(comp: BOHCompare, i:int):
    match comp:
        case BOHCompare.LessThan:       comp = lambda a, b: a < b;
        case BOHCompare.LessOrEquals:   comp = lambda a, b: a <= b;
        case BOHCompare.EqualTo:        comp = lambda a, b: a == b;
        case BOHCompare.GreaterOrEquals:comp = lambda a, b: a >= b;
        case BOHCompare.GreaterThan:    comp = lambda a, b: a > b;
    return [a for a in books for k in a.Aspects if "mystery" in k and comp(a.Aspects[k], i)]

books_prentice = get_books_where_mystery(BOHCompare.LessOrEquals, 4)
books_scholar = get_books_where_mystery(BOHCompare.LessOrEquals, 10)
books_keeper = get_books_where_mystery(BOHCompare.LessOrEquals, 15)
books_amortal = get_books_where_mystery(BOHCompare.GreaterThan, 15)

def total_lesson_ids_from_books(labels:list[str]):
    l = [a for a in books for l in labels if a.Label == l]
    id = [v for a in l for k,v in a.IfBook_Rewards_Vanilla_to_IdStr.items() if "mastering." in k]
    labels = [a.Label for d in id for a in lessons if a.IdStr == d]
    return id
def lesson_ids_to_skills(ids:list[str]):
    # assume str is in format "x.[a-z]"
    s_ids = [a.replace("x.", "s.") for a in ids]
    c = Counter(s_ids)
    return s_ids
def paths_in_skills(ids:list[str]) -> Counter[str]:
    sk = [s for s in skills for i in ids if s.IdStr == i]
    paths = [a for s in sk for a in s.Aspects if "w." in a]
    c = Counter(paths)
    return c
xx = total_lesson_ids_from_books(["Bancroft Diaries", "Bancroft Diaries", "Bancroft Diaries", "Bancroft Diaries"])
ss = lesson_ids_to_skills(xx)
pp = paths_in_skills(ss)
############################
wisdom_paths = {a.Label.split(" ")[0] for a in wisdomtree}
wisdom_paths.remove("The")
############################

def books_to_skills(bs:list[str], wants=True, exact_match=False, ignore_case=True):
    matched_books = []
    resulting_skills = []
    for s in bs:
        str1 = s.lower() if ignore_case else s
        for b in books:
            str2 = b.Label.lower() if ignore_case else b.Label
            if exact_match:
                match = str1 == str2
            else:
                match = str1 in str2
            if match:
                matched_books.append(b)
                [lessons_id] = [v for k,v in b.IfBook_Rewards_Vanilla_to_IdStr.items() if "mastering" in k]
                skill_id = lessons_id.replace("x.", "s.")
                [skill] = [a for a in skills if a.IdStr == skill_id]
                resulting_skills.append(skill)
    return matched_books, resulting_skills


def skill_to_books(s:str, wants=True, ignore_case=True) -> set[JsonParsed]:
    results = []
    s = s.lower() if ignore_case else s
    for sk in skills:
        label = sk.Label.lower() if ignore_case else sk.Label
        # False == False => True; EQUIV op
        if wants == (s in label):
            lesson_id = sk.IdStr.replace("s.", "x.")
            [results.append(b) for b in books if lesson_id in b.IfBook_Rewards_Vanilla_to_IdStr.values()]
            pass

    return set(results)

ll = books_to_skills(["MEnt"])
pass