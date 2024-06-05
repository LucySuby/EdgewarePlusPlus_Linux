# Copyright (C) 2024 LewdDevelopment
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import argparse
import json
import logging
import os
import shutil
import sys
from pathlib import Path

import filetype
import yaml
from voluptuous import All, Optional, Range, Schema, Union, Url


def write_json(dictionary, path):
    logging.info(f"Writing {path.name}")
    with open(path, "w") as f:
        json.dump(dictionary, f)


def make_media(source_path, build_path) -> set[str]:
    """Returns a set of existing, valid moods"""

    media = dict()
    media_path = source_path / "media"

    if not os.path.isdir(media_path):
        logging.error(f"{media_path} does not exist or is not a directory, unable to read media")
        return set()

    moods = os.listdir(media_path)
    if len(moods) == 0:
        logging.error("Media directory exists, but it is empty")
        return set()

    for mood in moods:
        mood_path = media_path / mood
        if not os.path.isdir(mood_path):
            logging.warning(f"{mood_path} is not a directory")
            continue

        mood_media = os.listdir(mood_path)
        if len(mood_media) == 0:
            logging.warning(f"Mood directory {mood} exists, but it is empty")
            continue

        logging.info(f"Copying media from mood {mood}")
        media[mood] = []
        for filename in mood_media:
            file_path = mood_path / filename

            file_type = None
            if filetype.is_image(file_path):
                file_type = "img"
            elif filetype.is_video(file_path):
                file_type = "vid"
            elif filetype.is_audio(file_path):
                file_type = "aud"

            if file_type:
                shutil.copyfile(file_path, build_path / file_type / filename)
                media[mood].append(filename)
            else:
                logging.warning(f"{file_path} is not an image, video, or audio file")

    write_json(media, build_path / "media.json")
    return set(media.keys())


def make_subliminals(source_path, build_path):
    subliminal_path = source_path / "subliminals"
    if not os.path.isdir(subliminal_path):
        return

    subliminals = os.listdir(subliminal_path)
    if len(subliminals) == 0:
        logging.warning("Subliminals directory exists, but it is empty")

    logging.info("Copying subliminals")
    os.makedirs(build_path / "subliminals", exist_ok=True)
    for filename in subliminals:
        file_path = subliminal_path / filename
        if filetype.is_image(file_path):
            shutil.copyfile(file_path, build_path / "subliminals" / filename)
        else:
            logging.warning(f"{file_path} is not an image")


def make_wallpapers(source_path, build_path):
    wallpaper_path = source_path / "wallpapers"

    if not os.path.isdir(wallpaper_path):
        logging.warning(f"{wallpaper_path} does not exist or is not a directory")
        return

    wallpapers = os.listdir(wallpaper_path)
    if len(wallpapers) == 0:
        logging.warning("Wallpaper directory exists, but it is empty")
        return

    logging.info("Copying wallpapers")
    default_found = False
    for filename in wallpapers:
        file_path = wallpaper_path / filename
        default_found = default_found or filename == "wallpaper.png"
        if filetype.is_image(file_path):
            shutil.copyfile(file_path, build_path / filename)
        else:
            logging.warning(f"{file_path} is not an image")

    if not default_found:
        logging.warning("No default wallpaper.png found")


def make_icon(source_path, build_path):
    icon_path = source_path / "icon.ico"
    if not os.path.exists(icon_path):
        return

    if filetype.is_image(icon_path):
        logging.info("Copying icon")
        shutil.copyfile(icon_path, build_path / "icon.ico")
    else:
        logging.warning(f"{icon_path} is not an image")


def make_loading_splash(source_path, build_path):
    loading_splash_found = False
    for extension in ["png", "gif", "jpg", "jpeg", "bmp"]:
        filename = f"loading_splash.{extension}"
        loading_splash_path = source_path / filename
        if not os.path.exists(loading_splash_path):
            continue

        if loading_splash_found:
            logging.warning(f"Found multiple loading splashes, ignoring {loading_splash_path}")
            continue

        if filetype.is_image(loading_splash_path):
            logging.info("Copying loading splash")
            shutil.copyfile(loading_splash_path, build_path / filename)
            loading_splash_found = True
        else:
            logging.warning(f"{loading_splash_path} is not an image")


