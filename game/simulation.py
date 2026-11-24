# -*- coding: utf-8 -*-
"""经营模拟核心：客流、员工、设施、经济、事件与结算。"""
import math
import random

from . import config as C
from .models import Facility, Guest, Ledger, Staff


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


GUEST_BUBBLES = {
    "good": ["这杯太顶了！", "气氛正好，再来一杯。", "服务很到位，值这个价。",
             "今晚来对了。", "这气氛绝了！", "调酒师手真快。"],
    "neutral": ["还行吧，凑合。", "价格有点高。", "人有点多。",
                "再坐一会儿吧。", "一般般，不算惊艳。"],
    "bad": ["等太久了！", "这酒兑水了吧…", "地板黏脚，扣分。",
            "音响吵得头疼。", "不值这个价。", "服务跟不上啊。"],
}

STAFF_BUBBLES = {
    "good": ["这桌客人真爽快。", "今晚手感不错。", "吧台节奏刚刚好。",
             "小费收到，谢啦！", "今天状态在线。"],
    "neutral": ["按顺序来，别急。", "这单马上好。", "场面还能hold住。",
                "再撑一会儿就打烊了。"],
    "bad": ["又催单，忙不过来了。", "这地也太脏了吧…", "音响再响就听不见点了。",
            "客人怎么越来越多。", "得叫保洁来看看。"],
}


