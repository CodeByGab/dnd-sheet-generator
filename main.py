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

def get_level():
    if args.level and 1 <= args.level <= 20:
        return args.level
    else:
        return random.choice(range(1, 20))

level = get_level()

def get_prof():
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
    
proficiency_bonus = get_prof()

def fetch_classes():
    return requests.get("https://www.dnd5eapi.co/api/classes").json()["results"]

def get_class(classes_data):
    if args.char_class:
        return args.char_class.lower()
    else:
        return random.choice(classes_data)["index"]

classes_data = fetch_classes()
random_class = get_class(classes_data)

def fetch_race():
    return requests.get("https://www.dnd5eapi.co/api/2014/races").json()["results"]

def get_race(races_data):
    if args.race:
        return args.race.lower()
    else:
        return random.choice(races_data)["index"]

races_data = fetch_race()
random_race = get_race(races_data)

with open("backgrounds.json", "r") as f:
    backgrounds = json.load(f)

random_bg = random.choice(backgrounds)
inventory = random_bg["equipment"]
random_bg_index = random_bg["index"]
bg_skills = random_bg["skills"]

def get_name():
    name_type = [
            "male",
            "female",
            "family",
            "given",
            "town",
            "region"
            ]
    random_nt = random.choice(name_type)
    name_data = requests.get(f"https://names.ironarachne.com/race/{random_race}/{random_nt}/1").json()
    if args.name:
        return args.name
    else:
        return name_data["names"][0]
random_name = get_name()

st_data = requests.get(f"https://www.dnd5eapi.co/api/2014/classes/{random_class}").json()["saving_throws"]
st1 = st_data[0]["index"]
st2 = st_data[1]["index"]

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

def calc_stt(stat):
    return int((stat - 10 ) / 2)

def add_plus(stat):
    if(stat > 0):
        return str(f"+{stat}")
    return str(stat)

def get_hp(hit_die, con, lvl):

    con_mod = calc_stt(con)
    hp = hit_die + con_mod
    for _ in range(lvl - 1):
        hp += random.randint(1, hit_die) + con_mod

    return hp

hit_die_data = requests.get(
        f"https://www.dnd5eapi.co/api/2014/classes/{random_class}").json()["hit_die"]
max_hp = get_hp(hit_die_data, ability_scores["con"], level)

def calculate_bonus_races(race_bonus):
   for bonus in race_bonus:
        stt = bonus["ability_score"]["index"]
        value = bonus["bonus"]
        ability_scores[stt] += value

race_ability_bonuses = requests.get(
        f"https://www.dnd5eapi.co/api/2014/races/{random_race}"
        ).json()["ability_bonuses"]
calculate_bonus_races(race_ability_bonuses)

proficiency_choices = requests.get(
        f"https://www.dnd5eapi.co/api/2014/classes/{random_class}"
        ).json()["proficiency_choices"][0]

prof_skills = bg_skills.copy()

available_class_skills = [
    option["item"]["index"] 
    for option in proficiency_choices["from"]["options"]
    if option["item"]["index"] not in bg_skills
]

for _ in range(proficiency_choices["choose"]):
    if not available_class_skills:
        break
    skill = random.choice(available_class_skills)
    prof_skills.append(skill)
    available_class_skills.remove(skill)

#####################################################################################

strText = f"STR:{ability_scores['str']} {add_plus(calc_stt(ability_scores["str"]))}"
dexText = f"DEX:{ability_scores['dex']} {add_plus(calc_stt(ability_scores["dex"]))}"
conText = f"CON:{ability_scores['con']} {add_plus(calc_stt(ability_scores["con"]))}"
intText = f"INT:{ability_scores['int']} {add_plus(calc_stt(ability_scores["int"]))}"
wisText = f"WIS:{ability_scores['wis']} {add_plus(calc_stt(ability_scores["wis"]))}"
chaText = f"CHA:{ability_scores['cha']} {add_plus(calc_stt(ability_scores["cha"]))}"

save1 = int(calc_stt(ability_scores[st1]) + proficiency_bonus)
save2 = int(calc_stt(ability_scores[st2]) + proficiency_bonus)

print("Name:", random_name)
print("Class:", random_class)
print("Race:", random_race)
print("Background:", random_bg_index)
print("Level:", level)
print("Prof Bonus: +", proficiency_bonus)
print(f"Hp: {max_hp}")
print(f"Saves: {st1}:{save1} {st2}:{save2}")
print(strText, dexText, conText, intText, wisText, chaText)
print(prof_skills)
