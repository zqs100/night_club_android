[app]
title = 霓虹不夜城 Night Club Empire
package.name = nightclub
package.domain = com.nightclub

source.dir = .
source.include_exts = py,png,jpg,ttf,otf,ttc,md,txt
source.exclude_exts = spec
source.exclude_dirs = build,bin,.buildozer,__pycache__,.git,.github

version = 1.0.0.1

# python-for-android 的 pygame recipe 版本由构建环境决定；游戏内不依赖特定小版本
requirements = python3,pygame

orientation = landscape
fullscreen = 1

android.permissions =
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b

[buildozer]
log_level = 2
warn_on_root = 1
