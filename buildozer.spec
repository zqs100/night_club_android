[app]
title = 霓虹不夜城 Night Club Empire
package.name = nightclub
package.domain = com.nightclub

source.dir = .
source.include_exts = py,png,jpg,ttf,otf,ttc,md,txt
source.exclude_exts = spec
source.exclude_dirs = build,bin,.buildozer,__pycache__,.git,.github

version = 1.0.0.1

# hostpython3/python3 版本必须一致。pygame 编译所需的 Cython 由云端工作流通过
# PYTHONPATH 提供给 p4a 的隔离 hostpython，不在此处重复安装到 Android 目标环境。
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
