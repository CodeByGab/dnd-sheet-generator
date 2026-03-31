import random
from config import BASE_STATS, ABILITIES, CLASS_PRIORITY
from api import client
from core import math

STARTING_ARMORS = {
    "leather armor": {"base": 11, "dex": True, "max_dex": None},
    "chain mail": {"base": 16, "dex": False, "max_dex": 0},
    "scale mail": {"base": 14, "dex": True, "max_dex": 2},
}

def calculate_ac(inventory, dex_mod):
    base_ac = 10 + dex_mod
    shield_bonus = 0
    best_armor_ac = base_ac

    for item in inventory:
        name = item["name"].lower()

        if "shield" in name:
            shield_bonus = 2

        for armor_name, data in STARTING_ARMORS.items():
            if armor_name in name:
                dex_bonus = dex_mod if data["dex"] else 0

                if data["max_dex"] is not None:
                    dex_bonus = min(dex_bonus, data["max_dex"])

                armor_ac = data["base"] + dex_bonus

                if armor_ac > best_armor_ac:
                    best_armor_ac = armor_ac

    return best_armor_ac + shield_bonus

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

    
    # Inventory
    inventory = []

    for item in class_data.get("starting_equipment", []):
        inventory.append({
            "name": item["equipment"]["name"],
            "quantity": item["quantity"]
        })
    for option in class_data.get("starting_equipment_options", []):
        option_from = option["from"]
    
        if option_from["option_set_type"] == "options_array":
            choices = option_from["options"]
    
            selected = random.choice(choices)
    
            if selected["option_type"] == "counted_reference":
                inventory.append({
                    "name": selected["of"]["name"],
                    "quantity": selected["count"]
                })
    
            elif selected["option_type"] == "multiple":
                for item in selected["items"]:

                    if item["option_type"] == "counted_reference":
                        inventory.append({
                            "name": item["of"]["name"],
                            "quantity": item["count"]
                        })

                    elif item["option_type"] == "choice":
                        category_data = item["choice"]["from"]["equipment_category"]
                        category_index = category_data["index"]
    
                        items = client.get_equipment_category(category_index)["equipment"]

                        for _ in range(item["choice"]["choose"]):
                            chosen_item = random.choice(items)

                            inventory.append({
                                "name": chosen_item["name"],
                                "quantity": 1
                            })
        elif option_from["option_set_type"] == "equipment_category":
            category = option_from["equipment_category"]["name"]

            inventory.append({
                "name": f"Any {category}",
                "quantity": option["choose"]
            })

    # Minus Status

    # Speed
    race_speed = race_data["speed"]
    # Initiative
    initiative = math.calc_stt(ability_scores["dex"])
    # AC
    ac = calculate_ac(inventory, initiative)
    # Pass Perception
    if "skill-perception" in prof_skills:
        pass_perception = 10 + math.calc_stt(ability_scores["wis"]) + proficiency_bonus
    else:
        pass_perception = 10 + math.calc_stt(ability_scores["wis"])
    # Spell

    spellcaster = "spellcasting" in class_data

    if spellcaster:
        levels = client.get(class_data["class_levels"])

        if levels and len(levels) >= level:
            level_data = levels[level - 1]

            spellcasting_data = level_data.get("spellcasting", {})
            if spellcasting_data:

                spell_slots = {
                    k: v for k, v in spellcasting_data.items()
                    if k.startswith("spell_slots_level_") and v > 0
                }
            else:
                spell_slots = {}

            spell_data = spellcasting_data
        else:
            spell_slots = {}
            spell_data = {}

    # Class Features

    levels_data = client.get(class_data["class_levels"])
    features = []

    if levels_data:
        for lvl_data in levels_data:
            if lvl_data["level"] > level:
                break

            for feature in lvl_data.get("features", []):
                name = feature["name"]
                if name not in features:
                    features.append(name)

    # SPELLCASTING SYSTEM (COMPLETO)

    spell_info = None

    if spellcaster:
        spellcasting_ability = class_data["spellcasting"]["spellcasting_ability"]["index"]
        casting_mod = math.calc_stt(ability_scores[spellcasting_ability])

        spell_save_dc = 8 + proficiency_bonus + casting_mod
        spell_attack = casting_mod + proficiency_bonus

        # Spell Slot

        spell_slots = {}
        max_spell_level = 0
        spell_data = {}

        if levels_data and len(levels_data) >= level:
            level_data = levels_data[level - 1]
            spell_data = level_data.get("spellcasting", {})

            spell_slots = {
                k: v for k, v in spell_data.items()
                if k.startswith("spell_slots_level_") and v > 0
            }

            if spell_slots:
                max_spell_level = max(int(k.split("_")[-1]) for k in spell_slots)

        # Spell List
        class_spells_json = client.get(class_data["spells"])
        spells_raw = class_spells_json.get("results", [])

    # organizar por nível
        spells_by_level = {}
        for spell in spells_raw:
            lvl = spell["level"]
            name = spell["name"]
            spells_by_level.setdefault(lvl, []).append(name)

        # Cantrips
        cantrips_known = spell_data.get("cantrips_known", 0)
        cantrips_pool = spells_by_level.get(0, [])

        cantrips = random.sample(
            cantrips_pool,
            min(cantrips_known, len(cantrips_pool))
        )

        spells_known = None
        spells_prepared = None
        spellbook = None
        
        available_spells = []
        for lvl in range(1, max_spell_level + 1):
            available_spells.extend(spells_by_level.get(lvl, []))


        if "spells_known" in spell_data:
            total_known = spell_data["spells_known"]

            spells_known = []

            weights = {
                lvl: (max_spell_level - lvl + 1)
                for lvl in range(1, max_spell_level + 1)
            }

            for lvl in range(1, max_spell_level + 1):
                pool = spells_by_level.get(lvl, [])
                if pool:
                    spell = random.choice(pool)
                    if spell not in spells_known:
                        spells_known.append(spell)

            while len(spells_known) < total_known:
                levels = list(weights.keys())
                probs = list(weights.values())

                chosen_level = random.choices(levels, weights=probs, k=1)[0]
                pool = spells_by_level.get(chosen_level, [])

                if not pool:
                    continue

                spell = random.choice(pool)

                if spell not in spells_known:
                    spells_known.append(spell)

        elif random_class in ["cleric", "druid", "paladin", "wizard"]:

            if random_class in ["cleric", "druid"]:
                total_prepared = casting_mod + level

            elif random_class == "paladin":
                total_prepared = casting_mod + (level // 2)

            elif random_class == "wizard":
                total_prepared = casting_mod + level

            spells_prepared = random.sample(
                available_spells,
                min(total_prepared, len(available_spells))
            )

        # 📖 Wizard spellbook
            if random_class == "wizard":
                spellbook_size = 6 + ((level - 1) * 2)

                spellbook = random.sample(
                    available_spells,
                    min(spellbook_size, len(available_spells))
                )
        def group_spells_by_level(spell_list, spells_by_level):
            grouped = {}

            for lvl, spells in spells_by_level.items():
                filtered = [s for s in spells if s in (spell_list or [])]
                if filtered:
                    grouped[lvl] = filtered

            return grouped
        spell_info = {
            "ability": spellcasting_ability,
            "mod": casting_mod,
            "save_dc": spell_save_dc,
            "attack": spell_attack,
            "slots": spell_slots,
            "cantrips": cantrips,
            "spells_known": group_spells_by_level(spells_known, spells_by_level),
            "spells_prepared": group_spells_by_level(spells_prepared, spells_by_level),
            "spellbook": group_spells_by_level(spellbook, spells_by_level)
        }

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
        "features": features,
        "spellcasting": spell_info,
    }

