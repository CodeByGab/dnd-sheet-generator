import os
import requests
import random
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--level", type=int, help="Character Level")
parser.add_argument("--class", dest="char_class", type=str, help="Character Class")
parser.add_argument("--race", type=str, help="Character Race")
parser.add_argument("--name", type=str, help="Character Name")
args = parser.parse_args()

BASE_URL = "https://www.dnd5eapi.co/api"

def cached_request(url, cache_file):
    if os.path.exists(cache_file):
        with open(cache_file, "r") as f:
            return json.load(f)

    try:
        data = requests.get(url, timeout=3).json()

        os.makedirs(os.path.dirname(cache_file), exist_ok=True)
        with open(cache_file, "w") as f:
            json.dump(data, f, indent=2)

        return data

    except:
        print(f"[ERRO] Sem internet e sem cache: {url}")
        return None

def local_request(path):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except:
        print(f"[ERRO] Não foi possível carregar {path}")
        return None

def get_class():
    data = cached_request(
        f"{BASE_URL}/classes",
        "cache/classes/index.json"
    )
    return data["results"] if data else [{"index": "fighter"}]

def get_class_data(class_index):
    data = cached_request(
        f"{BASE_URL}/2014/classes/{class_index}",
        f"cache/classes/{class_index}.json"
    )
    return data or {
        "hit_die": 8,
        "saving_throws": [],
        "proficiency_choices": []
    }

def get_races():
    data = cached_request(
        f"{BASE_URL}/2014/races",
        "cache/races/index.json"
    )
    return data["results"] if data else [{"index": "human"}]


def get_race_data(race_index):
    data = cached_request(
        f"{BASE_URL}/2014/races/{race_index}",
        f"cache/races/{race_index}.json"
    )
    return data or {"ability_bonuses": []}

def get_name(race):
    if args.name:
        return args.name
    
    name_type = random.choice([
        "male", "female", "family", "given",
        "town", "region"
    ])

    data = cached_request(
        f"https://names.ironarachne.com/race/{race}/{name_type}/1",
        f"cache/names/{race}_{name_type}.json"
    )

    if not data:
        return random.choice(["Arin", "Luna", "Doran"])

    return data["names"][0]

def get_backgrounds():
    data = local_request("cache/backgrounds/index.json")
    return data if data else [{"index": "acolyte", "skills": []}]

def get_level():
    if args.level and 1 <= args.level <= 20:
        return args.level
    else:
        return random.choice(range(1, 21))

def get_prof(level):
    if 1 <= level <= 4:
        return 2
    if 5 <= level <= 8:
        return 3
    if 9 <= level <= 12:
        return 4
    if 13 <= level <= 16:
        return 5
    if 17 <= level <= 20:
        return 6

def calc_stt(stat):
    return int((stat - 10 ) / 2)

def add_plus(stat):
    if(stat > 0):
        return str(f"+{stat}")
    return str(stat)

def get_hp(hit_die, con, lvl):
    hp = hit_die + calc_stt(con)
    for _ in range(lvl - 1):
        hp += random.randint(1, hit_die) + calc_stt(con)
    return hp

# Backgrounds
backgrounds = get_backgrounds()
random_bg = random.choice(backgrounds)
bg_skills = random_bg["skills"]
level = get_level()
proficiency_bonus = get_prof(level)

classes_data = get_class()
random_class = args.char_class.lower() if args.char_class else random.choice(classes_data)["index"]

class_data = get_class_data(random_class)

races_data = get_races()
random_race = args.race.lower() if args.race else random.choice(races_data)["index"]

race_data = get_race_data(random_race)

random_name = get_name(random_race)

# Ability scores
base_stats = [15, 14, 13, 12, 10, 8]
abilities = ["str", "dex", "con", "int", "wis", "cha"]

class_priority = {
    "barbarian": ["str", "con", "dex"],
    "fighter": ["str", "con", "dex"],
    "rogue": ["dex", "con", "cha"],
    "wizard": ["int", "con", "dex"],
    "cleric": ["wis", "con", "str"],
    "bard": ["cha", "dex", "con"],
    "warlock": ["cha", "con", "dex"],
    "sorcerer": ["cha", "con", "dex"],
    "ranger": ["dex", "wis", "con"],
    "paladin": ["str", "cha", "con"],
    "monk": ["dex", "wis", "con"],
    "druid": ["wis", "con", "dex"]
}

priority = class_priority[random_class]
ability_scores = {}

for stat in priority:
    ability_scores[stat] = base_stats.pop(0)

random.shuffle(base_stats)

for stat in abilities:
    if stat not in ability_scores:
        ability_scores[stat] = base_stats.pop(0)

# Race Bonuses
for bonus in race_data["ability_bonuses"]:
    ability_scores[bonus["ability_score"]["index"]] += bonus["bonus"]

# HP
max_hp = get_hp(class_data["hit_die"], ability_scores["con"], level)

# Saving Throws
st_data = class_data["saving_throws"]
if len(st_data) >= 2:
    st1 = st_data[0]["index"]
    st2 = st_data[1]["index"]
else:
    st1 = st2 = "str"

save1 = calc_stt(ability_scores[st1]) + proficiency_bonus
save2 = calc_stt(ability_scores[st2]) + proficiency_bonus

# Skills
proficiency_choices = class_data["proficiency_choices"][0]

prof_skills = bg_skills.copy()

available_class_skills = [
    opt["item"]["index"]
    for opt in proficiency_choices["from"]["options"]
    if opt["item"]["index"] not in bg_skills
]

for _ in range(proficiency_choices["choose"]):
    if not available_class_skills:
        break
    skill = random.choice(available_class_skills)
    prof_skills.append(skill)
    available_class_skills.remove(skill)

print("Name:", random_name)
print("Class:", random_class)
print("Race:", random_race)
print("Background:", random_bg["index"])
print("Level:", level)
print("Prof Bonus: +", proficiency_bonus)
print("HP:", max_hp)
print(f"Saves: {st1}:{save1} {st2}:{save2}")

for stat in abilities:
    print(f"{stat.upper()}:{ability_scores[stat]} {add_plus(calc_stt(ability_scores[stat]))}")

print("Skills:", prof_skills)
