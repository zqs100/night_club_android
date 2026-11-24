[app]
title = 霓虹不夜城 Night Club Empire
package.name = nightclub
package.domain = com.nightclub

source.dir = .
source.include_exts = py,png,jpg,ttf,otf,ttc,md,txt
source.exclude_exts = spec
source.exclude_dirs = build,bin,.buildozer,__pycache__,.git,.github

version = 1.0.0.1

# 同时固定 hostpython3 与 python3，避免 p4a 默认使用 Python 3.14 造成版本不匹配
requirements = hostpython3==3.11.9,python3==3.11.9,pygame==2.6.1

orientation = landscape
fullscreen = 1

android.permissions =
android.api = 33
android.minapi = 21
android.ndk = 25b

[buildozer]
log_level = 2
warn_on_root = 1
