BASE_URL = "https://www.dnd5eapi.co/api"

BASE_STATS = [15, 14, 13, 12, 10, 8]

ABILITIES = ["str", "dex", "con", "int", "wis", "cha"]

CLASS_PRIORITY = {
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
