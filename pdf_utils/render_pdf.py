from PyPDFForm import PdfWrapper
from core import math

PDF_NAME = "pdf_utils/chac_sheet.pdf"
OUTPUT_PRE = "pdf_utils/output/"

def generate_pdf(chac):

    character_infos = {
            "CharacterName": chac["name"],
            "ClassLevel": f"{chac['class']}  {chac['level']}",
            "Background": chac["background"],
            "Race ": chac["race"],
            "STR": chac["stats"]["str"],
            "STRmod": math.calc_stt(chac["stats"]["str"]),
            "DEX": chac["stats"]["dex"],
            "DEXmod ": math.calc_stt(chac["stats"]["dex"]),
            "CON": chac["stats"]["con"],
            "CONmod": math.calc_stt(chac["stats"]["con"]),
            "INT": chac["stats"]["int"],
            "INTmod": math.calc_stt(chac["stats"]["int"]),
            "WIS": chac["stats"]["wis"],
            "WISmod": math.calc_stt(chac["stats"]["wis"]),
            "CHA": chac["stats"]["cha"],
            "CHamod": math.calc_stt(chac["stats"]["cha"]),
            "ProfBonus": chac["proficiency_bonus"],
            "Passive": chac["pass_perception"],
            "HPMax": chac["hp"],
            "HPCurrent": chac["hp"],
            "AC": chac["ac"],
            "Initiative": chac["initiative"],
            "Speed": chac["speed"],
            "HD": chac["hit_die"],
       }

    filled = PdfWrapper(PDF_NAME, need_appearances=True).fill(character_infos)

    filled.write(f"{OUTPUT_PRE}{chac['name']} {chac['class']} {chac['level']}.pdf")

    #     "hit_die": hit_die,
    #     "stats": ability_scores,
    #     "saves": {
    #         st1: save1,
    #         st2: save2
    #     },
    #     "skills": prof_skills,
    #     "proficiencies": proficiencies,
    #     "inventory": inventory,
    #     "features": features,
    #     "spellcasting": spell_info,
    # }
    #

