# 霓虹不夜城 Night Club Empire

2D 单机夜总会经营 SLG，Python + pygame 实现，纯代码绘制、无需外部素材。

## 运行

```powershell
cd 'D:\project\game_安卓库\night_club'
python -m pip install -r requirements.txt
python main.py
```

## 操作

- 顶栏查看现金、声望、清洁度、气氛、客流与今晚事件。
- 右侧标签页：总览 / 建造 / 员工 / 酒水 / 日志。
- 建造页：点击空地选择设施；点击已有设施升级；可拆除返还 40%。
- 营业中可暂停、切换 1x/2x/4x 倍速；`空格` 暂停，`H` 帮助。
- 目标：14 夜内现金 ≥ 38,000 且声望 ≥ 80。

详细设计见 `PRD.md`。

## 文案与字体兼容

源码与文档统一使用 UTF-8（无 BOM），Python 文件头部也显式声明了编码。游戏启动时会按 Android / Windows / macOS / Linux 直接加载常见中文字体文件（Noto Sans CJK、Droid Sans Fallback、微软雅黑、黑体、苹方、文泉驿等），并在必要时回退到系统字体名；这样可避开部分机器上 pygame 字体枚举异常导致的中文方框问题。若设备完全缺少中文字体，安装任意一款中文字体即可正常显示。

## 安卓构建

项目已包含 `buildozer.spec`，游戏内容、数值和文案与桌面端完全一致。桌面端行为不受影响。

在 Linux / WSL 环境中：

```bash
python -m pip install buildozer
buildozer android debug
```

生成的 APK 位于 `bin/` 目录。首次构建需要安装 JDK、Android SDK/NDK，耗时较长。`buildozer.spec` 已固定 `hostpython3==3.11.9`、`python3==3.11.9`、`cython==0.29.37` 与 `pygame==2.6.1`，解决 Python 版本不匹配及 pygame 在 p4a 隔离环境中缺少 Cython 的问题。

### 云端自动打包（推荐）

仓库已包含 `.github/workflows/build-android.yml`。将代码推送到 GitHub 的 `main` / `master` 分支，或推送 `v*` 标签，即可自动在云端构建 APK；也可以在 GitHub Actions 页面手动触发 `Build Android APK`。

构建完成后，在对应 Actions 运行的 Artifacts 中下载 `nightclub-v1.0.0.1-debug-apk`。首次构建较慢，后续运行会复用 Buildozer 与 Android SDK/NDK 缓存。

## 结构

```
main.py                入口与游戏循环
game/config.py         常量、数值配置
game/models.py         数据模型
game/simulation.py     经营模拟核心逻辑
game/renderer.py       2D 场景绘制
game/ui.py             按钮、面板、交互
game/android_compat.py 安卓显示缩放、触摸与生命周期适配
buildozer.spec         APK 打包配置
.github/workflows/build-android.yml  GitHub Actions 云端打包工作流
```
