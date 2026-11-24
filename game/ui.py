# -*- coding: utf-8 -*-
"""侧栏面板、按钮、弹窗与鼠标交互。"""
import pygame as pg

from . import android_compat as AC
from . import config as C
from .renderer import font, lighten


def text(s, content, x, y, size=12, color=None, bold=False):
    s.blit(font(size, bold).render(content, True, color or C.TEXT), (x, y))


def wrap_lines(content, max_width, size=11, bold=False):
    fnt = font(size, bold)
    lines, current = [], ""
    for ch in content:
        if ch == "\n":
            lines.append(current)
            current = ""
            continue
        if current and fnt.size(current + ch)[0] > max_width:
            lines.append(current)
            current = ch
        else:
            current += ch
    if current:
        lines.append(current)
    return lines


class Button:
    def __init__(self, rect, label, callback, color=None, enabled=True,
                 size=13, transparent=False):
        self.rect = pg.Rect(rect)
        self.label = label
        self.callback = callback
        self.color = color or C.BUTTON
        self.enabled = enabled
        self.size = size
        self.transparent = transparent
        self.hit_pad = 0 if transparent else AC.HIT_PAD

    @property
    def hit_rect(self):
        if not self.hit_pad:
            return self.rect
        return self.rect.inflate(self.hit_pad * 2, self.hit_pad * 2)

    def draw(self, screen):
        if self.transparent:
            return
        hover = self.enabled and self.rect.collidepoint(pg.mouse.get_pos())
        color = self.color if self.enabled else C.DISABLED
        if hover:
            color = lighten(color, 22)
        pg.draw.rect(screen, color, self.rect, border_radius=6)
        pg.draw.rect(screen, C.BORDER, self.rect, 1, border_radius=6)
        label = font(self.size, True).render(
            self.label, True, C.TEXT if self.enabled else C.MUTED)
        screen.blit(label, label.get_rect(center=self.rect.center))

    def click(self):
        if self.enabled and self.callback:
            self.callback()


