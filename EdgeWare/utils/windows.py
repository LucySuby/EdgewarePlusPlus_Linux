import ctypes
import logging
import os
import subprocess
import tempfile
from pathlib import Path

from utils.paths import Defaults, Process

user = ctypes.windll.user32


def panic_script():
    os.startfile("panic.bat")


def set_borderless(root):
    root.overrideredirect(1)


def set_wallpaper(wallpaper_path: Path | str):
    if isinstance(wallpaper_path, Path):
        wallpaper_path = str(wallpaper_path.absolute())

    ctypes.windll.user32.SystemParametersInfoW(20, 0, wallpaper_path, 0)


HIDDEN_ATTR = 0x02
SHOWN_ATTR = 0x08


def hide_file(path: Path | str):
    if isinstance(path, Path):
        path = str(path.absolute())
    ctypes.windll.kernel32.SetFileAttributesW(path, HIDDEN_ATTR)


def show_file(path: Path | str):
    if isinstance(path, Path):
        path = str(path.absolute())
    ctypes.windll.kernel32.SetFileAttributesW(path, SHOWN_ATTR)


def open_directory(url: str):
    subprocess.Popen(f'explorer "{url}"')


def does_desktop_shortcut_exist(name: str):
    file = Path(name)
    return Path(os.path.expanduser("~/Desktop") / file.with_name(f"{file.name}.lnk")).exists()


def make_shortcut(title: str, process: Path, icon: Path, location: Path | None = None) -> bool:
    success = False

    file_name = f"{title.lower()}.lnk"
    file = (location if location else Path(os.path.expanduser("~\\Desktop"))) / file_name

    with tempfile.NamedTemporaryFile(
        "w",
        suffix=".bat",
        delete=False,
    ) as bat:
        bat.writelines(
            [
                "@echo off\n" 'set SCRIPT="%TEMP%\\%RANDOM%-%RANDOM%-%RANDOM%-%RANDOM%.vbs"\n',
                'echo Set oWS = WScript.CreateObject("WScript.Shell") >> %SCRIPT%\n',
                'echo sLinkFile = "' + str(file) + '" >> %SCRIPT%\n',
                "echo Set oLink = oWS.CreateShortcut(sLinkFile) >> %SCRIPT%\n",
                'echo oLink.WorkingDirectory = "' + str(process.parent) + '\\" >> %SCRIPT%\n',
                'echo oLink.IconLocation = "' + str(icon) + '" >> %SCRIPT%\n',
                'echo oLink.TargetPath = "' + str(process) + '" >> %SCRIPT%\n',
                "echo oLink.Save >> %SCRIPT%\n",
                "cscript /nologo %SCRIPT%\n",
                "del %SCRIPT%",
            ]
        )  # write built shortcut script text to temporary batch file

    try:
        logging.info(f"making shortcut to {process.name}")
        subprocess.run(bat.name)
        success = True
    except Exception as e:
        logging.warning(f"failed to call or remove temp batch file for making shortcuts\n\tReason: {_remove_username(e)}")

    if os.path.exists(bat.name):
        os.remove(bat.name)

    return success


def toggle_run_at_startup(state: bool):
    try:
        startup_path = Path(os.path.expanduser("~\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup"))
        if state:
            logging.info(f"trying to toggle startup bat to true")
            make_shortcut("Edgeware", Process.START, Defaults.ICON, startup_path)
            logging.info("toggled startup run on.")
        else:
            if os.path.exists(startup_path / "edgeware.lnk"):
                logging.info(f"trying to toggle startup bat to false")
                os.remove(startup_path / "edgeware.lnk")
                logging.info("toggled startup run off.")
    except Exception as e:
        logging.warning(f"failed to toggle startup bat.\n\tReason: {_remove_username(e)}")


def _remove_username(e):
    return str(e).lower().replace(os.environ["USERPROFILE"].lower().replace("\\", "\\\\"), "[USERNAME_REDACTED]")
