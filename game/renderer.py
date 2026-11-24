# -*- coding: utf-8 -*-
"""2D 俯视场景与顶栏绘制。"""
import os

import pygame as pg

from . import config as C

_FONT_CACHE = {}
_FONT_FILE_CACHE = {}

# 直接指定系统中文字体文件，避免部分平台 pygame 字体枚举异常导致中文变方框
_ANDROID_FONT_DIR = "/system/fonts"
_WIN_FONT_DIR = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts")
_ANDROID_FONT_FILES = (
    os.path.join(_ANDROID_FONT_DIR, "NotoSansCJK-Regular.ttc"),
    os.path.join(_ANDROID_FONT_DIR, "NotoSansCJKsc-Regular.otf"),
    os.path.join(_ANDROID_FONT_DIR, "NotoSansSC-Regular.otf"),
    os.path.join(_ANDROID_FONT_DIR, "DroidSansFallback.ttf"),
)
_WINDOWS_FONT_FILES = (
    os.path.join(_WIN_FONT_DIR, "msyh.ttc"),
    os.path.join(_WIN_FONT_DIR, "msyhbd.ttc"),
    os.path.join(_WIN_FONT_DIR, "simhei.ttf"),
    os.path.join(_WIN_FONT_DIR, "simsun.ttc"),
)
_OTHER_FONT_FILES = (
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/STHeiti Light.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/Library/Fonts/Arial Unicode.ttf",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJKsc-Regular.otf",
    "/usr/share/fonts/opentype/source-han-sans/SourceHanSansSC-Regular.otf",
    "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
    "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
    "/usr/share/fonts/truetype/arphic/uming.ttc",
)
_CJK_FONT_FILES = _ANDROID_FONT_FILES + _WINDOWS_FONT_FILES + _OTHER_FONT_FILES

# SysFont 名称仅作为直接文件路径不可用时的兜底
_CJK_FONT_NAMES = (
    "notosanssc", "notosanscjksc", "droidsansfallback",
    "microsoftyahei", "simhei", "simsun",
    "pingfangsc", "heiti", "stheitisc",
    "notosanscjk", "sourcehansanssc",
    "wenquanyimicrohei", "wenquanyizenhei",
)


def _find_font_file(bold: bool):
    key = bool(bold)
    if key in _FONT_FILE_CACHE:
        return _FONT_FILE_CACHE[key]
    files = _CJK_FONT_FILES
    if key:
        files = tuple(os.path.join(_WIN_FONT_DIR, name) for name in
                      ("msyhbd.ttc", "simhei.ttf", "msyh.ttc", "simsun.ttc")) + _CJK_FONT_FILES
    found = None
    for path in files:
        try:
            if path and os.path.isfile(path):
                found = path
                break
        except Exception:
            continue
    _FONT_FILE_CACHE[key] = found
    return found


def font(size: int, bold: bool = False):
    if not pg.font.get_init():
        pg.font.init()
    key = (size, bold)
    if key not in _FONT_CACHE:
        chosen = None
        path = _find_font_file(bold)
        if path:
            try:
                chosen = pg.font.Font(path, size)
                if bold:
                    chosen.set_bold(True)
            except Exception:
                chosen = None
        if chosen is None:
            for name in _CJK_FONT_NAMES:
                try:
                    candidate = pg.font.SysFont(name, size, bold=bold)
                    if candidate and candidate.get_height() > 0:
                        chosen = candidate
                        break
                except Exception:
                    continue
        _FONT_CACHE[key] = chosen or pg.font.Font(None, size)
    return _FONT_CACHE[key]


def lighten(color, amount=30):
    return tuple(min(255, c + amount) for c in color)


_NEON = {
    "pink": (236, 72, 153),
    "cyan": (80, 220, 230),
    "purple": (150, 96, 220),
    "gold": (240, 184, 92),
    "dark": (16, 18, 28),
    "outline": (8, 10, 16),
    "skin": (232, 190, 160),
}
_BAR = {
    "wood_dark": (58, 38, 28),
    "wood": (92, 58, 38),
    "wood_light": (132, 88, 54),
    "iron": (48, 52, 60),
    "copper": (190, 118, 66),
    "glow": (255, 196, 96),
}
_DANCE = {
    "wood": (96, 64, 42),
    "wood_light": (136, 96, 60),
    "wood_dark": (62, 42, 30),
    "stone": (58, 62, 68),
    "iron": (52, 56, 64),
    "amber": (240, 168, 80),
}
_SEAT = {
    "leather": (132, 48, 48),
    "leather_dark": (92, 34, 34),
    "leather_light": (168, 68, 64),
    "wood": (86, 58, 40),
    "wood_light": (124, 88, 58),
    "iron": (52, 56, 62),
    "amber": (248, 186, 84),
}
_VIP = {
    "leather": (140, 44, 48),
    "leather_dark": (96, 30, 34),
    "leather_light": (176, 68, 70),
    "wood": (78, 56, 40),
    "wood_light": (116, 84, 58),
    "stone": (92, 96, 104),
    "rug": (126, 36, 42),
    "rug_gold": (206, 158, 86),
    "curtain": (132, 36, 44),
    "amber": (250, 190, 90),
}
_STAGE = {
    "wood": (86, 58, 40),
    "wood_light": (126, 90, 58),
    "stone": (80, 84, 90),
    "metal": (48, 52, 58),
    "speaker": (42, 40, 44),
    "curtain": (78, 40, 36),
    "amber": (248, 184, 84),
}
_LIGHT = {
    "wood": (78, 56, 40),
    "wood_light": (116, 84, 58),
    "metal": (48, 52, 58),
    "amber": (248, 184, 84),
    "blue": (96, 176, 232),
    "red": (224, 72, 80),
}
_RESTROOM = {
    "stone": (78, 84, 92),
    "stone_light": (110, 116, 124),
    "wood": (76, 54, 38),
    "wood_light": (112, 82, 54),
    "amber": (248, 190, 88),
    "red": (236, 72, 96),
    "blue": (72, 176, 232),
    "mirror": (150, 180, 190),
}
_SPRITE_CACHE = {}
_FLOOR_SURFACE = None


