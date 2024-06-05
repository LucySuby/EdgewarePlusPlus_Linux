# Edgeware++ Pack Tool

This is a supplementary program to Edgeware++ to aide in creating packs.

To get started, install the dependencies from `requirements.txt` and create a
new pack template:

```
$ python3 -m pip install -r requirements.txt
$ python3 pack_tool.py -n my_pack
```

This will create a new directory `my_pack` for the source form of your pack.
The source form is structured as follows:

```
.
├── media
│   ├── default
│   │   ├── audio.mp3
│   │   ├── image.png
│   │   ├── video.mp4
│   │   └── ...
│   └── ...
│       ├── audio.mp3
│       ├── image.png
│       ├── video.mp4
│       └── ...
├── subliminals
│   ├── image.gif
│   └── ...
├── wallpapers
│   ├── wallpaper.png
│   └── ...
├── icon.ico
├── loading_splash.{png, gif, jpg, jpeg, bmp}
└── pack.yml
```

Here, you can add all of your pack's content and edit its `pack.yml` to add
info, captions, prompts, web URLs, and corruption levels. Once you're done, you
can compile your pack to the format understood by Edgeware:

```
$ python3 pack_tool.py my_pack
```

Afterwards, you will find your pack under the `build` directory, ready to be
used with Edgeware.

Optionally, you may also specify another output directory:

```
$ python3 pack_tool.py -o my_pack_build my_pack
```
