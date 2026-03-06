[app]

# (str) Title of your application
title = Arcade Game

# (str) Package name
package.name = arcadegame

# (str) Package domain (needed for android/ios packaging)
package.domain = org.test

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas

# (list) Source folders to include
source.include_dirs = player_frames,boss_frames

# (list) Source files to exclude
# source.exclude_exts =

# (list) List of directory to exclude
source.exclude_dirs = tests, bin, venv, .git, .github

# (list) List of exclusions using pattern matching
# source.exclude_patterns = license,images/*/*.jpg

# (str) Application versioning
version = 0.1

# (list) Application requirements
requirements = python3==3.10.12,kivy==2.3.0,pygame,sdl2_ttf,sdl2_image,sdl2_mixer

# (str) Custom source folders for requirements
# requirements.source.kivy = ../../kivy

# (str) Presplash of the application
# presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
# icon.filename = %(source.dir)s/data/icon.png

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = landscape

# (list) Permissions
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK / AAB will support.
android.minapi = 24

# (str) Android NDK architecture (e.g. armeabi-v7a, arm64-v8a)
android.archs = arm64-v8a, armeabi-v7a

# (bool) Auto-accept the SDK licensing
android.accept_sdk_license = True

# (bool) Indicate whether the application should be fullscreen or not
fullscreen = 1

# (str) Supported python version
p4a.branch = master

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1
