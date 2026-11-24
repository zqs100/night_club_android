import os
import shutil

from pythonforandroid.recipe import CompiledComponentsPythonRecipe


class CythonRecipe(CompiledComponentsPythonRecipe):
    version = "0.29.37"
    url = "https://github.com/cython/cython/archive/{version}.tar.gz"
    site_packages_name = "cython"
    depends = ["setuptools"]
    call_hostpython_via_targetpython = False
    install_in_hostpython = True

    def build_arch(self, arch):
        super().build_arch(arch)

        # p4a develop 的 CompiledComponentsPythonRecipe.build_arch 只把 Cython
        # 装进 Android 目标环境，从不调用 install_hostpython_package，导致
        # pygame 的 setup.py 由隔离 hostpython 执行时报 "You need cython"。
        try:
            self.install_hostpython_package(arch)
            return
        except Exception:
            pass

        # 兜底：Cython 是纯 Python 包，把源码里的 Cython/ 与 cython.py 直接
        # 复制进 hostpython 的 site-packages，效果与 pip 安装一致。
        site_dir = self._host_recipe.site_dir
        build_dir = self.get_build_dir(arch.arch)
        os.makedirs(site_dir, exist_ok=True)
        for name in ("Cython", "cython.py"):
            src = os.path.join(build_dir, name)
            dst = os.path.join(site_dir, name)
            if not os.path.exists(src):
                continue
            if os.path.isdir(src):
                if os.path.isdir(dst):
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)


recipe = CythonRecipe()
