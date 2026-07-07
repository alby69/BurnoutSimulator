import json
import os
from typing import List, Tuple, Dict, Any

DEFAULT_ENDINGS = [
    {
        "id": "IL WHISTLEBLOWER",
        "priority": 7,
        "conditions": [
            {"stat": "factions.Ribelli", "op": ">=", "value": 70},
            {"stat": "integrity", "op": ">=", "value": 60}
        ]
    },
    {
        "id": "IL BRACCIO DESTRO",
        "priority": 7,
        "conditions": [
            {"stat": "factions.Fedelissimi", "op": ">=", "value": 70},
            {"stat": "manager_rep", "op": ">=", "value": 80}
        ]
    },
    {
        "id": "LO SPETTATORE",
        "priority": 6,
        "conditions": [
            {"stat": "factions.Gruppo Silenzioso", "op": ">=", "value": 70}
        ]
    },
    {
        "id": "IL CAMALEONTE",
        "priority": 5,
        "conditions": [
            {"stat": "factions.Ribelli", "op": ">=", "value": 50},
            {"stat": "factions.Fedelissimi", "op": ">=", "value": 50},
            {"stat": "factions.Gruppo Silenzioso", "op": ">=", "value": 50}
        ]
    },
    {
        "id": "IL FONDATORE ESAURITO",
        "priority": 6,
        "conditions": [
            {"stat": "company_type", "op": "==", "value": "Startup Caotica"},
            {"stat": "tags.burnout_risk", "op": ">=", "value": 5}
        ]
    },
    {
        "id": "IL PECORA NERA",
        "priority": 6,
        "conditions": [
            {"stat": "company_type", "op": "==", "value": "Azienda Familiare"},
            {"stat": "tags.truth_teller", "op": ">=", "value": 5},
            {"stat": "manager_rep", "op": "<=", "value": 30}
        ]
    },
    {
        "id": "L'INGRANAGGIO PERFETTO",
        "priority": 5,
        "conditions": [
            {"stat": "company_type", "op": "==", "value": "Consulting"},
            {"stat": "tags.yes_man", "op": ">=", "value": 10}
        ]
    },
    {
        "id": "IL RESISTENTE",
        "priority": 4,
        "conditions": [
            {"stat": "energy", "op": "<=", "value": 10},
            {"stat": "days_survived", "op": ">=", "value": 20}
        ]
    },
    {
        "id": "L'INDIOMABILE",
        "priority": 3,
        "conditions": [
            {"stat": "self_esteem", "op": ">=", "value": 80},
            {"stat": "is_alive", "op": "==", "value": True}
        ]
    },
    {
        "id": "IL POLITICO",
        "priority": 4,
        "conditions": [
            {"stat": "status", "op": "==", "value": "Promosso"}
        ]
    },
    {
        "id": "IL CINICO",
        "priority": 4,
        "conditions": [
            {"stat": "status", "op": "==", "value": "Promozione Tossica"}
        ]
    },
    {
        "id": "IL CINESE",
        "priority": 3,
        "conditions": [
            {"stat": "status", "op": "==", "value": "Licenziato"}
        ]
    },
    {
        "id": "IL MARTIRE",
        "priority": 3,
        "conditions": [
            {"stat": "integrity", "op": ">=", "value": 80},
            {"stat": "manager_rep", "op": "<=", "value": 30}
        ]
    },
    {
        "id": "IL CINICO",
        "priority": 2,
        "conditions": [
            {"stat": "integrity", "op": "<=", "value": 25}
        ]
    },
    {
        "id": "IL FUGGITIVO",
        "priority": 2,
        "conditions": [
            {"stat": "employability", "op": ">=", "value": 70},
            {"stat": "is_alive", "op": "==", "value": True}
        ]
    },
    {
        "id": "IL RIFORMATORE",
        "priority": 3,
        "conditions": [
            {"stat": "manager_rep", "op": ">=", "value": 70},
            {"stat": "integrity", "op": ">=", "value": 70}
        ]
    },
    {
        "id": "IL CADUTO",
        "priority": 4,
        "conditions": [
            {"stat": "status", "op": "contains", "value": "Burnout"}
        ]
    }
]

class EndingResolver:
    def __init__(self, rules_file: str = "game/data/endings.json"):
        self.rules = self.load_rules(rules_file)

    def load_rules(self, rules_file: str) -> List[Dict]:
        if os.path.exists(rules_file):
            with open(rules_file, 'r') as f:
                return json.load(f)
        return DEFAULT_ENDINGS

    def _get_nested_attr(self, obj, attr_path):
        parts = attr_path.split('.')
        val = obj
        for part in parts:
            if hasattr(val, part):
                val = getattr(val, part)
            elif isinstance(val, dict) and part in val:
                val = val[part]
            else:
                return None
        return val

    def resolve(self, player) -> str:
        achieved = []
        for rule in self.rules:
            match = True
            for cond in rule["conditions"]:
                stat_val = self._get_nested_attr(player, cond["stat"])
                op = cond["op"]
                target = cond["value"]

                if op == ">=":
                    if not (stat_val is not None and stat_val >= target): match = False
                elif op == "<=":
                    if not (stat_val is not None and stat_val <= target): match = False
                elif op == "==":
                    # Handle Enum for company_type
                    if cond["stat"] == "company_type" and hasattr(stat_val, "value"):
                        stat_val = stat_val.value
                    if not (stat_val == target): match = False
                elif op == "contains":
                    if not (stat_val is not None and target in str(stat_val)): match = False

                if not match: break

            if match:
                achieved.append((rule["id"], rule["priority"]))

        if not achieved:
            return "IL SOPRAVVISSUTO"

        achieved.sort(key=lambda x: x[1], reverse=True)
        return achieved[0][0]

resolver = EndingResolver()

def determine_ending(player) -> str:
    return resolver.resolve(player)
