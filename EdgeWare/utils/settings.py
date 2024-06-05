import ast
import json
import logging
import os
import shutil

from utils.paths import Data, Defaults


class Settings:
    default = {}
    config = {}

    def __init__(self):
        self.load_config()
        self.load_constants()

    def __getitem__(self, key):
        return self.config[key]

    def __setitem__(self, key, value):
        self.config[key] = value

    def get(self, key):
        return self.config.get(key)

    # Loads settings from the config file or generates / updates it from the default
    # configuration
    def load_config(self):
        logging.info("loading config...")

        # Checking if config file exists and then writing the default config settings
        # to a new file if it doesn't
        if not os.path.exists(Data.CONFIG):
            shutil.copyfile(Defaults.CONFIG, Data.CONFIG)
            logging.warning("could not find config.cfg, wrote new file from default config values.")

        with open(Defaults.CONFIG, "r") as f:
            self.default = json.loads(f.read())
            logging.info("read in settings from default.json")

        with open(Data.CONFIG, "r") as f:
            self.config = json.loads(f.read())
            logging.info("read in settings from config.cfg")

        # If the length of the settings are different, attempt to add any missing
        # settings from the defaults to the actual config
        if len(self.config) != len(self.default):
            logging.warning("config JSON len mismatch, regenerating new config with missing keys...")
            for key in self.default:
                if key not in self.config:
                    self.config[key] = self.default[key]
            self.config["versionplusplus"] = self.default["versionplusplus"]
            with open(Data.CONFIG, "w") as f:
                f.write(json.dumps(self.config))
                logging.info("wrote updated config to config.cfg")

        # TODO: Wallpapers should be stored as JSON objects
        try:
            self.config["wallpaperDat"] = ast.literal_eval(self.config["wallpaperDat"])
        except Exception as e:
            logging.warning(f"failed to parse wallpaper from string\n\tReason: {e}")

    def load_constants(self):
        # Popups
        self.DELAY = int(self.config["delay"])
        self.POPUP_CHANCE = int(self.config["popupMod"])
        self.SHOW_CAPTIONS = int(self.config["showCaptions"]) == 1
        self.HAS_LIFESPAN = int(self.config["timeoutPopups"]) == 1
        self.LIFESPAN = int(self.config["popupTimeout"])
        self.BUTTONLESS = int(self.config["buttonless"]) == 1
        self.MULTI_CLICK = int(self.config["multiClick"]) == 1
        self.OPACITY = int(self.config["lkScaling"])
        self.SINGLE_MODE = int(self.config["singleMode"]) == 1
        self.LANCZOS_MODE = int(self.config["antiOrLanczos"]) == 1

        # Moving popups
        self.MOVING_CHANCE = int(self.config["movingChance"])
        self.MOVING_SPEED = int(self.config["movingSpeed"])
        self.MOVING_RANDOM = int(self.config["movingRandom"]) == 1

        # Popup subliminals
        self.SUBLIMINAL_MODE = int(self.config["popupSubliminals"]) == 1
        self.SUBLIMINAL_CHANCE = int(self.config["subliminalsChance"])
        self.MAX_SUBLIMINALS = int(self.config["maxSubliminals"])
        self.SUBLIMINAL_ALPHA = int(self.config["subliminalsAlpha"]) / 100

        # Audio
        self.AUDIO_CHANCE = int(self.config["audioMod"])
        self.AUDIO_CAP = int(self.config["maxAudioBool"]) == 1
        self.AUDIO_MAX = int(self.config["maxAudio"])

        # Video
        self.VIDEO_CHANCE = int(self.config["vidMod"])
        self.VIDEO_CAP = int(self.config["maxVideoBool"]) == 1
        self.VIDEO_MAX = int(self.config["maxVideos"])
        self.VIDEO_VOLUME = min(max(0, float(self.config["videoVolume"]) / 100), 1)
        self.VIDEOS_ONLY = int(self.config["onlyVid"]) == 1
        self.VLC_MODE = int(self.config["vlcMode"]) == 1

        # Web
        self.WEB_CHANCE = int(self.config["webMod"])
        self.DOWNLOAD_ENABLED = int(self.config["downloadEnabled"]) == 1
        self.USE_WEB_RESOURCE = int(self.config["useWebResource"]) == 1
        self.WEB_OPEN = int(self.config["webPopup"]) == 1

        # Prompts
        self.PROMPT_CHANCE = int(self.config["promptMod"])
        self.MAX_MISTAKES = int(self.config["promptMistakes"])

        # Caption popups
        self.CAP_POP_CHANCE = int(self.config["capPopChance"])
        self.CAP_OPACITY = int(self.config["capPopOpacity"])
        self.CAP_TIMER = int(self.config["capPopTimer"])
        self.SUBLIMINAL_MOOD = int(self.config["capPopMood"]) == 1

        # Panic
        self.PANIC_DISABLED = int(self.config["panicDisabled"]) == 1
        self.PANIC_KEY = self.config["panicButton"]

        # Fill drive
        self.DRIVE_PATH = self.config["drivePath"]
        self.MAX_FILL_THREADS = int(self.config["maxFillThreads"])
        self.FILL_MODE = int(self.config["fill"]) == 1
        self.FILL_DELAY = int(self.config["fill_delay"])
        self.REPLACE_MODE = int(self.config["replace"]) == 1
        self.REPLACE_THRESHOLD = int(self.config["replaceThresh"])
        try:
            self.AVOID_LIST = self.config["avoidList"].split(">")
        except Exception as e:
            self.AVOID_LIST = ["EdgeWare", "AppData"]  # default avoid list for fill/replace
            logging.warning(f"failed to set avoid list\n\tReason: {e}")

        # Lowkey mode
        self.LOWKEY_MODE = int(self.config["lkToggle"]) == 1
        self.LOWKEY_CORNER = int(self.config["lkCorner"])

        # Denial mode
        self.DENIAL_MODE = int(self.config["denialMode"]) == 1
        self.DENIAL_CHANCE = int(self.config["denialChance"])

        # Hibernate mode
        self.HIBERNATE_MODE = int(self.config["hibernateMode"]) == 1
        self.HIBERNATE_MIN = int(self.config["hibernateMin"])
        self.HIBERNATE_MAX = int(self.config["hibernateMax"])
        self.WAKEUP_ACTIVITY = int(self.config["wakeupActivity"])
        self.HIBERNATE_TYPE = self.config["hibernateType"]
        self.HIBERNATE_TRUTH = self.config["hibernateType"]  # TODO: Purpose?
        self.HIBERNATE_LENGTH = int(self.config["hibernateLength"])
        self.FIX_WALLPAPER = int(self.config["fixWallpaper"]) == 1
        self.PUMP_SCARE_OFFSET = int(self.config["pumpScareOffset"])
        if self.HIBERNATE_MODE and self.HIBERNATE_TYPE == "Chaos" and os.path.exists(Data.CHAOS_TYPE):
            with open(Data.CHAOS_TYPE, "r") as ct:
                self.HIBERNATE_TYPE = ct.read()

        # Mitosis mode
        self.MITOSIS_MODE = int(self.config["mitosisMode"]) == 1
        self.MITOSIS_STRENGTH = int(self.config["mitosisStrength"])

        # Timer mode
        self.TIMER_MODE = int(self.config["timerMode"]) == 1

        # Corruption
        self.CORRUPTION_MODE = int(self.config["corruptionMode"]) == 1
        self.CORRUPTION_FADE = self.config["corruptionFadeType"]
        self.CORRUPTION_TRIGGER = self.config["corruptionTrigger"]
        # adding all three as individual vars instead of checking for trigger type because of an idea: randomized corruption per-launch?
        self.CORRUPTION_TIME = int(self.config["corruptionTime"])
        self.CORRUPTION_POPUPS = int(self.config["corruptionPopups"])
        self.CORRUPTION_LAUNCHES = int(self.config["corruptionLaunches"])
        self.CORRUPTION_DEVMODE = int(self.config["corruptionDevMode"]) == 1
        self.CORRUPTION_WALLCYCLE = int(self.config["corruptionWallpaperCycle"]) == 1
        self.CORRUPTION_THEMECYCLE = int(self.config["corruptionThemeCycle"]) == 1
        self.CORRUPTION_PURITY = int(self.config["corruptionPurityMode"]) == 1
        self.CORRUPTION_FULL = int(self.config["corruptionFullPerm"]) == 1

        # Miscellaneous
        self.THEME = self.config["themeType"]
        self.SHOW_ON_DISCORD = int(self.config["showDiscord"]) == 1
        self.LOADING_FLAIR = int(self.config["showLoadingFlair"]) == 1
        self.DESKTOP_ICONS = int(self.config["desktopIcons"]) == 1
        self.ROTATE_WALLPAPER = int(self.config["rotateWallpaper"]) == 1
        self.MOOD_OFF = int(self.config["toggleMoodSet"]) == 1
        self.MOOD_FILENAME = int(self.config["captionFilename"]) == 1