def make_info(pack, build_path):
    if not pack["info"]["generate"]:
        logging.info("Skipping info.json")
        return

    Schema({
        "generate": bool,
        "name": str,
        "id": str,
        "creator": str,
        "version": str,
        "description": str,
    })(pack["info"])  # fmt: skip

    info = {
        "name": pack["info"]["name"],
        "id": pack["info"]["id"],
        "creator": pack["info"]["creator"],
        "version": pack["info"]["version"],
        "description": pack["info"]["description"].strip(),
    }

    write_json(info, build_path / "info.json")


def make_discord(pack, build_path):
    if not pack["discord"]["generate"]:
        logging.info("Skipping discord.dat")
        return

    Schema({"generate": bool, "status": str})(pack["discord"])

    with open(build_path / "discord.dat", "w") as f:
        logging.info("Writing discord.dat")
        f.write(pack["discord"]["status"])


def make_captions(pack, build_path):
    if not pack["captions"]["generate"]:
        logging.info("Skipping captions.json")
        return

    Schema({
        "generate": bool,
        "close-text": str,
        "default-captions": [str],
        "prefixes": Union(
            [
                {
                    "name": str,
                    Optional("chance"): All(Union(int, float), Range(min=0, max=100)),
                    Optional("max-clicks"): All(int, Range(min=1)),
                    "captions": [str],
                }
            ],
            None,
        ),
    })(pack["captions"])  # fmt: skip

    captions = {
        "subtext": pack["captions"]["close-text"],
        "default": pack["captions"]["default-captions"],
        "prefix": [],
        "prefix_settings": {},
    }

    prefixes = pack["captions"]["prefixes"]
    if prefixes:
        for prefix in prefixes:
            prefix_name = prefix["name"]

            captions["prefix"].append(prefix_name)
            captions[prefix_name] = prefix["captions"]

            prefix_settings = {}
            if "chance" in prefix:
                prefix_settings["chance"] = prefix["chance"]
            if "max-clicks" in prefix:
                prefix_settings["max"] = prefix["max-clicks"]

            if prefix_settings:
                captions["prefix_settings"][prefix_name] = prefix_settings

    write_json(captions, build_path / "captions.json")


def make_prompt(pack, build_path):
    if not pack["prompt"]["generate"]:
        logging.info("Skipping prompt.json")
        return

    Schema({
        "generate": bool,
        "submit-text": str,
        "minimum-length": All(int, Range(min=1)),
        "maximum-length": All(int, Range(min=pack["prompt"]["minimum-length"])),
        "default-prompts": {
            "weight": All(int, Range(min=0)),
            "prompts": Union([str], None),
        },
        "moods": Union(
            [
                {
                    "name": str,
                    "weight": All(int, Range(min=0)),
                    "prompts": [str],
                }
            ],
            None,
        ),
    })(pack["prompt"])  # fmt: skip

    prompt = {
        "subtext": pack["prompt"]["submit-text"],
        "minLen": pack["prompt"]["minimum-length"],
        "maxLen": pack["prompt"]["maximum-length"],
        "moods": [],
        "freqList": [],
    }

    default = pack["prompt"]["default-prompts"]
    if default["prompts"]:
        prompt["moods"].append("default")
        prompt["freqList"].append(default["weight"])
        prompt["default"] = default["prompts"]

    moods = pack["prompt"]["moods"]
    if moods:
        for mood in moods:
            mood_name = mood["name"]

            prompt["moods"].append(mood_name)
            prompt["freqList"].append(mood["weight"])
            prompt[mood_name] = mood["prompts"]

    write_json(prompt, build_path / "prompt.json")


