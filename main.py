import argparse
from core import math
from core.chac_logic import generate_character, print_character
from pdf_utils.render_pdf import generate_pdf

parser = argparse.ArgumentParser()
parser.add_argument("--level", type=int, help="Character Level")
parser.add_argument("--class", dest="char_class", type=str, help="Character Class")
parser.add_argument("--race", type=str, help="Character Race")
parser.add_argument("--name", type=str, help="Character Name")
args = parser.parse_args()

char = generate_character(args)
# print_character(char, math)
generate_pdf(char)
