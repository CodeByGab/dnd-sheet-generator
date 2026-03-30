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

    # Classes
    classes_data = client.get_class()
    random_class = args.char_class.lower() if args.char_class else random.choice(classes_data)["index"]
    class_data = client.get_class_data(random_class)

    # Races
    races_data = client.get_races()
    random_race = args.race.lower() if args.race else random.choice(races_data)["index"]
    race_data = client.get_race_data(random_race)

    random_name = client.get_name(random_race, args.name)

    # Stats
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
    hit_die = class_data["hit_die"]
    max_hp = math.get_hp(hit_die, ability_scores["con"], level)


    # Saving Throws
    st_data = class_data["saving_throws"]
    if len(st_data) >= 2:
        st1 = st_data[0]["index"]
        st2 = st_data[1]["index"]
    else:
        st1 = st2 = "str"

    save1 = math.calc_stt(ability_scores[st1]) + proficiency_bonus
    save2 = math.calc_stt(ability_scores[st2]) + proficiency_bonus

    # Prof Skills
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

    # Geral Prof
    
    proficiencies = [
        prof["name"]
        for prof in class_data["proficiencies"]
        if not prof["index"].startswith("saving-throw")
    ]
    
    if random_class == 'bard' or random_class == 'monk':

        proficiency_choices_extra = class_data["proficiency_choices"][1]
        r_number = proficiency_choices_extra["choose"]

        if random_class == 'bard':
            for _ in range(r_number):
                extra_prof = random.choice(proficiency_choices_extra["from"]["options"])["item"]["name"]
                if extra_prof not in proficiencies:
                    proficiencies.append(extra_prof)

        if random_class == 'monk':
            proficiency_choices_extra = class_data["proficiency_choices"][1]
            r_number = proficiency_choices_extra["choose"]
            for _ in range(r_number):
                choice_index = random.choice([0, 1])
                selected_choice = proficiency_choices_extra["from"]["options"][choice_index]["choice"]

                extra_prof = random.choice(selected_choice["from"]["options"])["item"]["name"]

                if extra_prof not in proficiencies:
                    proficiencies.append(extra_prof)

    # Minus Status

    # Speed
    race_speed = race_data["speed"]
    # Initiative
    initiative = math.calc_stt(ability_scores["dex"])
    # AC
    ac = 10 + initiative
    # Pass Perception
    if "skill-perception" in prof_skills:
        pass_perception = 10 + math.calc_stt(ability_scores["wis"]) + proficiency_bonus
    else:
        pass_perception = 10 + math.calc_stt(ability_scores["wis"])
    
    # Inventory
    inventory = [] 
    for option in class_data["starting_equipment_options"]:
        option_from = option["from"]

        if option_from["option_set_type"] == "options_array":
            choice = option_from["options"][0]

            if choice["option_type"] == "counted_reference":
                inventory.append({
                    "name": choice["of"]["name"],
                    "quantity": choice["count"]
                })

        elif option_from["option_set_type"] == "equipment_category":
            category = option_from["equipment_category"]["name"]

            inventory.append({
                "name": f"Any {category}",
                "quantity": 1
            })
    return {
        "name": random_name,
        "class": random_class,
        "race": random_race,
        "background": random_bg["index"],
        "level": level,
        "hp": max_hp,
        "hit_die": hit_die,
        "proficiency_bonus": proficiency_bonus,
        "stats": ability_scores,
        "saves": {
            st1: save1,
            st2: save2
        },
        "skills": prof_skills,
        "speed": race_speed,
        "initiative": initiative,
        "ac": ac,
        "pass_perception": pass_perception,
        "proficiencies": proficiencies,
        "inventory": inventory,
    }

# OutPut DeBug

def format_skill(skill):
    if skill.startswith("skill-"):
        skill = skill.replace("skill-", "")
    return skill.replace("-", " ").title()

def print_character(char, math):
    lines_width = 36
    print("=" * lines_width)
    print(f"{char['name']} | {char['race'].title()} {char['class'].title()}")
    print("=" * lines_width)

    lvl_txt = f"Level: {char['level']}"
    hp_txt = f"HP: {char['hp']}"
    ht_txt = f"Hit Die: {char['level']}d{char['hit_die']}"
    txt_space = 3 * " "

    print(lvl_txt + txt_space + hp_txt + txt_space + ht_txt)
    print(f"Proficiency Bonus: +{char['proficiency_bonus']}")
    print(f"Background: {char['background'].title()}")

    print(f"\nArmor Class: {char['ac']}")
    print(f"Initiative: +{char['initiative']}")
    print(f"Speed: {char['speed']} feet")
    print(f"Pass Perception: {char['pass_perception']}")

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
    print("\nProficiencies:")
    for prof in char["proficiencies"]:
        print(f"  - {prof}")
    for item in char['inventory']:
        print(f"{item['name']}{f' x{item["quantity"]}' if item['quantity'] > 1 else ''}")
