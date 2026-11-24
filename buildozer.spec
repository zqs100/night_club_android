[app]
title = 霓虹不夜城 Night Club Empire
package.name = nightclub
package.domain = com.nightclub

source.dir = .
source.include_exts = py,png,jpg,ttf,otf,ttc,md,txt
source.exclude_exts = spec
source.exclude_dirs = build,bin,.buildozer,__pycache__,.git,.github,p4a-recipes

version = 1.0.0.1

p4a.local_recipes = p4a-recipes

# hostpython3/python3 版本必须一致。pygame 2.6.1 的 setup.py 需要 Cython 3.x，
# 通过 p4a-recipes/pygame 覆盖版的 hostpython_prerequisites 让 hostpython 自身
# 安装 Cython；requirements 只放 Android 目标环境需要的包。
requirements = hostpython3==3.11.9,python3==3.11.9,pygame==2.6.1

orientation = landscape
fullscreen = 1

android.permissions =
android.api = 33
android.minapi = 21
android.ndk = 25b
# version=1.0.0.1 被 p4a 自动算成 10211000001，超过 Android versionCode 的
# 32 位有符号上限，AGP 8.11 解析为 null 导致 Gradle "Value is null"。显式指定。
android.numeric_version = 1

[buildozer]
log_level = 2
warn_on_root = 1
