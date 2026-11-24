[app]
title = 霓虹不夜城 Night Club Empire
package.name = nightclub
package.domain = com.nightclub

source.dir = .
source.include_exts = py,png,jpg,ttf,otf,ttc,md,txt
source.exclude_exts = spec
source.exclude_dirs = build,bin,.buildozer,__pycache__,.git,.github

version = 1.0.0.1

# 固定为本地已验证的版本，避免 p4a 默认拉取 Python 3.14 导致 pygame 编译失败
requirements = python3==3.11.9,pygame==2.6.1

orientation = landscape
fullscreen = 1

android.permissions =
android.api = 33
android.minapi = 21
android.ndk = 25b

[buildozer]
log_level = 2
warn_on_root = 1
