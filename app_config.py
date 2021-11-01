import sys
from os import path
from yaml import safe_load

def rootPath():
    try:
        return sys._MEIPASS
    except Exception:
        return path.abspath(".")

ROOT_DIR = rootPath()
CONFIG_PATH = path.join(ROOT_DIR, 'resources\\config.yml')
ICON_PATH = path.join(ROOT_DIR, 'resources\\icon.ico')

# Image files
WAITING_FOR_FISH_IMAGE_PATH = path.join(ROOT_DIR, 'resources\\img\\waiting_for_fish.jpg')
FISH_NOTICED_IMAGE_PATH = path.join(ROOT_DIR, 'resources\\img\\fish_noticed.jpg')
CAN_BE_REELED_IMAGE_PATH = path.join(ROOT_DIR, 'resources\\img\\can_be_reeled.jpg')

# rzctl.dll 
RZCTL_DLL_PATH = path.join(ROOT_DIR, 'resources\\rzctl.dll')

config = safe_load(open(CONFIG_PATH))