def make_web(pack, build_path):
    if not pack["web"]["generate"]:
        logging.info("Skipping web.json")
        return

    Schema({
        "generate": bool,
        "urls": [
            {
                "url": Url(),
                "mood": str,
                Optional("args"): [str]
            }
        ],
    })(pack["web"])  # fmt: skip

    web = {"urls": [], "moods": [], "args": []}

    for url in pack["web"]["urls"]:
        web["urls"].append(url["url"])
        web["moods"].append(url["mood"])

        args_string = ""
        if "args" in url:
            for arg in url["args"]:
                if "," in arg:
                    logging.error(f"Web args must not contain commas, invalid arg: {arg}")
                else:
                    if args_string != "":
                        args_string += ","
                    args_string += f"{arg}"

        web["args"].append(args_string)

    write_json(web, build_path / "web.json")


def make_corruption(pack, build_path, moods):
    if not pack["corruption"]["generate"]:
        logging.info("Skipping corruption.json")
        return

    Schema({
        "generate": bool,
        "levels": [
            {
                Optional("add-moods"): [str],
                Optional("remove-moods"): [str],
                Optional("wallpaper"): str,
                Optional("config"): dict,
            }
        ],
    })(pack["corruption"])  # fmt: skip

    corruption = {"moods": {}, "wallpapers": {}, "config": {}}

    active_moods = set()
    for i, level in enumerate(pack["corruption"]["levels"]):
        n = str(i + 1)
        corruption["moods"][n] = {}

        remove = []
        if "remove-moods" in level:
            for mood in level["remove-moods"]:
                if mood in active_moods:
                    remove.append(mood)
                    active_moods.remove(mood)
                else:
                    logging.warning(f"Corruption level {n} is trying to remove an inactive mood {mood}, skipping")
        corruption["moods"][n]["remove"] = remove

        add = []
        if "add-moods" in level:
            for mood in level["add-moods"]:
                if mood in moods:
                    add.append(mood)
                    active_moods.add(mood)
                else:
                    logging.warning(f"Corruption level {n} is trying to add a nonexistent mood {mood}, skipping")
        corruption["moods"][n]["add"] = add

        if "wallpaper" in level:
            corruption["wallpapers"][n] = level["wallpaper"]

        if "config" in level:
            corruption["config"][n] = level["config"]

    write_json(corruption, build_path / "corruption.json")


# TODO: config.json


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", help="pack source directory")
    parser.add_argument("-o", "--output", default="build", help="output directory name")
    parser.add_argument("-n", "--new", action="store_true", help="create a new pack template and exit")
    args = parser.parse_args()

    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    root = Path(__file__).parent
    source_path = root / args.source
    if args.new:
        if os.path.exists(source_path):
            logging.error(f"{source_path} already exists")
        else:
            os.makedirs(source_path / "media" / "default", exist_ok=True)
            os.makedirs(source_path / "subliminals", exist_ok=True)
            os.makedirs(source_path / "wallpapers", exist_ok=True)
            shutil.copyfile(root / "default_pack.yml", source_path / "pack.yml")

            logging.info(f"Created a template for a new pack at {source_path}")

        sys.exit()
    elif not os.path.isdir(source_path):
        logging.error(f"{source_path} does not exist or is not a direcory")
        sys.exit()

    build_path = root / args.output

    try:
        os.makedirs(build_path / "img", exist_ok=True)
        os.makedirs(build_path / "vid", exist_ok=True)
        os.makedirs(build_path / "aud", exist_ok=True)

        moods = make_media(source_path, build_path)
        make_subliminals(source_path, build_path)
        make_wallpapers(source_path, build_path)
        make_icon(source_path, build_path)
        make_loading_splash(source_path, build_path)

        with open(source_path / "pack.yml", "r") as f:
            pack = yaml.safe_load(f)
            make_info(pack, build_path)
            make_discord(pack, build_path)
            make_captions(pack, build_path)
            make_prompt(pack, build_path)
            make_web(pack, build_path)
            make_corruption(pack, build_path, moods)
    except Exception as e:
        logging.error(e)


if __name__ == "__main__":
    main()
