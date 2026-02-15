import json
import os.path

with open(os.path.join(__file__, "..", 'dump.json'), mode='r', encoding='utf-8') as f:
    data = json.load(f)

memories=[]
souls=[]
terrains = {}
books=[]
wisdomtree=[]
lessons=[]
skills=[]
for a in data:
    s = str(a["ApId"])
    sl = s[:2]
    match sl:
        case "10":memories.append(a);
        case "20":souls.append(a);
        case "30":terrains[a["Label"]] = a
        case "40":wisdomtree.append(a);
        case "50":books.append(a);
        case "60":lessons.append(a);
        case "70":skills.append(a);

del terrains["The Atlantic Ocean"] # more background than game element, also: can not be interacted with, so its best to fire it and fhuget abbat id
# oddly the only other terrain left that has Preface = string.Empty // nullchecks wont work
terrains["St Brandan’s Cove"]["Preface"] = "St Brandan’s Cove"