class UI:
    TABS = [("overview", "总览"), ("build", "建造"), ("staff", "员工"),
            ("drinks", "酒水"), ("log", "日志")]

    def __init__(self, sim):
        self.sim = sim
        self.tab = "overview"
        self.buttons = []
        self.hover_tile = None
        self.selected_tile = None
        self.build_menu = None
        self.show_help = False
        self.message = ""
        self.msg_until = 0

    # ------------------------------------------------------------ 通知/输入
    def notify(self, message: str):
        self.message = message
        self.msg_until = pg.time.get_ticks() + 2600

    def act(self, result):
        ok, message = result
        self.notify(message)
        return ok

    def handle_click(self, pos, sim):
        for button in reversed(self.buttons):
            if button.enabled and button.hit_rect.collidepoint(pos):
                button.click()
                return
        tile = sim.world_to_tile(*pos)
        if tile:
            self.selected_tile = tile
            if (self.tab == "build" and tile != C.ENTRANCE
                    and sim.phase not in ("settlement", "gameover")):
                self.build_menu = tile

    # ------------------------------------------------------------ 绘制入口
    def draw(self, screen, sim):
        self.buttons = []
        self.draw_sidebar(screen, sim)
        self.draw_bottom(screen, sim)
        self.draw_overlays(screen, sim)
        self.draw_toast(screen)
        for button in self.buttons:
            button.draw(screen)

    def button(self, rect, label, callback, **kwargs):
        b = Button(rect, label, callback, **kwargs)
        self.buttons.append(b)
        return b

    # ------------------------------------------------------------ 侧栏
    def draw_sidebar(self, s, sim):
        panel = pg.Rect(C.SIDE_X, C.MAP_Y, C.SIDE_W, C.GRID_H * C.TILE)
        pg.draw.rect(s, C.PANEL, panel, border_radius=8)
        pg.draw.rect(s, C.BORDER, panel, 1, border_radius=8)
        text(s, "经营控制台", C.SIDE_X + 12, C.MAP_Y + 9, 13, C.ACCENT, True)

        tab_y, tab_h, gap = C.MAP_Y + 34, 28, 4
        inner_x = C.SIDE_X + 12
        inner_w = C.SIDE_W - 24
        tab_w = (inner_w - gap * 4) // 5
        for i, (key, label) in enumerate(self.TABS):
            rect = (inner_x + i * (tab_w + gap), tab_y, tab_w, tab_h)
            color = C.BUTTON_HOVER if self.tab == key else C.BUTTON
            self.button(rect, label, lambda k=key: setattr(self, "tab", k),
                        color=color, size=12)

        top = tab_y + tab_h + 14
        if self.tab == "overview":
            self.draw_overview(s, sim, inner_x, inner_w, top)
        elif self.tab == "build":
            self.draw_build(s, sim, inner_x, inner_w, top)
        elif self.tab == "staff":
            self.draw_staff(s, sim, inner_x, inner_w, top)
        elif self.tab == "drinks":
            self.draw_drinks(s, sim, inner_x, inner_w, top)
        else:
            self.draw_log(s, sim, inner_x, inner_w, top)

    @staticmethod
    def section(s, title, x, y, width):
        pg.draw.rect(s, C.ACCENT, (x, y + 2, 3, 15))
        text(s, title, x + 9, y, 13, C.ACCENT, True)
        pg.draw.line(s, C.BORDER, (x, y + 22), (x + width, y + 22))

    def bar(self, s, x, y, width, label, value, max_value, color):
        text(s, f"{label}  {value:.0f} / {max_value:.0f}", x, y, 11)
        pg.draw.rect(s, (18, 21, 30), (x, y + 18, width, 9), border_radius=4)
        pg.draw.rect(s, color, (x, y + 18,
                                max(3, int(width * min(value, max_value) / max_value)), 9),
                     border_radius=4)

    def draw_overview(self, s, sim, x, w, top):
        self.section(s, "实时状态", x, top, w)
        self.bar(s, x, top + 32, w, "声望", sim.reputation, 100, C.ACCENT)
        self.bar(s, x, top + 76, w, "清洁度", sim.cleanliness, 100,
                 C.GOOD if sim.cleanliness >= 60 else C.BAD)
        self.bar(s, x, top + 120, w, "气氛", sim.hype, 100, C.INFO)

        self.section(s, "今晚事件", x, top + 168, w)
        box = pg.Rect(x, top + 198, w, 80)
        pg.draw.rect(s, C.PANEL_LIGHT, box, border_radius=6)
        text(s, sim.event["name"], x + 10, box.y + 8, 13, C.ACCENT, True)
        for i, line in enumerate(wrap_lines(sim.event["desc"], w - 20, 11)[:3]):
            text(s, line, x + 10, box.y + 30 + i * 16, 11, C.MUTED)

        self.section(s, "经营速览", x, top + 290, w)
        rows = [
            ("设施数量", f"{len(sim.facilities)} 处"),
            ("团队规模", f"{len(sim.staff)} 人"),
            ("今夜客流", f"{sim._visitors} 人"),
            ("酒水售出", f"{sim._served} 杯"),
            ("当前净额", f"{sim.ledger.net():+,.0f} 元"),
        ]
        for i, (label, value) in enumerate(rows):
            y = top + 322 + i * 23
            text(s, label, x, y, 11, C.MUTED)
            label_w = font(11).size(value)[0]
            text(s, value, x + w - label_w, y, 11,
                 C.GOOD if sim.ledger.net() >= 0 else C.BAD)

        hint = "提示：声望 ≥ 55 才会吸引贵宾；清洁度低于 60 可能触发卫生罚款。"
        for i, line in enumerate(wrap_lines(hint, w, 10)[:2]):
            text(s, line, x, top + 448 + i * 15, 10, C.MUTED)

    def draw_build(self, s, sim, x, w, top):
        self.section(s, "建造指南", x, top, w)
        for i, line in enumerate(wrap_lines("点击场地空地选择设施；点击已有设施可升级或拆除。", w, 11)[:2]):
            text(s, line, x, top + 30 + i * 17, 11, C.MUTED)

        box = pg.Rect(x, top + 68, w, 80)
        pg.draw.rect(s, C.PANEL_LIGHT, box, border_radius=6)
        if self.selected_tile:
            gx, gy = self.selected_tile
            facility = sim.facilities.get(self.selected_tile)
            text(s, f"选中格：({gx}, {gy})", x + 10, box.y + 8, 12, C.ACCENT, True)
            if facility:
                data = C.FACILITIES[facility.kind]
                text(s, f"{data['name']}  Lv.{facility.level}", x + 10, box.y + 30, 11)
                next_cost = int(data["cost"] * (0.7 + 0.5 * facility.level))
                self.button((x + 10, box.y + 50, 96, 24), "升级",
                            lambda: self.act(sim.upgrade(self.selected_tile)),
                            enabled=facility.level < C.MAX_LEVEL)
                text(s, f"{next_cost:,} 元", x + 112, box.y + 54, 10, C.MUTED)
                self.button((x + w - 88, box.y + 50, 78, 24), "拆除",
                            lambda: self.act(sim.demolish(self.selected_tile)))
            else:
                text(s, "空地 — 点击地图建造", x + 10, box.y + 30, 11, C.MUTED)
        else:
            text(s, "尚未选中地块", x + 10, box.y + 16, 12, C.MUTED)

        self.section(s, "设施造价", x, top + 158, w)
        for i, kind in enumerate(C.FACILITY_ORDER):
            data = C.FACILITIES[kind]
            y = top + 188 + i * 43
            text(s, data["name"], x, y, 11, C.TEXT, True)
            cost = f"{data['cost']:,}"
            text(s, cost, x + w - font(11).size(cost)[0], y, 11, C.ACCENT)
            text(s, data["desc"], x, y + 17, 10, C.MUTED)
        if sim.reputation < 55:
            text(s, "VIP包厢需声望 ≥ 55 解锁", x, top + 486, 10, C.MUTED)

    def draw_staff(self, s, sim, x, w, top):
        self.section(s, "团队管理", x, top, w)
        for i, kind in enumerate(C.STAFF_ORDER):
            data = C.STAFF[kind]
            y = top + 30 + i * 102
            box = pg.Rect(x, y, w, 94)
            pg.draw.rect(s, C.PANEL_LIGHT, box, border_radius=6)
            pg.draw.rect(s, data["color"], (box.x, box.y, 4, box.height))
            text(s, data["name"], x + 12, y + 8, 12, C.TEXT, True)
            count = f"×{sim.count_staff(kind)}"
            text(s, count, x + w - font(12).size(count)[0] - 10, y + 8, 12, C.ACCENT, True)
            text(s, f"日薪 {data['salary']} / 签约 {data['hire']}", x + 12, y + 29, 10, C.MUTED)
            for j, line in enumerate(wrap_lines(data["desc"], 190, 10)[:2]):
                text(s, line, x + 12, y + 47 + j * 14, 10, C.INFO)
            self.button((x + w - 132, y + 56, 56, 26), "雇佣",
                        lambda k=kind: self.act(sim.hire(k)), size=11)
            self.button((x + w - 70, y + 56, 56, 26), "解雇",
                        lambda k=kind: self.act(sim.fire(k)), size=11)

        total = sum(C.STAFF[st.kind]["salary"] for st in sim.staff)
        text(s, f"每晚固定人力成本：{total:,} 元", x, top + 442, 11, C.ACCENT, True)

    def draw_drinks(self, s, sim, x, w, top):
        self.section(s, "酒水经营", x, top, w)
        for i, kind in enumerate(C.DRINK_ORDER):
            data = C.DRINKS[kind]
            y = top + 30 + i * 150
            box = pg.Rect(x, y, w, 142)
            pg.draw.rect(s, C.PANEL_LIGHT, box, border_radius=6)
            pg.draw.rect(s, data["color"], (box.x, box.y, 4, box.height))
            text(s, data["name"], x + 12, y + 8, 12, C.TEXT, True)
            stock = f"库存 {sim.stock[kind]}"
            text(s, stock, x + w - font(11).size(stock)[0] - 10, y + 9, 11,
                 C.BAD if sim.stock[kind] == 0 else C.GOOD)
            text(s, f"进价 {data['cost']}   售价 {sim.prices[kind]:.0f}   "
                    f"毛利 {sim.prices[kind] - data['cost']:.0f}",
                 x + 12, y + 29, 11, C.MUTED)
            self.button((x + 12, y + 52, 62, 26), "- 调价",
                        lambda k=kind: self.act(sim.adjust_price(k, -1)), size=11)
            self.button((x + 80, y + 52, 62, 26), "+ 调价",
                        lambda k=kind: self.act(sim.adjust_price(k, 1)), size=11)
            self.button((x + 12, y + 90, 92, 30), "采购 ×10",
                        lambda k=kind: self.act(sim.buy(k, 10)), size=11)
            self.button((x + 110, y + 90, 92, 30), "采购 ×50",
                        lambda k=kind: self.act(sim.buy(k, 50)), size=11)
            if i == 0 and sim.event["cost"] < 1:
                text(s, f"促销中：采购成本 ×{sim.event['cost']}", x + 12, y + 124, 10, C.GOOD)

    def draw_log(self, s, sim, x, w, top):
        self.section(s, "经营日志", x, top, w)
        y = top + 32
        for entry in sim.log[:24]:
            color = C.MUTED
            if "罚款" in entry or "损失" in entry or "售罄" in entry:
                color = C.BAD
            elif "通过" in entry or "请走" in entry or "达成" in entry:
                color = C.GOOD
            elif "事件" in entry or "开始营业" in entry:
                color = C.ACCENT
            for line in wrap_lines(entry, w, 10)[:2]:
                if y > C.MAP_Y + C.GRID_H * C.TILE - 20:
                    return
                text(s, line, x, y, 10, color)
                y += 14

    # ------------------------------------------------------------ 底栏
    def draw_bottom(self, s, sim):
        pg.draw.rect(s, C.PANEL, (0, C.BOTTOM_Y, C.WINDOW_W, C.BOTTOM_H))
        pg.draw.line(s, C.BORDER, (0, C.BOTTOM_Y), (C.WINDOW_W, C.BOTTOM_Y))
        y = C.BOTTOM_Y + 7
        h = C.BOTTOM_H - 14
        x = 16

        if sim.phase == "ready":
            label, action = "开始营业", sim.start_night
        elif sim.phase == "open":
            label = "暂停" if not sim.paused else "继续"
            action = sim.toggle_pause
        else:
            label, action = "已结束", None
        self.button((x, y, 100, h), label, action,
                    color=C.GOOD if sim.phase == "ready" else C.BUTTON,
                    enabled=sim.phase in ("ready", "open"))
        x += 108

        for speed in (1, 2, 4):
            color = C.BUTTON_HOVER if sim.speed == speed and not sim.paused else C.BUTTON
            self.button((x, y, 46, h), f"{speed}x",
                        lambda v=speed: sim.set_speed(v), color=color,
                        enabled=sim.phase == "open", size=12)
            x += 54

        self.button((x, y, 100, h), "提前打烊", sim.close_night,
                    enabled=sim.phase == "open", size=12)
        x += 108
        self.button((x, y, 80, h), "新游戏",
                    lambda: (sim.reset(), self.notify("已开始新的一局。")), size=12)
        x += 88
        self.button((x, y, 70, h), "帮助 H",
                    lambda: setattr(self, "show_help", not self.show_help), size=12)

        hint = "空格：暂停    H：帮助    右侧标签：经营操作    点击地图：选地/建造"
        text(s, hint, x + 80, C.BOTTOM_Y + 16, 11, C.MUTED)

    # ------------------------------------------------------------ 弹窗
    @staticmethod
    def dim(s):
        overlay = pg.Surface((C.WINDOW_W, C.WINDOW_H), pg.SRCALPHA)
        overlay.fill((6, 8, 14, 165))
        s.blit(overlay, (0, 0))

    def draw_overlays(self, s, sim):
        if self.build_menu and sim.phase not in ("settlement", "gameover"):
            self.dim(s)
            self.button((0, 0, C.WINDOW_W, C.WINDOW_H), "",
                        lambda: setattr(self, "build_menu", None), transparent=True)
            panel = pg.Rect((C.WINDOW_W - 520) // 2, (C.WINDOW_H - 350) // 2, 520, 350)
            pg.draw.rect(s, C.PANEL, panel, border_radius=10)
            pg.draw.rect(s, C.BORDER, panel, 2, border_radius=10)
            gx, gy = self.build_menu
            text(s, f"在 ({gx}, {gy}) 建造设施", panel.x + 20, panel.y + 16,
                 15, C.ACCENT, True)
            for i, kind in enumerate(C.FACILITY_ORDER):
                data = C.FACILITIES[kind]
                col, row = i % 2, i // 2
                rect = (panel.x + 20 + col * 246, panel.y + 54 + row * 56, 232, 46)
                unlocked = kind != "vip" or sim.reputation >= 55
                affordable = sim.cash >= data["cost"]
                label = f"{data['name']}   {data['cost']:,} 元"
                if kind == "vip" and not unlocked:
                    label += "  [声望55解锁]"
                self.button(rect, label,
                            lambda k=kind: self.do_build(k),
                            color=data["color"] if affordable and unlocked else C.DISABLED,
                            enabled=affordable and unlocked, size=12)
            self.button((panel.x + 20, panel.y + 302, 480, 32), "取消",
                        lambda: setattr(self, "build_menu", None))

        if sim.phase == "settlement" and sim.settlement:
            self.dim(s)
            data = sim.settlement
            panel = pg.Rect(310, 120, 660, 478)
            pg.draw.rect(s, C.PANEL, panel, border_radius=10)
            pg.draw.rect(s, C.BORDER, panel, 2, border_radius=10)
            text(s, f"第 {data['day']} 夜结算 · {data['event']}",
                 panel.x + 24, panel.y + 18, 17, C.ACCENT, True)
            text(s, f"客流 {data['visitors']} 人  |  售出 {data['served']} 杯  |  "
                    f"声望 {data['rep_before']:.0f} → {data['rep_after']:.0f}",
                 panel.x + 24, panel.y + 48, 12, C.MUTED)
            pg.draw.line(s, C.BORDER, (panel.x + 24, panel.y + 76),
                         (panel.right - 24, panel.y + 76))
            for i, (label, amount, _) in enumerate(data["rows"]):
                y = panel.y + 86 + i * 25
                text(s, label, panel.x + 24, y, 12, C.TEXT)
                value = f"{amount:+,.0f}" if amount else "0"
                text(s, value, panel.right - 24 - font(12).size(value)[0], y, 12,
                     C.GOOD if amount > 0 else (C.BAD if amount < 0 else C.MUTED))
            pg.draw.line(s, C.BORDER, (panel.x + 24, panel.y + 330),
                         (panel.right - 24, panel.y + 330))
            text(s, "本夜净额", panel.x + 24, panel.y + 344, 14, C.ACCENT, True)
            net = f"{data['net']:+,.0f} 元"
            text(s, net, panel.right - 24 - font(14, True).size(net)[0],
                 panel.y + 344, 14, C.GOOD if data["net"] >= 0 else C.BAD, True)
            text(s, f"当前现金：{data['cash']:,.0f} 元  |  距目标 "
                    f"{max(0, C.TARGET_CASH - data['cash']):,.0f} 元 / "
                    f"{max(0, C.TARGET_REP - data['rep_after']):.0f} 声望",
                 panel.x + 24, panel.y + 378, 11, C.MUTED)
            self.button((panel.x + 24, panel.y + 412, panel.width - 48, 38),
                        "进入下一夜 →", sim.next_day, color=C.GOOD, size=14)

        if sim.phase == "gameover":
            self.dim(s)
            panel = pg.Rect(360, 195, 560, 330)
            pg.draw.rect(s, C.PANEL, panel, border_radius=10)
            pg.draw.rect(s, C.BORDER, panel, 2, border_radius=10)
            won = sim.result == "win"
            text(s, "经营成功" if won else "经营失败",
                 panel.x + 28, panel.y + 26, 24, C.GOOD if won else C.BAD, True)
            for i, line in enumerate(wrap_lines(sim.result_reason, 500, 14)[:2]):
                text(s, line, panel.x + 28, panel.y + 76 + i * 22, 14, C.TEXT)
            text(s, f"营业夜数：{sim.day}   现金：{sim.cash:,.0f}   声望：{sim.reputation:.0f}",
                 panel.x + 28, panel.y + 140, 13, C.MUTED)
            self.button((panel.x + 28, panel.y + 240, panel.width - 56, 44),
                        "重新开始",
                        lambda: (sim.reset(), setattr(self, "build_menu", None)),
                        color=C.GOOD, size=15)

        if self.show_help:
            self.dim(s)
            self.button((0, 0, C.WINDOW_W, C.WINDOW_H),
                        "", lambda: setattr(self, "show_help", False), transparent=True)
            panel = pg.Rect(240, 92, 800, 536)
            pg.draw.rect(s, C.PANEL, panel, border_radius=10)
            pg.draw.rect(s, C.BORDER, panel, 2, border_radius=10)
            text(s, "玩法说明", panel.x + 24, panel.y + 18, 20, C.ACCENT, True)
            lines = [
                "目标：14 夜内现金 ≥ 38,000 元且声望 ≥ 80；现金低于 -3,000 元破产。",
                "每夜流程：准备（采购 / 调价 / 装修 / 排班）→ 营业 → 结算。",
                "右侧「建造」：点空地选设施，点已有设施升级/拆除；不同设施吸引不同客人。",
                "右侧「员工」：调酒师加快出杯，保安处置闹事者，DJ 提升音乐评分，保洁维持清洁。",
                "右侧「酒水」：低价带来人气但压缩毛利；贵宾偏好香槟，可加收包厢服务费。",
                "声望 ≥ 55 且拥有 VIP 包厢后才会出现贵宾；声望直接决定基础客流。",
                "清洁度低于 60 遇到卫生检查会罚款；噪音投诉事件下气氛过高也会被罚。",
                "快捷键：空格暂停/继续，H 打开或关闭帮助。底栏可切换 1x / 2x / 4x 倍速。",
                "本作为健康娱乐经营模拟，不含任何成人内容。",
            ]
            y = panel.y + 62
            for line in lines:
                for wrapped in wrap_lines(line, panel.width - 48, 13)[:2]:
                    text(s, wrapped, panel.x + 24, y, 13, C.TEXT)
                    y += 25
                y += 10
            self.button((panel.x + 24, panel.y + 470, panel.width - 48, 40),
                        "关闭帮助", lambda: setattr(self, "show_help", False),
                        color=C.GOOD)

    def draw_toast(self, s):
        if pg.time.get_ticks() < self.msg_until and self.message:
            rect = pg.Rect((C.WINDOW_W - 440) // 2, C.MAP_Y + 8, 440, 36)
            pg.draw.rect(s, (26, 32, 46), rect, border_radius=8)
            pg.draw.rect(s, C.ACCENT, rect, 2, border_radius=8)
            label = font(13).render(self.message, True, C.TEXT)
            s.blit(label, label.get_rect(center=rect.center))

    def do_build(self, kind):
        if self.build_menu:
            ok = self.act(self.sim.build(kind, self.build_menu))
            if ok:
                self.build_menu = None