def _surf(w, h):
    return pg.Surface((w, h), pg.SRCALPHA)


def _box(s, color, x, y, w, h):
    pg.draw.rect(s, color, (x, y, w, h))


def _label(s, content, cx, cy, size=9, color=None):
    img = font(size, True).render(content, True, color or C.TEXT)
    s.blit(img, img.get_rect(center=(cx, cy)))


def _shine(s, x, y, color=None):
    c = color or _NEON["gold"]
    _box(s, c, x - 1, y, 3, 1)
    _box(s, c, x, y - 1, 1, 3)


def _draw_bubble(s, entity, x, y, now):
    if not entity.bubble_text or now >= entity.bubble_until:
        return
    f = font(10, True)
    tw, _ = f.size(entity.bubble_text)
    w, h = tw + 14, 20
    bx = int(max(C.MAP_X + 2,
                 min(x - w // 2, C.MAP_X + C.GRID_W * C.TILE - w - 2)))
    by = int(max(C.MAP_Y + 2, y - 34 - h))
    color = {"good": C.GOOD, "bad": C.BAD}.get(entity.bubble_tone, C.MUTED)
    pg.draw.rect(s, (14, 17, 26), (bx, by, w, h), border_radius=5)
    pg.draw.rect(s, color, (bx, by, w, h), 1, border_radius=5)
    pg.draw.polygon(s, (14, 17, 26),
                    [(bx + w // 2 - 4, by + h), (bx + w // 2 + 4, by + h),
                     (bx + w // 2, by + h + 5)])
    pg.draw.line(s, color, (bx + w // 2 - 4, by + h), (bx + w // 2, by + h + 5))
    pg.draw.line(s, color, (bx + w // 2 + 4, by + h), (bx + w // 2, by + h + 5))
    img = f.render(entity.bubble_text, True, C.TEXT)
    s.blit(img, img.get_rect(center=(bx + w // 2, by + h // 2)))


def _facility_sprite(kind, base, level=1):
    level = max(1, min(3, int(level)))
    key = ("facility", kind, level)
    if key in _SPRITE_CACHE:
        return _SPRITE_CACHE[key]
    s = _surf(56, 56)
    if level == 1:
        frame = (58, 62, 74)
        trim = tuple(max(0, c - 30) for c in base)
    elif level == 2:
        frame = _NEON["dark"]
        trim = base
    else:
        frame = _NEON["dark"]
        trim = _NEON["gold"]
    _box(s, _NEON["outline"], 2, 2, 52, 52)
    _box(s, frame, 4, 4, 48, 48)
    _box(s, trim, 4, 4, 48, 2)
    _box(s, trim, 4, 50, 48, 2)
    if level >= 3:
        for px, py in ((6, 6), (48, 6), (6, 48), (48, 48)):
            _shine(s, px, py)

    if kind == "bar":
        wood_dark = _BAR["wood_dark"] if level >= 2 else (46, 32, 24)
        wood = _BAR["wood"] if level >= 2 else (72, 48, 34)
        wood_light = _BAR["wood_light"] if level >= 2 else (96, 64, 46)

        _box(s, wood_dark, 8, 8, 40, 20)
        _box(s, wood, 8, 8, 40, 3)
        _box(s, wood, 8, 24, 40, 3)
        _box(s, _NEON["outline"], 8, 15, 40, 1)
        if level >= 2:
            _box(s, _BAR["glow"], 9, 17, 38, 1)
        if level >= 3:
            for dx in (21, 34):
                _box(s, wood, dx, 11, 1, 13)

        bottle_cols = (_NEON["pink"], _NEON["cyan"], _NEON["gold"],
                       (220, 220, 240), (120, 220, 180), (180, 110, 70),
                       (200, 200, 210))
        bottle_count = 2 if level == 1 else (5 if level == 2 else 7)
        for i in range(bottle_count):
            bx = 11 + i * 5
            _box(s, bottle_cols[i % len(bottle_cols)], bx, 19, 3, 5)
            _box(s, (230, 230, 240), bx + 1, 20, 1, 2)
        if level >= 2:
            for i in range(4):
                _box(s, (160, 168, 180), 12 + i * 6, 26, 3, 2)

        _box(s, wood_dark, 6, 22, 6, 22)
        _box(s, wood_dark, 44, 22, 6, 22)
        _box(s, wood_light, 6, 22, 6, 2)
        _box(s, wood_light, 44, 22, 6, 2)
        _box(s, wood_light, 6, 34, 44, 2)
        _box(s, wood, 6, 36, 44, 5)
        _box(s, _BAR["iron"], 6, 41, 44, 3)
        if level >= 3:
            _box(s, _NEON["gold"], 6, 41, 44, 1)
        if level >= 2:
            _box(s, _BAR["copper"] if level >= 3 else _BAR["iron"], 8, 46, 40, 1)
            for tx in (38, 43):
                _box(s, _BAR["copper"], tx, 29, 2, 7)
                _box(s, _BAR["iron"], tx - 1, 28, 4, 1)

        stools = (16, 36) if level == 1 else (12, 22, 32, 42)
        for sx in stools:
            pg.draw.circle(s, _NEON["outline"], (sx, 50), 4)
            pg.draw.circle(s, wood_light, (sx, 50), 3)
            if level >= 3:
                _box(s, _NEON["gold"], sx - 1, 49, 2, 1)

        if level == 1:
            _box(s, wood, 21, 6, 14, 7)
            _label(s, "BAR", 28, 9, 7, (34, 26, 20))
        else:
            _box(s, _NEON["dark"], 18, 4, 20, 10)
            _box(s, trim, 18, 4, 20, 1)
            _label(s, "BAR", 28, 9, 9, _NEON["pink"] if level == 2 else _NEON["gold"])
            _box(s, _NEON["cyan"], 19, 13, 18, 1)
        if level >= 3:
            _shine(s, 10, 12, _BAR["glow"])
            _shine(s, 46, 12, _BAR["glow"])
            _shine(s, 28, 22, _NEON["gold"])
    elif kind == "dance":
        outer = [(18, 12), (38, 12), (48, 22), (48, 40),
                 (38, 50), (18, 50), (8, 40), (8, 22)]
        inner = [(19, 15), (37, 15), (45, 23), (45, 39),
                 (37, 47), (19, 47), (11, 39), (11, 23)]
        wood = _DANCE["wood"] if level >= 2 else (70, 50, 38)
        wood_light = _DANCE["wood_light"] if level >= 2 else (96, 70, 52)
        wood_dark = _DANCE["wood_dark"] if level >= 2 else (48, 34, 26)
        edge = (_NEON["gold"] if level >= 3
                else (_DANCE["iron"] if level >= 2 else (54, 58, 64)))

        if level >= 2:
            _box(s, (96, 58, 48), 18, 8, 20, 9)
            for dx in (21, 27, 33):
                _box(s, (140, 96, 70), dx, 10, 1, 5)

        pg.draw.polygon(s, edge, outer)
        pg.draw.polygon(s, wood, inner)
        for py in (21, 29, 37, 44):
            _box(s, wood_dark, 13, py, 30, 1)

        cx, cy = 28, 31
        radius = 11 if level >= 2 else 8
        pg.draw.circle(s, wood_dark, (cx, cy), radius, 1)
        pg.draw.circle(s, edge, (cx, cy), radius - 4, 1)
        if level >= 2:
            pg.draw.line(s, edge, (cx - 9, cy), (cx + 9, cy))
            pg.draw.line(s, edge, (cx, cy - 9), (cx, cy + 9))
            pg.draw.polygon(s, edge,
                            [(cx, cy - 6), (cx + 6, cy), (cx, cy + 6), (cx - 6, cy)], 1)
        else:
            _box(s, edge, cx - 1, cy - 1, 2, 2)

        if level >= 2:
            _box(s, _DANCE["amber"], 13, 19, 30, 1)
            _box(s, _DANCE["amber"], 13, 43, 30, 1)
            _box(s, _DANCE["amber"], 11, 24, 1, 14)
            _box(s, _DANCE["amber"], 44, 24, 1, 14)

            spots = ((14, 9), (22, 9), (30, 9), (38, 9)) if level == 2 else \
                    ((12, 9), (19, 9), (28, 9), (37, 9), (44, 9))
            beam = _surf(56, 56)
            for i, (sx, sy) in enumerate(spots):
                col = (_NEON["cyan"], _NEON["pink"], _DANCE["amber"])[i % 3]
                alpha = 30 if level == 2 else 42
                pg.draw.polygon(beam, (*col, alpha),
                                [(sx, sy + 2), (sx - 6, 44), (sx + 6, 44)])
            s.blit(beam, (0, 0))

            for bx in (6, 42):
                _box(s, _NEON["outline"], bx, 20, 8, 14)
                _box(s, (60, 52, 50), bx + 1, 21, 6, 12)
                pg.draw.circle(s, (20, 20, 24), (bx + 4, 25), 2)
                pg.draw.circle(s, _DANCE["amber"] if level >= 3 else
                               (110, 100, 90), (bx + 4, 31), 1)
                if level >= 3:
                    _box(s, _NEON["gold"], bx, 20, 8, 1)

        _box(s, wood_light, 22, 48, 12, 3)
        _box(s, _DANCE["stone"], 20, 51, 16, 2)
        if level >= 3:
            _box(s, _NEON["gold"], 22, 48, 12, 1)

        if level == 1:
            _box(s, wood, 22, 7, 12, 5)
            _box(s, _DANCE["amber"], 27, 8, 2, 2)
        else:
            _box(s, _DANCE["iron"], 8, 5, 40, 2)
            if level >= 3:
                _box(s, _NEON["gold"], 8, 5, 40, 1)
            for sx in ((14, 22, 30, 38) if level == 2 else
                       (12, 19, 28, 37, 44)):
                pg.draw.circle(s, _DANCE["amber"], (sx, 8), 1)
            _box(s, _NEON["dark"], 16, 6, 24, 8)
            sign_color = _NEON["gold"] if level >= 3 else _NEON["pink"]
            _box(s, sign_color, 16, 6, 24, 1)
            _label(s, "DANCE", 28, 10, 7, sign_color)
        if level >= 3:
            _shine(s, 12, 16, _DANCE["amber"])
            _shine(s, 44, 16, _DANCE["amber"])
            _shine(s, 28, 18, _NEON["gold"])
    elif kind == "seat":
        leather = _SEAT["leather"] if level >= 2 else (96, 44, 42)
        leather_dark = _SEAT["leather_dark"] if level >= 2 else (68, 32, 32)
        leather_light = _SEAT["leather_light"] if level >= 2 else (116, 56, 54)
        wood = _SEAT["wood"] if level >= 2 else (70, 50, 38)
        wood_light = _SEAT["wood_light"] if level >= 2 else (96, 70, 50)
        edge = (_NEON["gold"] if level >= 3
                else (_SEAT["iron"] if level >= 2 else (60, 64, 70)))

        if level == 1:
            _box(s, wood, 8, 16, 40, 6)
            _box(s, leather, 10, 18, 36, 8)
            _box(s, leather_dark, 10, 26, 36, 12)
            _box(s, wood, 8, 38, 40, 4)
            _box(s, edge, 8, 16, 40, 1)
            _box(s, wood_light, 22, 30, 12, 10)
        else:
            _box(s, wood, 6, 10, 44, 6)
            _box(s, wood, 6, 14, 6, 34)
            _box(s, wood, 44, 14, 6, 34)
            _box(s, edge, 6, 10, 44, 2)
            _box(s, edge, 6, 10, 2, 38)
            _box(s, edge, 48, 10, 2, 38)

            _box(s, leather, 10, 14, 36, 12)
            _box(s, leather_dark, 12, 26, 32, 16)
            _box(s, leather, 8, 22, 8, 22)
            _box(s, leather, 40, 22, 8, 22)
            _box(s, leather_light, 11, 16, 34, 2)
            _box(s, leather_light, 9, 24, 3, 18)
            _box(s, leather_light, 44, 24, 3, 18)

            for bx, by in ((6, 16), (44, 16), (6, 44), (44, 44)):
                _box(s, _SEAT["iron"], bx, by, 5, 2)
                _box(s, _SEAT["iron"], bx, by, 2, 5)

            if level >= 3:
                for px, py in ((12, 18), (38, 18), (10, 34), (42, 34)):
                    _box(s, leather_light, px, py, 6, 5)
                    _box(s, leather_dark, px, py + 4, 6, 1)

            _box(s, wood_light, 20, 28, 16, 14)
            _box(s, wood, 20, 30, 16, 11)
            for bx, by in ((20, 28), (33, 28), (20, 39), (33, 39)):
                _box(s, _SEAT["iron"], bx, by, 3, 3)
            pg.draw.circle(s, (180, 110, 66), (25, 33), 2)
            pg.draw.circle(s, (176, 182, 190), (32, 36), 2)
            if level >= 3:
                pg.draw.circle(s, (230, 220, 190), (30, 31), 2)

        if level == 1:
            _box(s, wood, 22, 8, 12, 5)
        else:
            _box(s, _NEON["dark"], 16, 4, 24, 8)
            sign_color = _NEON["gold"] if level >= 3 else _NEON["pink"]
            _box(s, sign_color, 16, 4, 24, 1)
            _label(s, "RELAX", 28, 8, 7, sign_color)
            _box(s, _SEAT["amber"], 16, 12, 24, 1)
            if level >= 3:
                pg.draw.polygon(s, _NEON["gold"],
                                [(28, 13), (31, 14), (31, 17), (28, 19),
                                 (25, 17), (25, 14)])
                _shine(s, 10, 12, _SEAT["amber"])
                _shine(s, 46, 12, _SEAT["amber"])
                _shine(s, 28, 22, _NEON["gold"])
    elif kind == "vip":
        leather = _VIP["leather"] if level >= 2 else (94, 40, 42)
        leather_dark = _VIP["leather_dark"] if level >= 2 else (66, 30, 32)
        leather_light = _VIP["leather_light"] if level >= 2 else (116, 54, 56)
        wood = _VIP["wood"] if level >= 2 else (66, 48, 36)
        wood_light = _VIP["wood_light"] if level >= 2 else (94, 70, 50)
        edge = (_NEON["gold"] if level >= 3
                else (_VIP["stone"] if level >= 2 else (58, 60, 66)))

        _box(s, _NEON["outline"], 5, 7, 46, 42)
        _box(s, wood, 6, 8, 44, 40)
        _box(s, wood_light, 6, 8, 44, 2)
        _box(s, edge, 6, 8, 44, 1)
        if level >= 3:
            _box(s, _NEON["gold"], 5, 7, 46, 1)
            _box(s, _NEON["gold"], 5, 48, 46, 1)

        _box(s, (48, 36, 28) if level >= 2 else (56, 42, 32), 9, 11, 38, 34)

        if level == 1:
            _box(s, leather, 11, 14, 26, 10)
            _box(s, leather_dark, 11, 24, 10, 18)
            _box(s, wood_light, 22, 26, 14, 10)
            _box(s, wood, 42, 14, 7, 28)
        else:
            _box(s, leather, 10, 12, 28, 12)
            _box(s, leather_dark, 10, 22, 10, 22)
            _box(s, leather_light, 11, 13, 26, 2)
            _box(s, leather_light, 11, 24, 2, 18)
            for sx in (18, 26, 34):
                _box(s, leather_dark, sx, 16, 1, 7)
            for sy in (29, 36):
                _box(s, leather_dark, 15, sy, 4, 1)

            _box(s, _VIP["rug"], 20, 24, 20, 18)
            _box(s, _VIP["rug_gold"], 20, 24, 20, 1)
            _box(s, _VIP["rug_gold"], 20, 41, 20, 1)
            _box(s, _VIP["rug_gold"], 20, 24, 1, 18)
            _box(s, _VIP["rug_gold"], 39, 24, 1, 18)
            for ry in (29, 35):
                _box(s, _VIP["rug_gold"], 23, ry, 14, 1)
                _box(s, _VIP["rug_gold"], 27, ry - 2, 6, 1)

            _box(s, wood_light, 23, 28, 14, 10)
            _box(s, wood, 23, 30, 14, 7)
            _box(s, (40, 62, 48), 29, 29, 3, 6)
            _box(s, _VIP["rug_gold"], 30, 28, 1, 1)
            pg.draw.circle(s, (182, 112, 68), (26, 35), 2)
            pg.draw.circle(s, (176, 182, 190), (34, 35), 2)
            if level >= 3:
                _box(s, (40, 62, 48), 25, 30, 2, 5)
                pg.draw.circle(s, (230, 220, 190), (32, 31), 2)

            _box(s, _VIP["stone"], 41, 14, 9, 28)
            _box(s, _VIP["stone"], 40, 12, 11, 5)
            _box(s, _VIP["curtain"], 40, 14, 3, 28)
            _box(s, _VIP["curtain"], 49, 14, 3, 28)
            _box(s, _NEON["outline"], 43, 17, 5, 23)
            _box(s, wood, 44, 19, 3, 19)
            _box(s, _VIP["amber"], 43, 16, 5, 1)
            _box(s, _VIP["amber"], 43, 40, 5, 1)
            pg.draw.circle(s, _VIP["rug_gold"], (46, 29), 1)
            _box(s, _VIP["stone"], 42, 45, 9, 2)
            if level >= 3:
                _box(s, _NEON["gold"], 41, 14, 1, 28)
                _box(s, _NEON["gold"], 49, 14, 1, 28)
                _shine(s, 12, 12, _VIP["amber"])
                _shine(s, 38, 12, _VIP["amber"])
                _shine(s, 28, 22, _NEON["gold"])

        if level == 1:
            _box(s, wood, 39, 7, 12, 6)
            _label(s, "VIP", 45, 10, 7, (40, 32, 24))
        else:
            _box(s, _NEON["dark"], 38, 5, 14, 8)
            sign_color = _NEON["gold"] if level >= 3 else _NEON["pink"]
            _box(s, sign_color, 38, 5, 14, 1)
            _label(s, "VIP", 45, 9, 8, sign_color)
            if level >= 3:
                _box(s, _NEON["cyan"], 39, 12, 12, 1)
    elif kind == "stage":
        wood = _STAGE["wood"] if level >= 2 else (68, 48, 36)
        wood_light = _STAGE["wood_light"] if level >= 2 else (96, 72, 50)
        edge = (_NEON["gold"] if level >= 3
                else (_STAGE["metal"] if level >= 2 else (56, 58, 64)))

        _box(s, _STAGE["stone"], 6, 42, 44, 6)
        _box(s, wood, 8, 28, 40, 14)
        _box(s, wood_light, 8, 28, 40, 2)
        _box(s, edge, 8, 28, 40, 1)

        if level == 1:
            _box(s, (52, 46, 50), 10, 24, 7, 16)
            _box(s, wood_light, 21, 30, 14, 9)
            pg.draw.circle(s, _NEON["outline"], (25, 34), 3)
            pg.draw.circle(s, (110, 116, 130), (25, 34), 1)
        else:
            _box(s, _STAGE["curtain"], 12, 10, 32, 12)
            _box(s, wood_light, 12, 10, 32, 2)
            for dx in (17, 24, 31, 38):
                _box(s, (110, 58, 48), dx, 13, 2, 8)

            _box(s, wood_light, 20, 30, 16, 10)
            _box(s, wood, 20, 32, 16, 7)
            for cx in (24, 32):
                pg.draw.circle(s, _NEON["outline"], (cx, 34), 3)
                pg.draw.circle(s, _NEON["cyan"], (cx, 34), 1)
            _box(s, _STAGE["metal"], 28, 31, 2, 6)
            for dy in (32, 34, 36):
                _box(s, _NEON["pink"], 28, dy, 2, 1)

            for bx in (8, 41):
                _box(s, _NEON["outline"], bx, 22, 7, 20)
                _box(s, _STAGE["speaker"], bx + 1, 23, 5, 18)
                pg.draw.circle(s, (20, 20, 24), (bx + 3, 28), 2)
                pg.draw.circle(s, (20, 20, 24), (bx + 3, 36), 2)
                pg.draw.circle(s, _NEON["cyan"] if level == 2 else _NEON["gold"],
                               (bx + 3, 28), 1)
                if level >= 3:
                    _box(s, _NEON["gold"], bx, 22, 7, 1)

        _box(s, wood_light, 22, 45, 12, 3)
        _box(s, _STAGE["stone"], 20, 48, 16, 2)
        if level >= 3:
            _box(s, _NEON["gold"], 22, 45, 12, 1)

        if level == 1:
            _box(s, wood, 22, 8, 12, 5)
        else:
            _box(s, _STAGE["metal"], 7, 5, 42, 2)
            if level >= 3:
                _box(s, _NEON["gold"], 7, 5, 42, 1)
            spots = (12, 18, 24, 30, 36, 42) if level == 2 else \
                    (9, 14, 19, 24, 29, 34, 39, 44)
            for sx in spots:
                _box(s, _STAGE["metal"], sx - 1, 7, 2, 3)
                pg.draw.circle(s, _STAGE["amber"], (sx, 11), 1)
            _box(s, _NEON["dark"], 13, 5, 30, 11)
            sign_color = _NEON["pink"] if level == 2 else _NEON["gold"]
            _box(s, sign_color, 13, 5, 30, 1)
            _label(s, "DJ", 28, 9, 9, sign_color)
            _label(s, "STAGE", 28, 14, 6, _NEON["cyan"] if level == 2 else sign_color)
            _box(s, _STAGE["amber"], 14, 17, 28, 1)
        if level >= 3:
            _shine(s, 9, 8, _STAGE["amber"])
            _shine(s, 47, 8, _STAGE["amber"])
            _shine(s, 28, 19, _NEON["gold"])
    elif kind == "light":
        wood = _LIGHT["wood"] if level >= 2 else (66, 56, 48)
        wood_light = _LIGHT["wood_light"] if level >= 2 else (94, 72, 52)
        edge = (_NEON["gold"] if level >= 3
                else (_LIGHT["metal"] if level >= 2 else (58, 60, 66)))

        if level == 1:
            _box(s, wood, 10, 16, 36, 3)
            _box(s, _LIGHT["metal"], 26, 19, 4, 5)
            pg.draw.circle(s, (120, 124, 136), (28, 25), 3)
        else:
            _box(s, wood, 6, 8, 44, 4)
            _box(s, wood, 6, 10, 4, 40)
            _box(s, wood, 46, 10, 4, 40)
            _box(s, wood_light, 6, 8, 44, 1)
            _box(s, edge, 6, 8, 44, 1)

            _box(s, _LIGHT["metal"], 10, 14, 36, 4)
            for tx in range(10, 46, 6):
                pg.draw.line(s, wood_light, (tx, 14), (tx + 6, 18))
                pg.draw.line(s, wood_light, (tx + 6, 14), (tx, 18))

            lamps = (14, 22, 30, 38) if level == 2 else (11, 17, 23, 29, 35, 41, 47)
            beam = _surf(56, 56)
            for i, lx in enumerate(lamps):
                col = _LIGHT["amber"] if i % 2 == 0 else _LIGHT["blue"]
                _box(s, _LIGHT["metal"], lx - 1, 18, 2, 4)
                pg.draw.circle(s, col, (lx, 23), 2)
                alpha = 30 if level == 2 else 40
                pg.draw.polygon(beam, (*col, alpha),
                                [(lx, 24), (lx - 6, 48), (lx + 6, 48)])
            s.blit(beam, (0, 0))

            for i in range(8):
                col = _LIGHT["red"] if i % 2 == 0 else _LIGHT["blue"]
                _box(s, col, 10 + i * 5, 12, 3, 1)
            for ly in (20, 28, 36):
                _box(s, _LIGHT["red"], 6, ly, 2, 4)
                _box(s, _LIGHT["blue"], 48, ly, 2, 4)

            _box(s, _NEON["outline"], 39, 38, 11, 12)
            _box(s, wood, 40, 39, 9, 10)
            for ky in (41, 44):
                _box(s, _LIGHT["metal"], 42, ky, 1, 1)
                _box(s, _LIGHT["amber"], 45, ky, 1, 1)
                _box(s, _LIGHT["blue"], 47, ky, 1, 1)

            _box(s, wood_light, 10, 48, 36, 2)
            _box(s, _LIGHT["amber"], 14, 48, 10, 1)
            _box(s, _LIGHT["blue"], 32, 48, 10, 1)
            if level >= 3:
                _box(s, _NEON["gold"], 6, 8, 44, 1)
                _box(s, _NEON["gold"], 6, 8, 1, 42)
                _box(s, _NEON["gold"], 49, 8, 1, 42)

        if level >= 2:
            _box(s, _NEON["dark"], 34, 4, 20, 8)
            sign_color = _NEON["gold"] if level >= 3 else _NEON["cyan"]
            _box(s, sign_color, 34, 4, 20, 1)
            _label(s, "LIGHTS", 44, 8, 7, sign_color)
        if level >= 3:
            _shine(s, 8, 10, _LIGHT["amber"])
            _shine(s, 48, 10, _LIGHT["blue"])
            _shine(s, 28, 26, _NEON["gold"])
    elif kind == "restroom":
        stone = _RESTROOM["stone"] if level >= 2 else (64, 68, 74)
        stone_light = _RESTROOM["stone_light"] if level >= 2 else (86, 92, 100)
        wood = _RESTROOM["wood"] if level >= 2 else (64, 48, 36)
        wood_light = _RESTROOM["wood_light"] if level >= 2 else (90, 68, 48)
        edge = (_NEON["gold"] if level >= 3
                else (stone_light if level >= 2 else (58, 62, 68)))

        _box(s, _NEON["outline"], 5, 5, 46, 46)
        _box(s, stone, 6, 6, 44, 44)
        _box(s, stone_light, 9, 9, 38, 38)
        for fy in (16, 24, 32, 40):
            _box(s, stone, 10, fy, 36, 1)
        for fx in (16, 24, 32, 40):
            _box(s, stone, fx, 10, 1, 36)
        if level >= 3:
            _box(s, _NEON["gold"], 5, 5, 46, 1)
            _box(s, _NEON["gold"], 5, 50, 46, 1)
            _box(s, _NEON["gold"], 5, 5, 1, 46)
            _box(s, _NEON["gold"], 50, 5, 1, 46)

        if level == 1:
            _box(s, wood, 18, 18, 20, 24)
            _box(s, wood_light, 20, 20, 16, 20)
            _box(s, stone_light, 24, 12, 8, 5)
            _label(s, "WC", 28, 14, 8, (180, 186, 200))
            _box(s, stone_light, 34, 28, 3, 3)
        else:
            for sx in (13, 31):
                _box(s, _RESTROOM["mirror"], sx + 2, 9, 8, 6)
                _box(s, wood, sx, 15, 12, 6)
                _box(s, stone_light, sx + 2, 16, 8, 4)
                pg.draw.circle(s, stone, (sx + 6, 17), 2)
                _box(s, _RESTROOM["amber"], sx + 5, 13, 2, 1)

            _box(s, wood, 38, 24, 10, 20)
            for sy in (24, 34):
                _box(s, wood_light, 38, sy, 10, 2)
                _box(s, _NEON["outline"], 43, sy + 5, 3, 5)
                pg.draw.circle(s, _RESTROOM["amber"], (45, sy + 8), 1)
            _box(s, stone, 38, 44, 10, 2)

            _box(s, wood, 6, 26, 9, 16)
            _box(s, wood_light, 8, 28, 5, 12)
            _box(s, _NEON["outline"], 11, 34, 2, 2)

            for lx, ly in ((11, 12), (45, 12), (11, 44), (45, 44)):
                pg.draw.circle(s, _RESTROOM["amber"], (lx, ly), 1)
            if level >= 3:
                _box(s, _NEON["gold"], 38, 24, 1, 20)
                _box(s, _NEON["gold"], 38, 24, 10, 1)
                for sx in (13, 31):
                    _box(s, (230, 240, 245), sx + 3, 10, 2, 4)

            _box(s, _NEON["dark"], 18, 5, 20, 9)
            _box(s, edge, 18, 5, 20, 1)
            f = font(10, True)
            s.blit(f.render("W", True, _RESTROOM["red"]), (22, 6))
            s.blit(f.render("C", True, _RESTROOM["blue"]), (31, 6))
            if level >= 3:
                _shine(s, 20, 14, _RESTROOM["amber"])
                _shine(s, 36, 14, _RESTROOM["amber"])
    _SPRITE_CACHE[key] = s
    return s


def _person_sprite(group, kind, base):
    key = (group, kind)
    if key in _SPRITE_CACHE:
        return _SPRITE_CACHE[key]
    s = _surf(20, 30)
    _box(s, (6, 8, 14, 120), 4, 26, 12, 2)
    _box(s, _NEON["outline"], 5, 24, 4, 5)
    _box(s, _NEON["outline"], 11, 24, 4, 5)
    _box(s, _NEON["outline"], 4, 11, 12, 14)
    _box(s, base, 5, 12, 10, 12)
    _box(s, _NEON["outline"], 5, 3, 10, 9)
    _box(s, _NEON["skin"], 6, 4, 8, 7)
    _box(s, _NEON["outline"], 6, 3, 8, 2)
    if group == "staff":
        if kind == "bartender":
            _box(s, _NEON["pink"], 8, 14, 4, 2)
            _box(s, _NEON["cyan"], 15, 15, 3, 8)
        elif kind == "security":
            _box(s, (30, 38, 58), 5, 12, 10, 12)
            _box(s, _NEON["gold"], 12, 16, 3, 3)
            _box(s, _NEON["cyan"], 13, 6, 2, 2)
        elif kind == "dj":
            _box(s, (92, 52, 120), 5, 12, 10, 12)
            _box(s, _NEON["outline"], 4, 4, 12, 2)
            _box(s, _NEON["pink"], 4, 4, 2, 5)
            _box(s, _NEON["pink"], 14, 4, 2, 5)
        elif kind == "cleaner":
            _box(s, _NEON["cyan"], 5, 2, 10, 2)
            _box(s, (120, 130, 150), 16, 8, 2, 16)
            _box(s, _NEON["gold"], 14, 23, 6, 2)
    else:
        if kind == "normal":
            _box(s, _NEON["cyan"], 6, 18, 8, 2)
        elif kind == "regular":
            _box(s, (30, 70, 70), 5, 12, 10, 12)
            _box(s, _NEON["cyan"], 6, 8, 8, 1)
        elif kind == "vip":
            _box(s, (96, 58, 120), 5, 12, 10, 12)
            _box(s, _NEON["gold"], 7, 16, 6, 2)
            _box(s, _NEON["outline"], 6, 7, 8, 2)
            _box(s, _NEON["gold"], 8, 7, 4, 1)
        elif kind == "trouble":
            _box(s, (150, 40, 48), 5, 12, 10, 12)
            _box(s, (150, 40, 48), 5, 3, 10, 4)
            _box(s, _NEON["outline"], 7, 7, 2, 1)
            _box(s, _NEON["outline"], 11, 7, 2, 1)
    scaled = pg.transform.scale(s, (24, 36))
    _SPRITE_CACHE[key] = scaled
    return scaled


def _build_floor():
    global _FLOOR_SURFACE
    if _FLOOR_SURFACE is not None:
        return _FLOOR_SURFACE
    w, h = C.GRID_W * C.TILE, C.GRID_H * C.TILE
    s = _surf(w, h)
    for gy in range(C.GRID_H):
        for gx in range(C.GRID_W):
            x, y = gx * C.TILE, gy * C.TILE
            _box(s, C.FLOOR_A if (gx + gy) % 2 == 0 else C.FLOOR_B, x, y, C.TILE, C.TILE)
            _box(s, (52, 57, 74), x, y, C.TILE, 1)
            _box(s, (52, 57, 74), x, y, 1, C.TILE)
            if (gx * 7 + gy * 13) % 5 == 0:
                _box(s, (72, 82, 112), x + 14, y + 22, 3, 3)
    glow = _surf(w, h)
    pg.draw.circle(glow, (*_NEON["purple"], 26), (int(w * 0.56), int(h * 0.5)), 190)
    pg.draw.circle(glow, (*_NEON["cyan"], 18), (int(w * 0.56), int(h * 0.5)), 120)
    s.blit(glow, (0, 0))
    ex, ey = C.ENTRANCE[0] * C.TILE, C.ENTRANCE[1] * C.TILE
    _box(s, _NEON["dark"], ex + 4, ey + 4, C.TILE - 8, C.TILE - 8)
    _box(s, _NEON["cyan"], ex + 4, ey + 4, C.TILE - 8, 2)
    _box(s, _NEON["pink"], ex + 4, ey + C.TILE - 6, C.TILE - 8, 2)
    label = font(12, True).render("入口", True, C.TEXT)
    s.blit(label, label.get_rect(center=(ex + C.TILE / 2, ey + C.TILE / 2)))
    _box(s, _NEON["pink"], 0, 0, w, 2)
    _box(s, _NEON["cyan"], 0, h - 2, w, 2)
    _FLOOR_SURFACE = s
    return s


class Renderer:
    def __init__(self, screen):
        self.screen = screen

    def draw(self, sim, ui):
        s = self.screen
        s.fill(C.BG)
        self.draw_top(sim)
        self.draw_map(sim, ui)
        ui.draw(s, sim)
        display = pg.display.get_surface()
        if display is not None and display is s:
            pg.display.flip()

    def draw_top(self, sim):
        s = self.screen
        pg.draw.rect(s, (24, 27, 38), (0, 0, C.WINDOW_W, C.TOP_H))
        pg.draw.line(s, C.BORDER, (0, C.TOP_H - 1), (C.WINDOW_W, C.TOP_H - 1))

        s.blit(font(18, True).render("霓虹不夜城", True, C.ACCENT), (14, 8))
        s.blit(font(10).render("NIGHT CLUB EMPIRE", True, C.MUTED), (15, 34))

        items = [
            ("营业日", f"{sim.day} / {C.TOTAL_DAYS}", C.TEXT),
            ("时间", f"{sim.fmt_hour(sim.clock)}", C.TEXT),
            ("现金", f"{sim.cash:,.0f}", C.GOOD if sim.cash >= 0 else C.BAD),
            ("声望", f"{sim.reputation:.0f} / 100", C.ACCENT),
            ("清洁度", f"{sim.cleanliness:.0f}", C.GOOD if sim.cleanliness >= 60 else C.BAD),
            ("气氛", f"{sim.hype:.0f}", C.INFO),
            ("在场客人", f"{len(sim.guests)}", C.TEXT),
            ("今晚事件", sim.event["name"], C.ACCENT),
        ]
        x = 168
        width = 137
        for label, value, color in items:
            s.blit(font(11).render(label, True, C.MUTED), (x, 9))
            s.blit(font(14, True).render(value, True, color), (x, 28))
            x += width

    def draw_map(self, sim, ui):
        s = self.screen
        s.blit(_build_floor(), (C.MAP_X, C.MAP_Y))

        for pos, facility in sim.facilities.items():
            data = C.FACILITIES[facility.kind]
            gx, gy = pos
            sx = C.MAP_X + gx * C.TILE + 3
            sy = C.MAP_Y + gy * C.TILE + 3
            s.blit(_facility_sprite(facility.kind, data["color"], facility.level), (sx, sy))
            for i in range(facility.level):
                pg.draw.circle(s, C.ACCENT, (sx + 8 + i * 8, sy + 54), 3)

        if ui.hover_tile and ui.tab == "build":
            hx, hy = ui.hover_tile
            rect = pg.Rect(C.MAP_X + hx * C.TILE, C.MAP_Y + hy * C.TILE, C.TILE, C.TILE)
            color = C.GOOD if hx != C.ENTRANCE[0] or hy != C.ENTRANCE[1] else C.BAD
            pg.draw.rect(s, color, rect, 2)
        if ui.selected_tile:
            sx, sy = ui.selected_tile
            rect = pg.Rect(C.MAP_X + sx * C.TILE + 1, C.MAP_Y + sy * C.TILE + 1,
                           C.TILE - 2, C.TILE - 2)
            pg.draw.rect(s, C.ACCENT, rect, 2)

        now = pg.time.get_ticks()
        for member in sim.staff:
            x, y = int(member.x), int(member.y)
            spr = _person_sprite("staff", member.kind, C.STAFF[member.kind]["color"])
            bob = (now // 320 + member.uid) % 2
            s.blit(spr, (x - spr.get_width() // 2, y - spr.get_height() + 6 - bob))
        for guest in sim.guests:
            x, y = int(guest.x), int(guest.y)
            spr = _person_sprite("guest", guest.kind, C.GUEST_KINDS[guest.kind]["color"])
            bob = (now // 260 + guest.uid) % 2
            s.blit(spr, (x - spr.get_width() // 2, y - spr.get_height() + 6 - bob))
            if guest.satisfaction < 45:
                pg.draw.circle(s, C.BAD, (x, y - 4), 11, 1)

        for member in sim.staff:
            _draw_bubble(s, member, int(member.x), int(member.y), sim.real_time)
        for guest in sim.guests:
            _draw_bubble(s, guest, int(guest.x), int(guest.y), sim.real_time)

        if sim.phase == "ready" or sim.paused:
            overlay = pg.Surface((C.GRID_W * C.TILE, C.GRID_H * C.TILE), pg.SRCALPHA)
            overlay.fill((8, 10, 18, 105))
            s.blit(overlay, (C.MAP_X, C.MAP_Y))
            text = "准备阶段：采购 / 调价 / 装修 / 排班" if sim.phase == "ready" else "已暂停"
            label = font(22, True).render(text, True, C.ACCENT)
            s.blit(label, label.get_rect(center=(C.MAP_X + C.GRID_W * C.TILE / 2,
                                                 C.MAP_Y + C.GRID_H * C.TILE / 2)))
