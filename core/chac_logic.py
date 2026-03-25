import random
from config import BASE_STATS, ABILITIES, CLASS_PRIORITY
from api import client
from core import math

def generate_character(args):
    base_stats = BASE_STATS.copy()
    # Backgrounds
    backgrounds = client.get_backgrounds()
    random_bg = random.choice(backgrounds)
    bg_skills = random_bg["skills"]

    level = math.get_level(args.level)
    proficiency_bonus = math.get_prof(level)

    classes_data = client.get_class()
    random_class = args.char_class.lower() if args.char_class else random.choice(classes_data)["index"]
    class_data = client.get_class_data(random_class)

    races_data = client.get_races()
    random_race = args.race.lower() if args.race else random.choice(races_data)["index"]
    race_data = client.get_race_data(random_race)

    random_name = client.get_name(random_race, args.name)


    priority = CLASS_PRIORITY[random_class]
    ability_scores = {}

    for stat in priority:
        ability_scores[stat] = base_stats.pop(0)

    random.shuffle(base_stats)

    for stat in ABILITIES:
        if stat not in ability_scores:
            ability_scores[stat] = base_stats.pop(0)

    # Race Bonuses
    for bonus in race_data["ability_bonuses"]:
        ability_scores[bonus["ability_score"]["index"]] += bonus["bonus"]

    ability_scores = math.up_asi(ability_scores, priority, level)

    # HP
    max_hp = math.get_hp(class_data["hit_die"], ability_scores["con"], level)

    # Saving Throws
    st_data = class_data["saving_throws"]
    if len(st_data) >= 2:
        st1 = st_data[0]["index"]
        st2 = st_data[1]["index"]
    else:
        st1 = st2 = "str"

    save1 = math.calc_stt(ability_scores[st1]) + proficiency_bonus
    save2 = math.calc_stt(ability_scores[st2]) + proficiency_bonus

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

    return {
        "name": random_name,
        "class": random_class,
        "race": random_race,
        "background": random_bg["index"],
        "level": level,
        "hp": max_hp,
        "proficiency_bonus": proficiency_bonus,
        "stats": ability_scores,
        "saves": {
            st1: save1,
            st2: save2
        },
        "skills": prof_skills
    }

def format_skill(skill):
    if skill.startswith("skill-"):
        skill = skill.replace("skill-", "")
    return skill.replace("-", " ").title()

def print_character(char, math):
    lines_width = 30
    print("=" * lines_width)
    print(f"{char['name']} | {char['race'].title()} {char['class'].title()}")
    print("=" * lines_width)

    print(f"Level: {char['level']}    HP: {char['hp']}")
    print(f"Proficiency Bonus: +{char['proficiency_bonus']}")
    print(f"Background: {char['background'].title()}")

    print("\nSaving Throws:")
    for k, v in char["saves"].items():
        print(f"  {k.upper():<3}: {v:+}")

    print("\nAttributes:")
    for stat, value in char["stats"].items():
        mod = math.calc_stt(value)
        print(f"  {stat.upper():<3}: {value:>2} ({mod:+})")

    print("\nSkills:")
    for skill in char["skills"]:
        print(f"  - {format_skill(skill)}")

    print("=" * lines_width)
