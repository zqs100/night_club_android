# -*- coding: utf-8 -*-
"""数据模型。"""
from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class Facility:
    kind: str
    level: int = 1


@dataclass
class Staff:
    kind: str
    uid: int
    x: float
    y: float
    busy: float = 0.0
    bubble_text: str = ""
    bubble_tone: str = ""
    bubble_until: float = 0.0
    last_bubble_at: float = -999.0


@dataclass
class Guest:
    uid: int
    kind: str
    x: float
    y: float
    tx: float
    ty: float
    intent: str
    state: str = "walk"
    timer: float = 0.0
    budget: float = 0.0
    spent: float = 0.0
    satisfaction: float = 75.0
    drink: Optional[str] = None
    visits: int = 0
    bubble_text: str = ""
    bubble_tone: str = ""
    bubble_until: float = 0.0
    last_bubble_at: float = -999.0


@dataclass
class Ledger:
    sales: float = 0.0
    cover: float = 0.0
    tips: float = 0.0
    salaries: float = 0.0
    upkeep: float = 0.0
    utilities: float = 0.0
    fines: float = 0.0
    purchase: float = 0.0
    build: float = 0.0
    repair: float = 0.0
    other: float = 0.0

    def income(self) -> float:
        return self.sales + self.cover + self.tips

    def expense(self) -> float:
        return (self.salaries + self.upkeep + self.utilities + self.fines
                + self.purchase + self.build + self.repair + self.other)

    def net(self) -> float:
        return self.income() - self.expense()