# OutPut DeBug

def format_skill(skill):
    if skill.startswith("skill-"):
        skill = skill.replace("skill-", "")
    return skill.replace("-", " ").title()

def print_spell_group(title, spell_dict):
    if not spell_dict:
        return

    print(f"\n  {title}:")
    for lvl in sorted(spell_dict.keys()):
        print(f"    Level {lvl}:")
        for spell in sorted(spell_dict[lvl]):
            print(f"      - {spell}")

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
    if char['initiative'] >= 0:
        print(f"Initiative: +{char['initiative']}")
    if char['initiative'] < 0:
        print(f"Initiative: {char['initiative']}")
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
    print("Inventory: ")
    for item in char['inventory']:
        print(f"  - {item['name']}{f' x{item["quantity"]}' if item['quantity'] > 1 else ''}")
    print("\nFeatures:")
    for feat in char["features"]:
         print(f"  - {feat}")
    if char.get("spellcasting"):
        spell = char["spellcasting"]

        print("\n" + "=" * lines_width)
        print("Spellcasting:")
        print(f"  Ability: {spell['ability'].upper()}")
        print(f"  Save DC: {spell['save_dc']}")
        print(f"  Attack Mod: {spell['attack']:+}")

        if spell["cantrips"]:
            print("\n  Cantrips:")
            for s in sorted(spell["cantrips"]):
                print(f"    - {s}")
        print_spell_group("Spells Known", spell["spells_known"])
        print_spell_group("Spells Prepared", spell["spells_prepared"])
        print_spell_group("Spellbook", spell["spellbook"])
