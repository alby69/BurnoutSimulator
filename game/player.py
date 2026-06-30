from dataclasses import dataclass, field
from typing import Dict

@dataclass
class Player:
    name: str
    energy: int = 100
    reputation: int = 50
    integrity: int = 50
    stress: int = 0
    employability: int = 50
    tags: Dict[str, int] = field(default_factory=lambda: {
        "yes_man": 0,
        "boundary_setter": 0,
        "truth_teller": 0,
        "survivor": 0,
        "burnout_risk": 0
    })
    days_survived: int = 0
    is_alive: bool = True
    status: str = "Active"

    def update_stats(self, effects: dict):
        for stat, value in effects.items():
            if hasattr(self, stat):
                current_val = getattr(self, stat)
                if stat == "stress":
                    # Stress usually increases, we cap it at 100 but it starts from 0
                    setattr(self, stat, max(0, min(100, current_val + value)))
                else:
                    setattr(self, stat, max(0, min(100, current_val + value)))

        self.check_conditions()

    def add_tags(self, tags_list: list):
        for tag in tags_list:
            if tag in self.tags:
                self.tags[tag] += 1
            else:
                self.tags[tag] = 1

    def check_conditions(self):
        if self.energy <= 0:
            self.is_alive = False
            self.status = "Burnout (Esaurimento Fisico)"
        elif self.stress >= 100:
            self.is_alive = False
            self.status = "Burnout (Collasso Nervoso)"
        elif self.reputation <= 0:
            self.is_alive = False
            self.status = "Licenziato"
        elif self.integrity <= 0:
            self.is_alive = False
            self.status = "Alienazione Totale"
        elif self.days_survived >= 365:
            self.is_alive = False
            self.status = "Sopravvissuto"

    def to_dict(self):
        return {
            "name": self.name,
            "stats": {
                "energy": self.energy,
                "reputation": self.reputation,
                "integrity": self.integrity,
                "stress": self.stress,
                "employability": self.employability
            },
            "tags": self.tags,
            "days_survived": self.days_survived,
            "status": self.status
        }