class Simulation:
    def __init__(self):
        self.reset()

    # ---------------------------------------------------------------- 初始化
    def reset(self):
        self.day = 1
        self.clock = float(C.OPEN_HOUR)
        self.phase = "ready"          # ready / open / settlement / gameover
        self.paused = False
        self.speed = 1
        self.real_time = 0.0
        self._next_bubble_at = 0.0
        self.cash = C.START_CASH
        self.reputation = C.START_REP
        self.cleanliness = 85.0
        self.hype = 40.0
        self.stock = dict(C.START_STOCK)
        self.prices = {k: v["price"] for k, v in C.DRINKS.items()}
        self.staff = []
        self.facilities = {}
        self.guests = []
        self.ledger = Ledger()
        self.log = []
        self.event = self.pick_event()
        self.settlement = None
        self.result = None            # win / lose
        self.result_reason = ""
        self._uid = 1
        self._arrival_acc = 0.0
        self._last_hour = C.OPEN_HOUR
        self._rep_start = self.reputation
        self._served = 0
        self._visitors = 0
        self.init_layout()
        self.add_log("接手一家亏损夜店，14 夜内扭亏为盈。", "info")
        self.add_log(f"今晚事件：{self.event['name']} — {self.event['desc']}", "event")

    def init_layout(self):
        self.facilities[(3, 1)] = Facility("bar")
        self.facilities[(7, 4)] = Facility("dance")
        self.facilities[(4, 7)] = Facility("seat")
        self.facilities[(10, 1)] = Facility("stage")
        self.hire("bartender", free=True)
        self.hire("dj", free=True)

    # ---------------------------------------------------------------- 工具
    @staticmethod
    def tile_center(gx: int, gy: int):
        return (C.MAP_X + gx * C.TILE + C.TILE / 2,
                C.MAP_Y + gy * C.TILE + C.TILE / 2)

    def world_to_tile(self, px: float, py: float):
        gx = int((px - C.MAP_X) // C.TILE)
        gy = int((py - C.MAP_Y) // C.TILE)
        if 0 <= gx < C.GRID_W and 0 <= gy < C.GRID_H:
            return (gx, gy)
        return None

    def _bubble_ready(self, entity, chance: float) -> bool:
        if self.real_time < self._next_bubble_at:
            return False
        if self.real_time - entity.last_bubble_at < C.BUBBLE_ENTITY_COOLDOWN:
            return False
        return random.random() < chance

    def _say(self, entity, text: str, tone: str):
        entity.bubble_text = text
        entity.bubble_tone = tone
        entity.bubble_until = self.real_time + C.BUBBLE_DURATION
        entity.last_bubble_at = self.real_time
        self._next_bubble_at = self.real_time + random.uniform(
            C.BUBBLE_GAP_MIN, C.BUBBLE_GAP_MAX)

    @staticmethod
    def _tone_for(score: float) -> str:
        if score >= 72:
            return "good"
        if score <= 48:
            return "bad"
        return "neutral"

    def staff_mood(self) -> float:
        busy = sum(1 for s in self.staff if s.busy > 0)
        load = busy / max(1, len(self.staff))
        score = (50 + (self.cleanliness - 70) * 0.35
                 + (self.hype - 50) * 0.2
                 + min(12, self.cash / 1500) - load * 12)
        return clamp(score, 0, 100)

    def maybe_guest_bubble(self, g: Guest, facility_score: float):
        if not self._bubble_ready(g, C.GUEST_BUBBLE_CHANCE):
            return
        score = g.satisfaction * 0.6 + clamp(facility_score, 0, 100) * 0.4
        tone = self._tone_for(score)
        self._say(g, random.choice(GUEST_BUBBLES[tone]), tone)

    def maybe_staff_bubble(self, staff: Staff, service_score: float):
        if not self._bubble_ready(staff, C.STAFF_BUBBLE_CHANCE):
            return
        score = self.staff_mood() * 0.6 + clamp(service_score, 0, 100) * 0.4
        tone = self._tone_for(score)
        self._say(staff, random.choice(STAFF_BUBBLES[tone]), tone)

    @staticmethod
    def fmt_hour(hour: float) -> str:
        return f"{int(hour) % 24:02d}:00"

    def add_log(self, text: str, kind: str = "info"):
        self.log.insert(0, f"[D{self.day} {self.fmt_hour(self.clock)}] {text}")
        self.log = self.log[:80]

    def count_facility(self, kind: str) -> int:
        return sum(1 for f in self.facilities.values() if f.kind == kind)

    def total_level(self, kind: str) -> int:
        return sum(f.level for f in self.facilities.values() if f.kind == kind)

    def count_staff(self, kind: str) -> int:
        return sum(1 for s in self.staff if s.kind == kind)

    def venue_entries(self):
        return [(pos, f.kind) for pos, f in self.facilities.items()
                if f.kind in ("bar", "dance", "seat", "vip")]

    def music_score(self) -> float:
        score = (20 + self.count_staff("dj") * 20
                 + self.total_level("stage") * 12
                 + self.total_level("light") * 4)
        return clamp(score * self.event["music"], 0, 100)

    def pick_event(self) -> dict:
        weights = [e["weight"] for e in C.EVENTS]
        return random.choices(C.EVENTS, weights=weights, k=1)[0]

    # ---------------------------------------------------------------- 营业流程
    def start_night(self):
        if self.phase != "ready":
            return
        self.phase = "open"
        self.paused = False
        self.clock = float(C.OPEN_HOUR)
        self._arrival_acc = 0.0
        self._last_hour = C.OPEN_HOUR
        self._rep_start = self.reputation
        self._served = 0
        self._visitors = 0
        self.add_log(f"开始营业，今晚事件：{self.event['name']}。", "event")

    def set_speed(self, value: int):
        self.speed = value
        self.paused = False

    def toggle_pause(self):
        if self.phase == "open":
            self.paused = not self.paused

    def update(self, dt: float):
        self.real_time += dt
        for entity in list(self.staff) + list(self.guests):
            if entity.bubble_until and self.real_time >= entity.bubble_until:
                entity.bubble_text = ""
                entity.bubble_tone = ""
                entity.bubble_until = 0.0
        if self.phase != "open" or self.paused:
            return
        dt *= self.speed
        self.clock += dt / C.SECONDS_PER_HOUR
        if self.clock >= C.CLOSE_HOUR:
            self.clock = float(C.CLOSE_HOUR)
            self.close_night()
            return
        hour = int(self.clock)
        if hour != self._last_hour:
            self._last_hour = hour
            self.add_log(f"进入 {self.fmt_hour(hour)} 时段。", "time")

        target = self.hourly_target(hour)
        self._arrival_acc += dt * target / C.SECONDS_PER_HOUR
        while self._arrival_acc >= 1.0:
            self._arrival_acc -= 1.0
            self.spawn_guest()

        self.update_guests(dt)
        self.update_staff(dt)
        self.update_ambience(dt)

    def hourly_target(self, hour: int) -> int:
        peak = {20: 0.55, 21: 0.95, 22: 1.0, 23: 0.85, 0: 0.55, 1: 0.30}
        curve = peak.get(hour % 24, 0.4)
        rep_factor = 0.55 + self.reputation / 100
        music = 0.6 + self.music_score() / 100 * 0.6
        price_index = sum(self.prices[k] / C.DRINKS[k]["price"] for k in C.DRINKS) / 3
        price_factor = clamp(1.25 - price_index * 0.28, 0.5, 1.35)
        base = 7 + self.reputation * 0.16
        return max(1, int(base * curve * rep_factor * music * price_factor * self.event["arrival"]))

    def roll_guest_kind(self) -> str:
        weights = []
        for kind, data in C.GUEST_KINDS.items():
            w = data["weight"]
            if kind == "vip":
                if self.reputation < 55 or self.count_facility("vip") == 0:
                    w = 0
                else:
                    w += self.event["vip"]
            if kind == "trouble":
                w += self.event["trouble"]
            weights.append(w)
        return random.choices(list(C.GUEST_KINDS), weights=weights, k=1)[0]

    def pick_intent(self, kind: str) -> str:
        if kind == "trouble":
            return "trouble"
        entries = self.venue_entries()
        if not entries:
            return "wander"
        kinds = [k for _, k in entries]
        weights = []
        base = {"bar": 35, "dance": 30, "seat": 22, "vip": 12}
        for k in kinds:
            w = base.get(k, 1)
            if k == "vip":
                w = w * 4 if kind == "vip" else w * 0.15
            if k == "bar" and kind == "vip":
                w *= 0.5
            weights.append(w)
        return random.choices(kinds, weights=weights, k=1)[0]

    def pick_destination(self, intent: str):
        if intent == "trouble":
            intent = random.choice(["dance", "seat", "bar"])
        tiles = [pos for pos, f in self.facilities.items() if f.kind == intent]
        if not tiles:
            tiles = [(C.GRID_W // 2, C.GRID_H // 2)]
        gx, gy = random.choice(tiles)
        return self.tile_center(gx, gy)

    def spawn_guest(self):
        kind = self.roll_guest_kind()
        data = C.GUEST_KINDS[kind]
        ex, ey = self.tile_center(*C.ENTRANCE)
        price_index = sum(self.prices[k] / C.DRINKS[k]["price"] for k in C.DRINKS) / 3
        start_sat = (72 + (self.music_score() - 50) / 12
                     + (self.cleanliness - 70) / 12 - (price_index - 1) * 12)
        g = Guest(
            uid=self._uid, kind=kind, x=ex, y=ey, tx=ex, ty=ey, intent="",
            budget=random.uniform(*data["budget"]),
            satisfaction=clamp(start_sat, 25, 95),
        )
        self._uid += 1
        g.intent = self.pick_intent(kind)
        g.tx, g.ty = self.pick_destination(g.intent)
        self.guests.append(g)
        self._visitors += 1
        if kind not in ("vip", "trouble"):
            cover = C.COVER_BASE + self.reputation * 0.12
            self.cash += cover
            self.ledger.cover += cover

    # ---------------------------------------------------------------- 客人行为
    def move_toward(self, g: Guest, dt: float):
        dx, dy = g.tx - g.x, g.ty - g.y
        dist = math.hypot(dx, dy)
        if dist <= 4:
            g.x, g.y = g.tx, g.ty
            self.arrive(g)
        else:
            step = min(dist, 58 * dt)
            g.x += dx / dist * step
            g.y += dy / dist * step

    def arrive(self, g: Guest):
        if g.intent == "exit":
            self.finish_guest(g)
        elif g.intent == "bar":
            if not any(self.stock.values()):
                g.satisfaction -= 12
                self.add_log("酒水售罄，有客人失望离开。", "bad")
                self.send_home(g)
            else:
                g.state = "queue"
                g.timer = 0.0
        elif g.intent in ("dance", "seat", "vip"):
            if g.intent == "dance":
                dancing = sum(1 for other in self.guests
                              if other.state == "dance" and other.intent == "dance")
                capacity = 4 * max(1, self.count_facility("dance"))
                if dancing >= capacity:
                    g.state = "sit"
                    g.timer = 3.0
                    g.satisfaction -= 5
                    self.maybe_guest_bubble(g, 40)
                else:
                    g.state = "dance"
                    g.timer = random.uniform(5, 9)
            else:
                g.state = "sit"
                g.timer = random.uniform(7, 11)
                self.table_order(g)
        elif g.intent == "trouble":
            g.state = "trouble"
            g.timer = 9.0
        else:
            g.state = "sit"
            g.timer = 4.0
            g.satisfaction -= 4

    def update_guests(self, dt: float):
        for g in list(self.guests):
            if self.cleanliness < 65:
                g.satisfaction -= dt * (65 - self.cleanliness) / 65 * 1.5
            if g.state == "walk":
                self.move_toward(g, dt)
            elif g.state == "queue":
                g.timer += dt
                free = [s for s in self.staff if s.kind == "bartender" and s.busy <= 0]
                if free and any(self.stock.values()):
                    if g.timer > C.GUEST_KINDS[g.kind]["patience"][0]:
                        g.satisfaction -= 22
                        self.send_home(g)
                    else:
                        self.serve(g, free[0])
                else:
                    if g.timer > C.GUEST_KINDS[g.kind]["patience"][1] * 1.6:
                        g.satisfaction -= 18
                        self.send_home(g)
            elif g.state == "drink":
                g.timer -= dt
                if g.timer <= 0:
                    self.next_stop(g)
            elif g.state == "dance":
                g.timer -= dt
                self.hype += dt * (0.55 + self.total_level("stage") * 0.25)
                g.satisfaction += dt * 0.5
                if g.timer <= 0:
                    self.next_stop(g)
            elif g.state == "sit":
                g.timer -= dt
                g.satisfaction += dt * 0.3
                if g.timer <= 0:
                    self.next_stop(g)
            elif g.state == "trouble":
                g.timer -= dt
                guards = self.count_staff("security")
                chance = min(0.9, 0.22 + 0.18 * (guards - 1)) if guards else 0
                if guards and random.random() < chance * dt:
                    guard = random.choice([s for s in self.staff if s.kind == "security"])
                    self.guests.remove(g)
                    self.reputation = clamp(self.reputation + 1.2, 0, 100)
                    self.add_log("保安请走一名闹事者，声望 +1。", "good")
                    self.maybe_staff_bubble(guard, 85)
                    continue
                if g.timer <= 0:
                    self.cash -= 320
                    self.ledger.fines += 320
                    self.reputation = clamp(self.reputation - 5, 0, 100)
                    self.cleanliness = clamp(self.cleanliness - 8, 0, 100)
                    self.add_log("闹事者打翻酒瓶：损失 320 元，声望 -5。", "bad")
                    self.send_home(g)

    def choose_drink(self, g: Guest):
        available = [k for k in C.DRINK_ORDER if self.stock[k] > 0]
        if not available:
            return None
        weights = []
        for k in available:
            price = self.prices[k]
            if price > g.budget - g.spent:
                w = 0.2
            else:
                w = float(C.DRINKS[k]["demand"])
                if k == "champagne":
                    w *= 4 if g.kind == "vip" else 0.35
                if g.kind == "regular" and k == "cocktail":
                    w *= 1.8
                if price < C.DRINKS[k]["cost"] * 1.5:
                    w *= 1.5
            weights.append(w)
        if sum(weights) <= 0:
            return None
        return random.choices(available, weights=weights, k=1)[0]

    def price_bonus(self, drink: str) -> float:
        ratio = self.prices[drink] / C.DRINKS[drink]["price"]
        if ratio > 1.4:
            return -7.0
        if ratio < 0.85:
            return 3.0
        return 0.0

    def serve(self, g: Guest, staff: Staff):
        drink = self.choose_drink(g)
        if not drink:
            g.satisfaction -= 12
            self.maybe_guest_bubble(g, 20)
            self.send_home(g)
            return
        wait = g.timer
        self.stock[drink] -= 1
        price = self.prices[drink]
        self.cash += price
        self.ledger.sales += price
        g.spent += price
        self._served += 1
        serve_time = max(2.0, 5.0 - self.count_staff("bartender") * 1.1)
        staff.busy = serve_time
        g.state = "drink"
        g.timer = serve_time
        g.drink = drink
        bonus = 3 + self.price_bonus(drink)
        g.satisfaction += bonus
        tipped = False
        if g.kind in ("regular", "vip") and random.random() < 0.55:
            tip = price * 0.12
            self.cash += tip
            self.ledger.tips += tip
            tipped = True
        wait_penalty = max(0.0, wait - C.GUEST_KINDS[g.kind]["patience"][0] * 0.6) * 2
        facility_score = clamp(65 + bonus * 8 - wait_penalty, 0, 100)
        self.maybe_guest_bubble(g, facility_score)
        service = (55 + (18 if tipped else 0) + self.price_bonus(drink) * 3
                   + (10 if g.satisfaction >= 75 else -10)
                   - (8 if serve_time > 3.0 else 0))
        self.maybe_staff_bubble(staff, service)

    def table_order(self, g: Guest):
        drink = self.choose_drink(g)
        if not drink:
            g.satisfaction -= 6
            return
        self.stock[drink] -= 1
        price = self.prices[drink]
        if g.intent == "vip":
            price += 120
            self.ledger.tips += 120
        self.cash += price
        self.ledger.sales += price
        g.spent += price
        bonus = 5 + self.price_bonus(drink)
        g.satisfaction += bonus
        self._served += 1
        self.maybe_guest_bubble(g, 68 + bonus * 8)

    def send_home(self, g: Guest):
        g.state = "walk"
        g.intent = "exit"
        ex, ey = self.tile_center(*C.ENTRANCE)
        g.tx, g.ty = ex, ey

    def finish_guest(self, g: Guest):
        delta = (g.satisfaction - 62) / 100 * 0.7
        self.reputation = clamp(self.reputation + delta, 0, 100)
        if g in self.guests:
            self.guests.remove(g)

    def next_stop(self, g: Guest):
        if g.visits >= 1 or random.random() < 0.55:
            self.send_home(g)
        else:
            g.visits += 1
            g.intent = self.pick_intent(g.kind)
            g.tx, g.ty = self.pick_destination(g.intent)
            g.state = "walk"

    # ---------------------------------------------------------------- 员工与环境
    def staff_target(self, s: Staff):
        if s.kind == "security":
            return self.tile_center(*C.ENTRANCE)
        if s.kind == "cleaner":
            return self.tile_center(C.GRID_W // 2, C.GRID_H // 2)
        want = "bar" if s.kind == "bartender" else "stage"
        for pos, f in self.facilities.items():
            if f.kind == want:
                return self.tile_center(*pos)
        return self.tile_center(2, 4)

    def update_staff(self, dt: float):
        for s in self.staff:
            s.busy = max(0.0, s.busy - dt)
            tx, ty = self.staff_target(s)
            dx, dy = tx - s.x, ty - s.y
            dist = math.hypot(dx, dy)
            if dist > 6:
                step = min(dist, 34 * dt)
                s.x += dx / dist * step
                s.y += dy / dist * step

    def update_ambience(self, dt: float):
        restroom_factor = max(0.2, 1 - 0.1 * self.total_level("restroom"))
        decay = 0.004 * len(self.guests) * restroom_factor
        self.cleanliness = clamp(self.cleanliness - decay * dt
                                 + self.count_staff("cleaner") * 0.35 * dt, 0, 100)
        self.hype = clamp(self.hype - 0.5 * dt
                          + (self.total_level("light") * 0.05
                             + self.count_staff("dj") * 0.08) * dt, 0, 100)

    # ---------------------------------------------------------------- 结算
    def close_night(self):
        ev = self.event
        if ev["id"] == "inspection":
            if self.cleanliness < 60:
                self.cash -= 1500
                self.ledger.fines += 1500
                self.add_log("卫生检查不合格：罚款 1,500 元。", "bad")
            else:
                self.reputation = clamp(self.reputation + 5, 0, 100)
                self.add_log("卫生检查通过：声望 +5。", "good")
        if ev["id"] == "broken_speaker":
            self.cash -= 800
            self.ledger.repair += 800
            self.add_log("支付音响维修费 800 元。", "bad")
        if ev["id"] == "noise_complaint" and self.hype > 65:
            self.cash -= 900
            self.ledger.fines += 900
            self.add_log("噪音超标被投诉：罚款 900 元。", "bad")
        self.reputation = clamp(self.reputation + ev.get("rep", 0), 0, 100)

        self.ledger.salaries = sum(C.STAFF[s.kind]["salary"] for s in self.staff)
        self.ledger.upkeep = sum(C.FACILITIES[f.kind]["upkeep"] * f.level
                                 for f in self.facilities.values())
        self.ledger.utilities = 280.0
        self.cash -= self.ledger.salaries + self.ledger.upkeep + self.ledger.utilities

        self.settlement = {
            "day": self.day,
            "event": ev["name"],
            "visitors": self._visitors,
            "served": self._served,
            "rep_before": self._rep_start,
            "rep_after": self.reputation,
            "cash": self.cash,
            "net": self.ledger.net(),
            "rows": [
                ("酒水销售", self.ledger.sales, True),
                ("门票收入", self.ledger.cover, True),
                ("小费与包厢服务", self.ledger.tips, True),
                ("员工薪资", -self.ledger.salaries, False),
                ("设施维护", -self.ledger.upkeep, False),
                ("水电杂费", -self.ledger.utilities, False),
                ("酒水采购", -self.ledger.purchase, False),
                ("建造与升级", -self.ledger.build, False),
                ("招聘与杂费", -self.ledger.other, False),
                ("罚款与维修", -(self.ledger.fines + self.ledger.repair), False),
            ],
        }
        self.phase = "settlement"
        self.guests.clear()
        self.add_log(f"第 {self.day} 夜结算完成，净额 {self.ledger.net():+,.0f} 元。", "time")

    def next_day(self):
        if self.phase != "settlement":
            return
        if self.cash < C.BANKRUPT_CASH:
            self.result, self.result_reason = "lose", "资金链断裂，夜店被迫转让。"
        elif self.reputation >= C.TARGET_REP and self.cash >= C.TARGET_CASH:
            self.result, self.result_reason = "win", "达成经营目标，霓虹不夜城正式起航！"
        elif self.day >= C.TOTAL_DAYS:
            self.result, self.result_reason = "lose", "合同到期，未能达成经营目标。"
        if self.result:
            self.phase = "gameover"
            self.add_log(self.result_reason, "event" if self.result == "win" else "bad")
            return
        self.day += 1
        self.phase = "ready"
        self.clock = float(C.OPEN_HOUR)
        self.ledger = Ledger()
        self.event = self.pick_event()
        self.settlement = None
        self.add_log(f"第 {self.day} 夜：事件「{self.event['name']}」— {self.event['desc']}", "event")

    # ---------------------------------------------------------------- 玩家操作
    def build(self, kind: str, pos: tuple):
        if self.phase in ("settlement", "gameover"):
            return False, "当前阶段不可建造。"
        if kind not in C.FACILITIES:
            return False, "无效设施。"
        if pos == C.ENTRANCE or pos in self.facilities:
            return False, "该位置不可建造。"
        if kind == "vip" and self.reputation < 55:
            return False, "声望 ≥ 55 才能建造 VIP 包厢。"
        cost = C.FACILITIES[kind]["cost"]
        if self.cash < cost:
            return False, f"现金不足，需要 {cost:,} 元。"
        self.cash -= cost
        self.ledger.build += cost
        self.facilities[pos] = Facility(kind)
        self.add_log(f"建造 {C.FACILITIES[kind]['name']}，支出 {cost:,} 元。", "info")
        return True, f"已建造 {C.FACILITIES[kind]['name']}。"

    def upgrade(self, pos: tuple):
        if self.phase in ("settlement", "gameover"):
            return False, "当前阶段不可升级。"
        f = self.facilities.get(pos)
        if not f:
            return False, "此处没有设施。"
        if f.level >= C.MAX_LEVEL:
            return False, "已达最高等级。"
        cost = int(C.FACILITIES[f.kind]["cost"] * (0.7 + 0.5 * f.level))
        if self.cash < cost:
            return False, f"现金不足，需要 {cost:,} 元。"
        self.cash -= cost
        self.ledger.build += cost
        f.level += 1
        self.add_log(f"{C.FACILITIES[f.kind]['name']} 升至 Lv.{f.level}，支出 {cost:,} 元。", "info")
        return True, "升级完成。"

    def demolish(self, pos: tuple):
        if self.phase in ("settlement", "gameover"):
            return False, "当前阶段不可拆除。"
        f = self.facilities.get(pos)
        if not f:
            return False, "此处没有设施。"
        refund = int(C.FACILITIES[f.kind]["cost"] * f.level * 0.4)
        del self.facilities[pos]
        self.cash += refund
        self.add_log(f"拆除 {C.FACILITIES[f.kind]['name']}，返还 {refund:,} 元。", "info")
        return True, "已拆除。"

    def hire(self, kind: str, free: bool = False):
        if kind not in C.STAFF:
            return False, "无效职位。"
        data = C.STAFF[kind]
        if not free:
            if self.phase in ("settlement", "gameover"):
                return False, "当前阶段不可雇佣。"
            if self.cash < data["hire"]:
                return False, f"现金不足，需要 {data['hire']:,} 元。"
            self.cash -= data["hire"]
            self.ledger.other += data["hire"]
        home = self.tile_center(2, 4) if kind != "bartender" else self.tile_center(3, 2)
        self.staff.append(Staff(kind=kind, uid=self._uid, x=home[0], y=home[1]))
        self._uid += 1
        if not free:
            self.add_log(f"雇佣 {data['name']}，签约费 {data['hire']:,} 元。", "info")
        return True, f"已雇佣 {data['name']}。"

    def fire(self, kind: str):
        if self.phase in ("settlement", "gameover"):
            return False, "当前阶段不可解雇。"
        for i in range(len(self.staff) - 1, -1, -1):
            if self.staff[i].kind == kind:
                del self.staff[i]
                self.add_log(f"解雇一名{C.STAFF[kind]['name']}。", "info")
                return True, "已解雇。"
        return False, "没有该职位员工。"

    def buy(self, drink: str, qty: int):
        if self.phase in ("settlement", "gameover"):
            return False, "当前阶段不可采购。"
        if drink not in C.DRINKS or qty <= 0:
            return False, "无效采购。"
        cost = int(C.DRINKS[drink]["cost"] * qty * self.event["cost"])
        if self.cash < cost:
            return False, f"现金不足，需要 {cost:,} 元。"
        self.cash -= cost
        self.ledger.purchase += cost
        self.stock[drink] += qty
        self.add_log(f"采购 {C.DRINKS[drink]['name']} ×{qty}，支出 {cost:,} 元。", "info")
        return True, "采购完成。"

    def adjust_price(self, drink: str, delta: int):
        if self.phase in ("settlement", "gameover"):
            return False, "当前阶段不可调价。"
        base = C.DRINKS[drink]
        step = 20 if base["price"] >= 150 else 5
        new = self.prices[drink] + delta * step
        new = clamp(new, base["cost"] * 0.6, base["cost"] * 5)
        self.prices[drink] = new
        self.add_log(f"{base['name']} 售价调整为 {new:.0f} 元。", "info")
        return True, "价格已更新。"
