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

# hostpython3/python3 版本必须一致。pygame 的 setup.py 由 p4a 隔离的 hostpython
# 执行，需要 hostpython 自身能 import Cython；用 p4a-recipes/cython 覆盖版把
# Cython 安装进 hostpython 的 site-packages（官方 recipe 只装到 Android 目标环境）。
requirements = hostpython3==3.11.9,python3==3.11.9,cython==0.29.37,pygame==2.6.1

orientation = landscape
fullscreen = 1

android.permissions =
android.api = 33
android.minapi = 21
android.ndk = 25b

[buildozer]
log_level = 2
warn_on_root = 1
