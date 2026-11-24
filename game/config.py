# -*- coding: utf-8 -*-
"""全局常量与数值配置。数值集中于此，便于平衡性调整。"""

ROOT = None

WINDOW_W, WINDOW_H = 1280, 720
FPS = 60
FPS_ANDROID = 45

TILE = 64
GRID_W, GRID_H = 14, 9
MAP_X, MAP_Y = 16, 76
ENTRANCE = (0, 4)
SIDE_X = MAP_X + GRID_W * TILE + 16
SIDE_W = WINDOW_W - SIDE_X - 16
TOP_H = 64
BOTTOM_Y = MAP_Y + GRID_H * TILE + 12
BOTTOM_H = WINDOW_H - BOTTOM_Y - 12

# ---------- 颜色 ----------
BG = (18, 20, 30)
PANEL = (30, 34, 48)
PANEL_LIGHT = (40, 45, 62)
FLOOR_A = (44, 48, 64)
FLOOR_B = (39, 43, 58)
BORDER = (72, 78, 100)
TEXT = (232, 236, 246)
MUTED = (150, 158, 178)
ACCENT = (240, 184, 92)
GOOD = (110, 206, 160)
BAD = (232, 106, 112)
INFO = (126, 176, 232)
BUTTON = (62, 70, 96)
BUTTON_HOVER = (82, 92, 124)
DISABLED = (44, 48, 62)
SHADOW = (10, 12, 18)

# ---------- 规则 ----------
START_CASH = 12000.0
START_REP = 30.0
TOTAL_DAYS = 14
TARGET_CASH = 38000.0
TARGET_REP = 80.0
BANKRUPT_CASH = -3000.0
OPEN_HOUR = 20
CLOSE_HOUR = 26           # 次日 02:00
SECONDS_PER_HOUR = 12.0   # 一整夜约 72 秒
COVER_BASE = 20.0
MAX_LEVEL = 3

# ---------- 冒泡评价 ----------
BUBBLE_DURATION = 2.0            # 单个气泡显示秒数（真实时间）
BUBBLE_GAP_MIN = 3.0             # 全局最短间隔
BUBBLE_GAP_MAX = 6.0             # 全局最长间隔
BUBBLE_ENTITY_COOLDOWN = 10.0    # 同一角色再次冒泡的冷却
GUEST_BUBBLE_CHANCE = 0.32       # 客人每次消费事件触发概率
STAFF_BUBBLE_CHANCE = 0.30       # 员工每次服务事件触发概率

# ---------- 设施 ----------
FACILITIES = {
    "bar":      {"name": "吧台",     "short": "BAR",   "cost": 2500, "upkeep": 120, "color": (196, 132, 74),  "desc": "客人点单处；调酒师越多出杯越快"},
    "dance":    {"name": "舞池",     "short": "DANCE", "cost": 1800, "upkeep": 90,  "color": (112, 86, 180),  "desc": "提升气氛与满意度，每处容量 4 人"},
    "seat":     {"name": "卡座",     "short": "SEAT",  "cost": 900,  "upkeep": 40,  "color": (92, 150, 132),  "desc": "客人小憩并加购，客单价提升"},
    "vip":      {"name": "VIP包厢",  "short": "VIP",   "cost": 6000, "upkeep": 300, "color": (198, 154, 84),  "desc": "声望 ≥ 55 解锁，贵宾高消费"},
    "stage":    {"name": "舞台音响", "short": "DJ",    "cost": 4200, "upkeep": 200, "color": (176, 80, 110),  "desc": "提升音乐评分，吸引客流"},
    "light":    {"name": "灯光装置", "short": "LIGHT", "cost": 1500, "upkeep": 60,  "color": (86, 142, 196),  "desc": "提升气氛与打卡传播"},
    "restroom": {"name": "洗手间",   "short": "WC",    "cost": 1200, "upkeep": 50,  "color": (120, 132, 150), "desc": "减缓清洁度下降"},
}
FACILITY_ORDER = ["bar", "dance", "seat", "vip", "stage", "light", "restroom"]

