import json
import os
import random as rand
import sys
import tkinter as tk
from pathlib import Path
from tkinter import RAISED, Button, Frame, Label, Text, Tk, font, messagebox

from screeninfo import get_monitors

sys.path.append(str(Path(__file__).parent.parent))
from utils import utils
from utils.paths import Data, Resource
from utils.settings import Settings

SYS_ARGS = sys.argv.copy()
SYS_ARGS.pop(0)

settings = Settings()

has_data = False
text_data = {}
submission_text = "I Submit <3"
command_text = "Type for me, slut~"
mood_data = {}

MOOD_ID = "0"
if len(SYS_ARGS) >= 1 and SYS_ARGS[0] != "0":
    MOOD_ID = SYS_ARGS[0].strip("-")

if MOOD_ID != "0":
    if os.path.exists(Data.MOODS / f"{MOOD_ID}.json"):
        with open(Data.MOODS / f"{MOOD_ID}.json", "r") as f:
            mood_data = json.loads(f.read())
    elif os.path.exists(Data.UNNAMED_MOODS / f"{MOOD_ID}.json"):
        with open(Data.UNNAMED_MOODS / f"{MOOD_ID}.json", "r") as f:
            mood_data = json.loads(f.read())

if os.path.exists(Resource.PROMPT):
    has_data = True
    with open(Resource.PROMPT, "r") as f:
        text_data = json.loads(f.read())
        try:
            submission_text = text_data["subtext"]
        except Exception:
            print("no subtext")
        try:
            command_text = text_data["commandtext"]
        except Exception:
            print("no commandtext")

if not has_data:
    messagebox.showerror("Prompt Error", 'Resource folder contains no "prompt.json". Either set prompt freq to 0 or add "prompt.json" to resource folder.')


def unbordered_window():
    if not has_data:
        exit()
    root = Tk()

    fore = "#000000"
    back = "#f0f0f0"
    textb = "#ffffff"
    textf = "#000000"
    mainfont = font.nametofont("TkDefaultFont")

    if settings.THEME == "Dark":
        fore = "#f9faff"
        back = "#282c34"
        textb = "#1b1d23"
        textf = "#f9faff"
    if settings.THEME == "The One":
        fore = "#00ff41"
        back = "#282c34"
        textb = "#1b1d23"
        textf = "#00ff41"
        mainfont.configure(family="Consolas", size=8)
    if settings.THEME == "Ransom":
        fore = "#ffffff"
        back = "#841212"
        textb = "#ffffff"
        textf = "#000000"
        mainfont.configure(family="Arial Bold")
    if settings.THEME == "Goth":
        fore = "#ba9aff"
        back = "#282c34"
        textb = "#db7cf2"
        textf = "#6a309d"
        mainfont.configure(family="Constantia")
    if settings.THEME == "Bimbo":
        fore = "#ff3aa3"
        back = "#ffc5cd"
        textb = "#ffc5cd"
        textf = "#f43df2"
        mainfont.configure(family="Constantia")

    root.configure(background=back)
    label = tk.Label(root, text="\n" + command_text + "\n", bg=back, fg=fore)
    label.pack()

    txt = build_text()

    monitor = rand.choice(get_monitors())  # TODO: Only on primary monitor?
    wid = monitor.width / 4
    hgt = monitor.height / 2

    text_label = Label(root, text=txt, wraplength=wid, bg=back, fg=fore)
    text_label.pack()

    root.geometry("%dx%d+%d+%d" % (wid, hgt, monitor.x + 2 * wid - wid / 2, monitor.y + hgt - hgt / 2))

    root.frame = Frame(root, borderwidth=2, relief=RAISED, bg=back)
    root.frame.pack_propagate(True)
    root.wm_attributes("-topmost", 1)
    utils.set_borderless(root)

    input_box = Text(root, bg=textb, fg=textf)
    input_box.pack()

    sub_button = Button(
        root,
        text=submission_text,
        command=lambda: check_total(root, txt, input_box.get(1.0, "end-1c")),
        bg=back,
        fg=fore,
        activebackground=back,
        activeforeground=fore,
    )
    sub_button.place(x=wid - 5 - sub_button.winfo_reqwidth(), y=hgt - 5 - sub_button.winfo_reqheight())
    root.mainloop()


def build_text():
    mood_list = text_data["moods"]
    freq_list = text_data["freqList"]
    if MOOD_ID != "0":
        for i, mood in enumerate(mood_list):
            if mood not in mood_data["prompts"]:
                del mood_list[i - 1]
                del freq_list[i - 1]
    output_phrase_count = rand.randint(int(text_data["minLen"]), int(text_data["maxLen"]))
    str_var = ""
    selection = rand.choices(mood_list, freq_list, k=1)
    for i in range(output_phrase_count):
        str_var += text_data[selection[0]][rand.randrange(0, len(text_data[selection[0]]))] + " "
    # str_var += MOOD_ID
    return str_var.strip()


# Checks that the number of mistakes is at most MAX_MISTAKES and if so,
# closes the prompt window. The number of mistakes is computed as the edit
# (Levenshtein) distance between a and b.
# https://en.wikipedia.org/wiki/Levenshtein_distance
def check_total(root, a, b):
    d = [[j for j in range(0, len(b) + 1)]] + [[i] for i in range(1, len(a) + 1)]

    for j in range(1, len(b) + 1):
        for i in range(1, len(a) + 1):
            d[i].append(
                min(
                    d[i - 1][j] + 1,
                    d[i][j - 1] + 1,
                    d[i - 1][j - 1] + (0 if a[i - 1] == b[j - 1] else 1)
                )
            )  # fmt: skip

    if d[len(a)][len(b)] <= settings.MAX_MISTAKES:
        root.destroy()


try:
    unbordered_window()
except Exception as e:
    messagebox.showerror("Prompt Error", "Could not create prompt window.\n[" + str(e) + "]")
