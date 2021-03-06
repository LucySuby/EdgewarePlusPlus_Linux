import ctypes
import os
import time
import webbrowser
import zipfile
import shutil
import json
import random as rand
import threading as thread

#delay(ms);y/n filling drive; y/n replacing images;(0-100) open web mod;(0-100) popup mod;y/n server only status (depracated from when plans included using nodejs server for abandoned functionality); slow fill mode
DEFAULT_CONFIG = '250;0;0;25;15;0;1'
PATH = os.path.abspath(os.getcwd())
AVOID_LIST = ['EdgeWare', 'AppData']
FILE_TYPES = ['png', 'jpg', 'jpeg']
MAX_FILL_THREADS = 8
IMG_REPLACE_THRESH = 500

liveFillThreads = 0
replaceThreadLive = False

if not os.path.exists(PATH + '\\resource\\'):
    with zipfile.ZipFile(PATH + '\\resources.zip', 'r') as obj:
        obj.extractall(PATH + '\\resource\\')
        
webJsonDat = ''
with open(PATH + '\\resource\\web.json', 'r') as webF:
    obj = webF.read()
    webJsonDat = json.loads(obj)

IMAGES = []
for img in os.listdir(PATH + '\\resource\\img\\'):
    IMAGES.append(PATH + '\\resource\\img\\' + img)
VIDEOS = []
for vid in os.listdir(PATH + '\\resource\\vid\\'):
    VIDEOS.append(PATH + '\\resource\\vid\\' + vid)
AUDIO = []
for aud in os.listdir(PATH + '\\resource\\aud\\'):
    AUDIO.append(PATH + '\\resource\\aud\\' + aud)

delay, fill, replace, webMod, popupMod, serverOnly, slowMode = 0, 0, 0, 0, 0, 0, 0

if not os.path.exists(PATH + '\\config.cfg'):
    with open(PATH + '\\config.cfg', 'w') as f:
        f.write(DEFAULT_CONFIG)

with open(PATH + '\\config.cfg', 'r') as f:
    cfgOptions = f.readline().split(';')
    delay = float(cfgOptions[0])
    fill = int(cfgOptions[1])
    replace = int(cfgOptions[2])
    webMod = int(cfgOptions[3])
    popupMod = int(cfgOptions[4])
    serverOnly = int(cfgOptions[5])
    slowMode = int(cfgOptions[6])
    f.close()

#set wallpaper
ctypes.windll.user32.SystemParametersInfoW(20, 0, PATH + '\\resource\\wallpaper.png', 0)

#selects url to be opened in new tab by web browser
def urlSelect(arg):
    return webJsonDat['urls'][arg] + webJsonDat['args'][arg].split(',')[rand.randrange(len(webJsonDat['args'][arg].split(',')))]

def main():
    annoyance(fill, replace)

#just checking %chance of doing annoyance options
def doRoll(mod):
    return mod > rand.randint(0, 100)

def annoyance(isFillingDrive, isReplacingImages):
    global liveFillThreads
    global replaceThreadLive
    while(True):
        if(doRoll(webMod)):
            webbrowser.open_new(urlSelect(rand.randrange(len(webJsonDat['urls']))))
        if(doRoll(popupMod)):
            os.startfile('popup.pyw')
        if(isFillingDrive == 1 and liveFillThreads < MAX_FILL_THREADS):
            thread.Thread(target=fillDrive).start()
        if(isReplacingImages == 1 and not replaceThreadLive):
            thread.Thread(target=replaceImages).start()
        time.sleep(float(delay) / 1000.0)

#fills drive with copies of images from /resource/img/
#   only targets User folders; none of that annoying elsaware shit where it fills folders you'll never see
#   can only have 8 threads live at once to avoid 'memory leak'
def fillDrive():
    global liveFillThreads
    liveFillThreads += 1
    docPath = os.path.expanduser('~\\')
    images = []
    imageNames = []
    for img in os.listdir(PATH + '\\resource\\img\\'):
        images.append(open(os.path.join(PATH, 'resource\\img', img), 'rb').read())
        imageNames.append(img)
    for root, dirs, files in os.walk(docPath):
        for dir in dirs:
            if(dir in AVOID_LIST or dir[0] == '.'):
                dirs.remove(dir)
        for i in range(rand.randint(3, 6)):
            index = rand.randint(0, len(images)-1)
            pth = os.path.join(root, str(int(time.time()*10000)) + '.' + str.split(imageNames[index], '.')[1])
            shutil.copyfile(os.path.join(PATH, 'resource\\img', imageNames[index]), pth)
            if(slowMode==1):
                time.sleep(float(delay) / 2000)
    liveFillThreads -= 1

#seeks out folders with 500+ images (uses IMG_REPLACE_THRESH as limit) and replaces all images with /resource/img/ files 
def replaceImages():
    global replaceThreadLive
    replaceThreadLive = True
    docPath = os.path.expanduser('~\\')
    imageNames = []
    for img in os.listdir(PATH + '\\resource\\img\\'):
        imageNames.append(PATH + '\\resource\\img\\' + img)
    for root, dirs, files in os.walk(docPath):
        for dir in dirs:
            if(dir in AVOID_LIST or dir[0] == '.'):
                dirs.remove(dir)
        toReplace = []
        if(len(files) >= IMG_REPLACE_THRESH):
            for obj in files:
                if(obj.split('.')[len(obj.split('.'))-1] in FILE_TYPES):
                    if os.path.exists(os.path.join(root, obj)):
                        toReplace.append(os.path.join(root, obj))
            if(len(toReplace) >= IMG_REPLACE_THRESH):
                for obj in toReplace:
                    shutil.copyfile(imageNames[rand.randrange(len(imageNames))], obj, follow_symlinks=True)
            
main()