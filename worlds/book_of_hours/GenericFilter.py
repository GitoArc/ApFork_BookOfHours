import re
from importlib.metadata import requires

from worlds.book_of_hours.jsondump import JsonParsed


class SimplePredicate:
    All = False
    Any = False
    comparer:str
    number:int

    def __init__(self, s:str):
        slicedByMiddle = re.split("<|<=|==|>=|>", s)
        slice1 = slicedByMiddle[0]
        slice3 = slicedByMiddle[1]
        slice2 = s.replace(slice1, "").replace(slice3, "")

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

    def evaluate_dict(self, dic:dict[str, int]) -> bool:
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


class GenericFilter:
    targets:list[str]
    filterPredicate:SimplePredicate
    item_classification: int # in bitflag-format, like in BaseClasses.py
    amount: int

    def __init__(self, targs:list[str], asps:SimplePredicate, classif:str, draws):
        self.targets = targs
        self.filterPredicate = asps
        self.amount = draws
        self.item_classification = 0
        if "progression" in classif:
            self.item_classification += 0b001
        if "useful" in classif:
            self.item_classification += 0b010
        if "trap" in classif:
            self.item_classification += 0b100

    def __repr__(self):
        s1 = str(self.targets)
        s2 = str(self.filterPredicate)
        s3 = str(self.item_classification)
        s4 = str(self.amount)
        s = f"{self.targets} # {self.filterPredicate} # ItemClass={self.item_classification} # insert {self.amount}"
        return s

    def evaluate(self, j:JsonParsed) -> bool:
        for t in self.targets:
            if not j.contains_substr(t):
                return False

            aspects = self.filterPredicate.evaluate_dict(j.Aspects)
            requir = self.filterPredicate.evaluate_dict(j.Requires)
            return aspects or requir
        return False

def parseFilterstring(s:str):
    splits = s.split("__")

    aspectFilter = splits[1]
    classif = splits[2]
    draws = splits[3]
    obj = GenericFilter(splits[0].split(","), SimplePredicate(aspectFilter), classif, int(draws))

    return obj
