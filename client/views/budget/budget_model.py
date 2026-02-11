from dataclasses import dataclass
from typing import List, Dict

@dataclass
class BudgetCategory:
    name: str
    limit: float
    spent: float

    @property
    def percent(self) -> float:
        if self.limit == 0: return 0
        return (self.spent / self.limit) * 100

@dataclass
class Subscription:
    name: str
    amount: float
    frequency: str = "חודשי"

@dataclass
class SavingsGoal:
    name: str
    target: float
    current: float

    @property
    def percent(self) -> float:
        if self.target == 0: return 0
        return (self.current / self.target) * 100

@dataclass
class BudgetModel:
    budgets: List[BudgetCategory]
    subscriptions: List[Subscription]
    savings: List[SavingsGoal]