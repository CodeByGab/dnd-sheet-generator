import os
import json
import requests
import random

from config import BASE_URL

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

def get_name(race, custom_name):
    if custom_name:
        return custom_name
    
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

def local_request(path):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except:
        print(f"[ERRO] Não foi possível carregar {path}")
        return None

def get_backgrounds():
    data = local_request("cache/backgrounds/index.json")
    return data if data else [{"index": "acolyte", "skills": []}]

