from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
from collections import defaultdict


@dataclass
class DecisionRecord:
    event_id: str
    choice_id: str
    choice_text: str
    category: str
    was_auto: bool
    day: int = 0
    human_id: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    outcomes: Dict = field(default_factory=dict)


class AgentMemory:
    """
    Memoria storica di un agente. Tiene traccia di tutte le decisioni
    e dei loro esiti per apprendimento e visualizzazione.
    """
    def __init__(self):
        self.decisions: List[DecisionRecord] = []
        self.choice_outcomes: Dict[str, List[Dict]] = defaultdict(list)
        self.event_frequency: Dict[str, int] = defaultdict(int)
        self.category_frequency: Dict[str, int] = defaultdict(int)

    def record_decision(self, event_id: str, choice_id: str, choice_text: str,
                        category: str, was_auto: bool, day: int = 0, human_id: Optional[str] = None):
        record = DecisionRecord(
            event_id=event_id,
            choice_id=choice_id,
            choice_text=choice_text,
            category=category,
            was_auto=was_auto,
            day=day,
            human_id=human_id
        )
        self.decisions.append(record)
        self.event_frequency[event_id] += 1
        self.category_frequency[category] += 1

    def record_outcome(self, choice_id: str, stats_before: Dict, stats_after: Dict) -> Dict:
        """Registra l'esito di una scelta per apprendimento."""
        outcomes = {
            "timestamp": datetime.now().isoformat(),
            "stress_delta": stats_after.get("stress", 0) - stats_before.get("stress", 0),
            "energy_delta": stats_after.get("energy", 0) - stats_before.get("energy", 0),
            "health_delta": stats_after.get("health", 0) - stats_before.get("health", 0),
            "integrity_delta": stats_after.get("integrity", 0) - stats_before.get("integrity", 0),
        }
        self.choice_outcomes[choice_id].append(outcomes)
        return outcomes

    def get_choice_outcomes(self, choice_id: str) -> List[Dict]:
        return self.choice_outcomes.get(choice_id, [])

    def get_human_vs_auto_stats(self) -> Dict:
        """Statistiche confronto decisioni umane vs automatiche."""
        human = [d for d in self.decisions if not d.was_auto]
        auto = [d for d in self.decisions if d.was_auto]
        return {
            "human_decisions": len(human),
            "auto_decisions": len(auto),
            "human_categories": self._count_categories(human),
            "auto_categories": self._count_categories(auto),
        }

    def _count_categories(self, decisions: List[DecisionRecord]) -> Dict[str, int]:
        counts = defaultdict(int)
        for d in decisions:
            counts[d.category] += 1
        return dict(counts)

    def get_summary(self) -> Dict:
        return {
            "total_decisions": len(self.decisions),
            "unique_events": len(self.event_frequency),
            "category_distribution": dict(self.category_frequency),
            "most_frequent_events": sorted(
                self.event_frequency.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5],
            "human_vs_auto": self.get_human_vs_auto_stats()
        }
