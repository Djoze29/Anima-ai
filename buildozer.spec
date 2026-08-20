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

[buildozer]
log_level = 2
warn_on_root = 1
