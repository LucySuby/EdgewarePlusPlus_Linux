@echo off
:top
echo =====Welcome to the Edgeware CLI Pack Tool.=====
echo For information on how to use this, check out the README file in this directory.
echo What would you like to run?
echo 1: PackTool Setup (first time user? Start here!)
echo 2: Create New Pack
echo 3: Finish Pack (compile and build)
echo 4: Exit
set /p usrSelect=Select number:
if %usrSelect%==1 goto ptSetup
if %usrSelect%==2 goto ptCreate
if %usrSelect%==3 goto ptCompile
if %usrSelect%==4 goto ptQuit
echo Must enter selection number (1, 2, 3, 4)
pause
goto top
:ptSetup
echo Running install...
echo pip version:
py -m pip --version
if NOT %errorlevel%==0 goto installPip
goto requirements
:installPip
echo Could not find pip.
echo Installing pip with ensurepip...
py -m ensurepip --upgrade
py -m pip --version
if NOT %errorlevel%==0 goto ptQuit
goto requirements
:requirements
echo Installing requirements...
py -m pip install -r requirements.txt
echo Done.
echo You don't need to run this install on future launches, but if things stop working
echo in newer updates, it might help to use this again in case there are new dependencies.
pause
goto top
:ptCreate
echo What do you want to name your pack's directory? 
echo (use valid filename characters, with underscores instead of spaces!)
set /p packName=Directory Name:
pack_tool.py -n "%packName%"
echo Done.
pause
goto top
:ptCompile
echo What pack would you like to compile?
set /p compileName=Directory Name:
pack_tool.py "%compileName%"
echo Done.
pause
goto top
:ptQuit
echo Goodbye!
pause
