from __future__ import annotations
import json
import os.path


class JsonParsed:
    IdStr:str
    Label:str
    Preface:str
    ApId: int|None
    Aspects:dict[str, int]|None
    Requires:dict[str, int]|None
    ConnectsTo:list[JsonParsed]

    def __init__(self, obj):
        self.IdStr = obj["IdStr"]
        self.Label = obj["Label"]
        self.ApId = dict.get(obj, "ApId")
        self.Aspects = dict.get(obj, "Aspects", {})
        self.ConnectsTo = [JsonParsed(c) for c in dict.get(obj, "ConnectsTo", [])]
        self.Preface = dict.get(obj,"Preface", "")
        self.Requires = dict.get(obj,"Requires", {})
        pass

    def __repr__(self):
        return f"{self.ApId} - {self.Label}"

    def contains_substr(self, s:str):
        return (s in self.IdStr
                or s in self.Label
                or s in self.Preface
                or s in self.Aspects
                or s in self.Requires
                or s in [cs.IdStr for cs in self.ConnectsTo]
                or s in [cs.Label for cs in self.ConnectsTo]
                or s in [cs.Preface for cs in self.ConnectsTo]
                )

with open(os.path.join(__file__, "..", 'dump.json'), mode='r', encoding='utf-8') as f:
    data = json.load(f)

memories:list[JsonParsed]=[]
souls:list[JsonParsed]=[]
terrains:list[JsonParsed]=[]
books:list[JsonParsed]=[]
wisdomtree:list[JsonParsed]=[]
lessons:list[JsonParsed]=[]
skills:list[JsonParsed]=[]
for a in data:
    s = str(a["ApId"])
    sl = s[:2]
    match sl:
        case "10":memories.append(JsonParsed(a));
        case "20":souls.append(JsonParsed(a));
        case "30":terrains.append(JsonParsed(a));
        case "40":wisdomtree.append(JsonParsed(a));
        case "50":books.append(JsonParsed(a));
        case "60":lessons.append(JsonParsed(a));
        case "70":skills.append(JsonParsed(a));

memories_basic = [a for a in memories if "mem." in a.IdStr]
memories_music = [a for a in memories if "sound" in a.Aspects]
memories_weather = [a for a in memories if "weather" in a.Aspects]
memories_persistent = [a for a in memories if "persistent" in a.Aspects]
memories_leftovers = [a for a in memories if a not in memories_basic
         and a not in memories_music
         and a not in memories_weather
         and a not in memories_persistent]
everything = memories + souls + terrains + books + wisdomtree + lessons + skills

# more background than game element, also: can not be interacted with, so its best to fire and fhuget abbat id
terrains = [a for a in terrains if a.Label != "The Atlantic Ocean"]
# oddly the only other terrain left that has Preface = string.Empty // nullchecks wont work
t = [a for a in terrains if a.Label == "St Brandan’s Cove"][0]
t.Preface = "St Brandan’s Cove"
