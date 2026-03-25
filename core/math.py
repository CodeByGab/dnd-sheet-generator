import random

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

def up_asi(ability_score, priority, level):
    asi_levels = [4, 8, 12, 16, 19]

    for asi in asi_levels:

        if level < asi:
            break

        points = 2

        for stat in priority:
            if points == 0:
                break

            current = ability_score[stat]

            if current >= 20:
                continue

            # quanto pode aumentar sem passar de 20
            increase = min(points, 20 - current)

            ability_score[stat] += increase
            points -= increase

    return ability_score

def get_level(args):
    if args and 1 <= args <= 20:
        return args
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

