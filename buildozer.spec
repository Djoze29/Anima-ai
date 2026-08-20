[app]
title = Anima AI
package.name = animaai
package.domain = org.animaai

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json

version = 0.1.0

requirements = python3,kivy,plyer

orientation = portrait
fullscreen = 0

# Permissions Android nécessaires : capteur de luminosité, micro, vibration
android.permissions = VIBRATE,RECORD_AUDIO,POST_NOTIFICATIONS

android.api = 33
android.minapi = 24
android.ndk = 25b
android.accept_sdk_license = True

# Épingler python-for-android sur la release stable v2024.01.21 (Python 3.11).
# Sans cela, buildozer clone la branche 'master' (2026) qui cible Python 3.14
# et fait échouer le build (wheel cp314 non supporté).
p4a.branch = v2024.01.21

[buildozer]
log_level = 2
warn_on_root = 1
