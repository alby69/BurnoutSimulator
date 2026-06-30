from dataclasses import dataclass, field
from typing import Dict

@dataclass
class Player:
    name: str
    energy: int = 100
    stress: int = 0
    self_esteem: int = 50
    manager_rep: int = 50
    team_rep: int = 50
    integrity: int = 50
    employability: int = 50
    health: int = 100
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
            # Support legacy 'reputation' key by mapping it to manager_rep
            target_stat = stat
            if stat == "reputation":
                target_stat = "manager_rep"

            if hasattr(self, target_stat):
                current_val = getattr(self, target_stat)
                # All stats are clamped between 0 and 100
                setattr(self, target_stat, max(0, min(100, current_val + value)))

        self.check_conditions()

    def add_tags(self, tags_list: list):
        for tag in tags_list:
            if tag in self.tags:
                self.tags[tag] += 1
            else:
                self.tags[tag] = 1

    def check_conditions(self):
        if self.health <= 0:
            self.is_alive = False
            self.status = "Burnout (Crollo Fisico)"
        elif self.stress >= 100:
            self.is_alive = False
            self.status = "Burnout (Crollo Mentale)"
        elif self.energy <= 0:
            self.is_alive = False
            self.status = "Esaurimento Energie"
        elif self.manager_rep <= 0:
            self.is_alive = False
            self.status = "Licenziato"
        elif self.self_esteem <= 0:
            self.is_alive = False
            self.status = "Depressione Professionale"
        elif self.integrity <= 0:
            self.is_alive = False
            self.status = "Promozione Tossica (Sei parte del problema)"
        elif self.days_survived >= 365:
            self.is_alive = False
            self.status = "Sopravvissuto"

    def to_dict(self):
        return {
            "name": self.name,
            "stats": {
                "energy": self.energy,
                "stress": self.stress,
                "self_esteem": self.self_esteem,
                "manager_rep": self.manager_rep,
                "team_rep": self.team_rep,
                "integrity": self.integrity,
                "employability": self.employability,
                "health": self.health
            },
            "tags": self.tags,
            "days_survived": self.days_survived,
            "status": self.status
        }
