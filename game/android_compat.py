# -*- coding: utf-8 -*-
"""Android 平台适配层：显示缩放、触摸事件坐标与生命周期辅助。

桌面端保持原有窗口与输入行为；游戏内容、数值与文案不受影响。
"""
import os
import sys

import pygame as pg

from . import config as C

IS_ANDROID = sys.platform == "android" or bool(os.environ.get("ANDROID_ROOT"))
HIT_PAD = 10 if IS_ANDROID else 0


def _event(name):
    return getattr(pg, name, None)


APP_BACKGROUND = _event("APP_WILLENTERBACKGROUND")
APP_FOREGROUND = _event("APP_DIDENTERFOREGROUND")
FINGER_DOWN = _event("FINGERDOWN")
FINGER_MOTION = _event("FINGERMOTION")
FINGER_UP = _event("FINGERUP")
BACK_KEY = _event("K_AC_BACK")
TAP_SLOP = 12


def create_display():
    """返回 (物理屏幕, 绘制目标)。

    桌面端两者相同；安卓端绘制到固定的逻辑分辨率表面，再等比缩放呈现。
    """
    if not IS_ANDROID:
        screen = pg.display.set_mode((C.WINDOW_W, C.WINDOW_H))
        return screen, screen
    try:
        screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
    except Exception:
        screen = pg.display.set_mode((C.WINDOW_W, C.WINDOW_H), pg.FULLSCREEN)
    target = pg.Surface((C.WINDOW_W, C.WINDOW_H))
    return screen, target


def viewport(screen_size=None):
    """计算逻辑画面在物理屏幕上的缩放比例、偏移与目标尺寸。"""
    if screen_size is None:
        surface = pg.display.get_surface()
        screen_size = surface.get_size() if surface else (C.WINDOW_W, C.WINDOW_H)
    sw, sh = screen_size
    if sw <= 0 or sh <= 0:
        return 1.0, 0, 0, C.WINDOW_W, C.WINDOW_H
    scale = min(sw / C.WINDOW_W, sh / C.WINDOW_H)
    w = max(1, int(C.WINDOW_W * scale))
    h = max(1, int(C.WINDOW_H * scale))
    return scale, (sw - w) // 2, (sh - h) // 2, w, h


def to_logical(pos, screen_size=None):
    """把物理坐标转换为逻辑坐标；落在留边区域时返回 None。"""
    scale, ox, oy, _, _ = viewport(screen_size)
    x = (pos[0] - ox) / scale
    y = (pos[1] - oy) / scale
    if 0 <= x < C.WINDOW_W and 0 <= y < C.WINDOW_H:
        return (int(x), int(y))
    return None


def finger_screen_pos(event, screen_size=None):
    """兼容 FINGER 事件的归一化坐标(0..1)与像素坐标。"""
    if screen_size is None:
        surface = pg.display.get_surface()
        screen_size = surface.get_size() if surface else (C.WINDOW_W, C.WINDOW_H)
    sw, sh = screen_size
    x, y = float(event.x), float(event.y)
    if 0.0 <= x <= 1.0 and 0.0 <= y <= 1.0:
        return (x * sw, y * sh)
    return (x, y)


def is_tap(start_logical, end_logical):
    """判断手指抬起是否属于轻点而非拖动。"""
    if not start_logical or not end_logical:
        return False
    dx = end_logical[0] - start_logical[0]
    dy = end_logical[1] - start_logical[1]
    return dx * dx + dy * dy <= TAP_SLOP * TAP_SLOP


def present(screen, target):
    """安卓端把逻辑画面等比缩放居中显示；桌面端不处理。"""
    if not IS_ANDROID or screen is target:
        return
    sw, sh = screen.get_size()
    _, ox, oy, w, h = viewport((sw, sh))
    scaled = pg.transform.smoothscale(target, (w, h))
    screen.fill((0, 0, 0))
    screen.blit(scaled, (ox, oy))
    pg.display.flip()


def fps():
    return 45 if IS_ANDROID else C.FPS
