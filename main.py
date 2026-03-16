import requests
import random
classes = requests.get("https://www.dnd5eapi.co/api/classes").json()

random_class = random.choice(data["results"])

data2 = requests.get("https://www.dnd5eapi.co/api/2014/classes/{}".format(random_class["index"])).json()

racesData = requests.get("https://www.dnd5eapi.co/api/2014/races").json()
random_race = random.choice(racesData["results"])

ability_score = requests.get("https://www.dnd5eapi.co/api/2014/ability-scores").json()
background = requests.get("https://www.dnd5eapi.co/api/2014/background").json()