# ---------- 员工 ----------
STAFF = {
    "bartender": {"name": "调酒师", "short": "酒", "salary": 260, "hire": 400, "color": (214, 158, 92),  "desc": "每名减少约 35% 出杯等待"},
    "security":  {"name": "保安",   "short": "保", "salary": 220, "hire": 300, "color": (110, 148, 202), "desc": "处置闹事者，避免声望损失"},
    "dj":        {"name": "DJ",     "short": "DJ", "salary": 420, "hire": 600, "color": (198, 104, 152), "desc": "音乐评分 +20 / 人"},
    "cleaner":   {"name": "保洁",   "short": "洁", "salary": 180, "hire": 200, "color": (118, 194, 166), "desc": "持续恢复清洁度"},
}
STAFF_ORDER = ["bartender", "security", "dj", "cleaner"]

# ---------- 酒水 ----------
DRINKS = {
    "beer":      {"name": "精酿啤酒",   "cost": 18,  "price": 38,  "demand": 3, "color": (224, 176, 84)},
    "cocktail":  {"name": "招牌鸡尾酒", "cost": 42,  "price": 98,  "demand": 2, "color": (222, 118, 158)},
    "champagne": {"name": "香槟",       "cost": 150, "price": 380, "demand": 1, "color": (222, 214, 140)},
}
DRINK_ORDER = ["beer", "cocktail", "champagne"]
START_STOCK = {"beer": 60, "cocktail": 40, "champagne": 10}

# ---------- 客群 ----------
GUEST_KINDS = {
    "normal":   {"name": "散客",   "color": (228, 230, 238), "budget": (120, 300),   "patience": (18, 30), "weight": 60},
    "regular":  {"name": "熟客",   "color": (120, 205, 190), "budget": (220, 520),   "patience": (24, 40), "weight": 22},
    "vip":      {"name": "贵宾",   "color": (244, 196, 96),  "budget": (900, 2200),  "patience": (30, 50), "weight": 8},
    "trouble":  {"name": "闹事者", "color": (226, 92, 98),   "budget": (0, 40),      "patience": (10, 18), "weight": 10},
}

# ---------- 事件 ----------
EVENTS = [
    {"id": "normal",          "name": "平常夜",       "desc": "没有特殊情况，稳扎稳打。",                     "arrival": 1.00, "vip": 0,  "trouble": 0,  "music": 1.0, "cost": 1.0, "rep": 0,  "weight": 20},
    {"id": "celebrity",       "name": "明星到访",     "desc": "社交热议，贵宾与打卡客激增。",               "arrival": 1.25, "vip": 14, "trouble": 0,  "music": 1.0, "cost": 1.0, "rep": 4,  "weight": 10},
    {"id": "inspection",      "name": "卫生突击检查", "desc": "打烊时清洁度低于 60 将被罚款 1,500 元。",     "arrival": 1.00, "vip": 0,  "trouble": 0,  "music": 1.0, "cost": 1.0, "rep": 0,  "weight": 10},
    {"id": "rival",           "name": "隔壁新店开业", "desc": "竞争激烈，今晚客流下降 25%。",               "arrival": 0.75, "vip": 0,  "trouble": 0,  "music": 1.0, "cost": 1.0, "rep": 0,  "weight": 10},
    {"id": "broken_speaker",  "name": "音响故障",     "desc": "音乐评分减半，打烊支付 800 元维修费。",       "arrival": 1.00, "vip": 0,  "trouble": 0,  "music": 0.5, "cost": 1.0, "rep": 0,  "weight": 9},
    {"id": "drunk_wave",      "name": "醉酒潮",       "desc": "闹事者大幅增加，务必配置保安。",             "arrival": 1.10, "vip": 0,  "trouble": 18, "music": 1.0, "cost": 1.0, "rep": 0,  "weight": 10},
    {"id": "supplier_sale",   "name": "供应商促销",   "desc": "今晚酒水采购成本降低 30%。",                 "arrival": 1.00, "vip": 0,  "trouble": 0,  "music": 1.0, "cost": 0.7, "rep": 0,  "weight": 9},
    {"id": "noise_complaint", "name": "噪音投诉预警", "desc": "打烊时气氛高于 65 将被罚款 900 元。",         "arrival": 1.00, "vip": 0,  "trouble": 0,  "music": 1.0, "cost": 1.0, "rep": 0,  "weight": 9},
    {"id": "viral",           "name": "短视频打卡",   "desc": "客流 +30%，口碑传播更快。",                  "arrival": 1.30, "vip": 0,  "trouble": 0,  "music": 1.0, "cost": 1.0, "rep": 3,  "weight": 9},
]
