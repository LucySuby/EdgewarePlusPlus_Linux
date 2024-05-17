# This sublabel.pyw originally provided very generously by u/basicmo!

import json
#import logging
import os
import random
import random as rand
import sys
import tkinter as tk
from pathlib import Path

from screeninfo import get_monitors

sys.path.append(str(Path(__file__).parent.parent))
from utils import utils
from utils.paths import Data, Resource
from utils.settings import Settings

SYS_ARGS = sys.argv.copy()
SYS_ARGS.pop(0)

#utils.init_logging("sublabel")

settings = Settings()

MOOD_ID = "0"
if len(SYS_ARGS) >= 1 and SYS_ARGS[0] != "0":
    MOOD_ID = SYS_ARGS[0].strip("-")

if MOOD_ID != "0":
    if os.path.exists(Data.MOODS / f"{MOOD_ID}.json"):
        with open(Data.MOODS / f"{MOOD_ID}.json") as f:
            mood_data = json.loads(f.read())
    elif os.path.exists(Data.UNNAMED_MOODS / f"{MOOD_ID}.json"):
        with open(Data.UNNAMED_MOODS / f"{MOOD_ID}.json") as f:
            mood_data = json.loads(f.read())

# background is one hex value off here, because it looks pretty ugly if they're different colours, so we keep them close so there is no visual difference
if settings.THEME == "Dark":
    fore = "#f9faff"
    back = "#f9fafe" if utils.is_windows() else "#282c34"
    mainfont = "Segoe UI"
elif settings.THEME == "The One":
    fore = "#00ff41"
    back = "#00ff42" if utils.is_windows() else "#282c34"
    mainfont = "Consolas"
elif settings.THEME == "Ransom":
    fore = "#ffffff"
    back = "#fffffe" if utils.is_windows() else "#841212"
    mainfont = "Arial Bold"
elif settings.THEME == "Goth":
    fore = "#ba9aff"
    back = "#ba9afe" if utils.is_windows() else "#282c34"
    mainfont = "Constantia"
elif settings.THEME == "Bimbo":
    fore = "#ff3aa3"
    back = "#ff3aa4" if utils.is_windows() else "#ffc5cd"
    mainfont = "Constantia"
else:
    fore = "#000000"
    back = "#000001" if utils.is_windows() else "#f0f0f0"
    mainfont = "Segoe UI"


def display_subliminal_message():
    # Load subliminal messages from captions.json
    def load_subliminal_messages():
        try:
            with open(Resource.CAPTIONS, "r") as file:
                l = json.load(file)
                if l.get("subliminals", []) and settings.SUBLIMINAL_MOOD:
                    return l.get("subliminals", [])
                else:
                    if "prefix" in l:
                        del l["prefix"]
                    if "subtext" in l:
                        del l["subtext"]
                    if "prefix_settings" in l:
                        del l["prefix_settings"]
                    if MOOD_ID != "0":
                        allsub = []
                        for key in l:
                            if key in mood_data["captions"]:
                                allsub.append(l[key])
                    else:
                        allsub = list(l.values())
                    flatlist = [i for sublist in allsub for i in sublist]
                    # logging.info(flatlist)
                    return flatlist
        except Exception as e:
            print(f"failed to get sublabel prefixes. {e}")
            return []

    # Get a random subliminal message
    def get_random_subliminal():
        subliminal_messages = load_subliminal_messages()
        if subliminal_messages:
            return random.choice(subliminal_messages)
        else:
            return "No subliminal messages found."

    # Create the label
    label = tk.Label(fg=fore, bg=back)

    # Choose a screen for the window
    monitor = rand.choice(get_monitors())

    # Calculate the font size based on screen resolution
    f_size = min(monitor.width, monitor.height) // 10  # Adjust the scaling factor as needed

    # Configure the font
    font = (mainfont, f_size)

    # Configure the label with the calculated font size and wrap the text
    label.config(font=font, wraplength=monitor.width // 1.5)

    # Set the text to a random subliminal message
    label.config(text=get_random_subliminal())

    # Calculate the position to center the window
    x = monitor.x + (monitor.width - label.winfo_reqwidth()) // 2
    y = monitor.y + (monitor.height - label.winfo_reqheight()) // 2

    # Configure the window
    label.master.overrideredirect(True)
    label.master.geometry(f"+{x}+{y}")
    label.master.lift()
    label.master.wm_attributes("-topmost", True)
    if utils.is_windows():
        label.master.wm_attributes("-disabled", True)
        label.master.wm_attributes("-transparentcolor", back)
    label.winfo_toplevel().attributes("-alpha", settings.CAP_OPACITY / 100)
    label.pack()

    # Update the label's size
    label.update_idletasks()

    # Schedule the destruction of the window after 0.3 seconds
    label.master.after(settings.CAP_TIMER, label.master.destroy)

    # Start the Tkinter event loop

    label.mainloop()


# Call the function to display the subliminal message
display_subliminal_message()
