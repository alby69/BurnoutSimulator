from typing import Dict, List, Optional, Any
from agents.swarm import AgentSwarm
from database.agent_db import get_all_agents, get_swarm_history


class MainDashboard:
    """
    Dashboard unificata per monitoraggio simulazione.
    Integra tutti i sottomoduli (agent_monitor, reports, timeline_viewer, alert_system).
    """

    def __init__(self, swarm: Optional[AgentSwarm] = None):
        self.swarm = swarm
        self.alert_system = AlertSystem()
        self.timeline_viewer = TimelineViewer(swarm)
        self.reports = Reports(swarm)
        self.agent_monitor = AgentMonitor(swarm)

    def set_swarm(self, swarm: AgentSwarm):
        self.swarm = swarm
        self.timeline_viewer.swarm = swarm
        self.reports.swarm = swarm
        self.agent_monitor.swarm = swarm

    def get_overview(self) -> Dict:
        if not self.swarm:
            return {"error": "No swarm attached"}

        analytics = self.swarm.get_swarm_analytics()
        alerts = self.alert_system.evaluate_all(self.swarm)
        top_risks = self.agent_monitor.get_risk_ranking()

        return {
            "total_agents": len(self.swarm.agents),
            "alive_count": analytics.get("alive_count", 0),
            "avg_stress": analytics.get("avg_stress", 0),
            "total_decisions": analytics.get("total_decisions", 0),
            "possessed_count": analytics.get("possessed_count", 0),
            "alerts": alerts,
            "top_risks": top_risks[:5],
            "most_stressful_archetype": analytics.get("most_stressful_archetype"),
        }

    def render_overview(self):
        """Placeholder per integrazione NiceGUI."""
        pass

    def render_agent_grid(self):
        """Placeholder per integrazione NiceGUI."""
        pass


class AgentMonitor:
    """
    Monitoraggio in tempo reale degli agenti.
    Analisi dei rischi, ranking, trend.
    """

    def __init__(self, swarm: Optional[AgentSwarm] = None):
        self.swarm = swarm

    def get_risk_ranking(self) -> List[Dict]:
        if not self.swarm:
            return []
        rankings = []
        for agent_id, agent in self.swarm.agents.items():
            if not agent.engine:
                continue
            p = agent.engine.player
            risk_score = 0
            risk_factors = []

            if p.stress > 70:
                risk_score += 25
                risk_factors.append("stress_critico")
            if p.energy < 30:
                risk_score += 20
                risk_factors.append("energia_critica")
            if p.health < 30:
                risk_score += 25
                risk_factors.append("salute_critica")
            if p.self_esteem < 25:
                risk_score += 15
                risk_factors.append("autostima_critica")
            if p.manager_rep < 20:
                risk_score += 15
                risk_factors.append("rep_critica")

            # Burnout imminente
            if p.stress >= 80 or p.health <= 20 or p.energy <= 10:
                risk_score += 20
                risk_factors.append("burnout_imminente")

            # Vulnerabilità psicologica
            if agent.profile.neuroticism > 70 and p.stress > 50:
                risk_score += 10
                risk_factors.append("vulnerabile_neuroticismo")

            rankings.append(
                {
                    "agent_id": agent_id,
                    "name": agent.name,
                    "profile": agent.profile.name,
                    "risk_score": min(100, risk_score),
                    "risk_factors": risk_factors,
                    "stress": p.stress,
                    "energy": p.energy,
                    "health": p.health,
                    "days": p.days_survived,
                    "alive": p.is_alive,
                }
            )

        rankings.sort(key=lambda x: (-x["risk_score"], x["alive"]))
        return rankings

    def get_trend(
        self, agent_id: str, metric: str = "stress", window: int = 10
    ) -> List[int]:
        if not self.swarm or agent_id not in self.swarm.agents:
            return []
        agent = self.swarm.agents[agent_id]
        if not agent.engine:
            return []
        history = agent.engine.stats_history
        values = [s.get(metric, 0) for s in history]
        return values[-window:]


class AlertSystem:
    """
    Sistema di allerta per burnout, soglie critiche e trend anomali.
    """

    SEVERITY_COLORS = {
        "critical": "#ef4444",
        "warning": "#f59e0b",
        "info": "#3b82f6",
    }

    def __init__(self, swarm: Optional[AgentSwarm] = None):
        self.swarm = swarm
        self._alert_history: List[Dict] = []
        self._last_state: Dict[str, Dict] = {}

    def evaluate_all(self, swarm: Optional[AgentSwarm] = None) -> List[Dict]:
        if swarm:
            self.swarm = swarm
        if not self.swarm:
            return []
        alerts = []
        for agent_id, agent in self.swarm.agents.items():
            if not agent.engine or not agent.engine.player.is_alive:
                continue
            alerts.extend(self._evaluate_agent(agent_id, agent))
        return alerts

    def _evaluate_agent(self, agent_id: str, agent) -> List[Dict]:
        p = agent.engine.player
        alerts = []

        # Soglie critiche
        if p.stress >= 80:
            alerts.append(
                {
                    "agent_id": agent_id,
                    "agent_name": agent.name,
                    "type": "stress_critico",
                    "severity": "critical",
                    "message": f"Stress critico: {p.stress}%",
                    "value": p.stress,
                    "threshold": 80,
                }
            )
        if p.energy <= 20:
            alerts.append(
                {
                    "agent_id": agent_id,
                    "agent_name": agent.name,
                    "type": "energia_critica",
                    "severity": "critical",
                    "message": f"Energia esaurita: {p.energy}%",
                    "value": p.energy,
                    "threshold": 20,
                }
            )
        if p.health <= 25:
            alerts.append(
                {
                    "agent_id": agent_id,
                    "agent_name": agent.name,
                    "type": "salute_critica",
                    "severity": "critical",
                    "message": f"Salute critica: {p.health}%",
                    "value": p.health,
                    "threshold": 25,
                }
            )

        # Warning soglie
        if p.stress > 60 and p.stress < 80:
            alerts.append(
                {
                    "agent_id": agent_id,
                    "agent_name": agent.name,
                    "type": "stress_alto",
                    "severity": "warning",
                    "message": f"Stress elevato: {p.stress}%",
                    "value": p.stress,
                    "threshold": 60,
                }
            )
        if p.self_esteem <= 20:
            alerts.append(
                {
                    "agent_id": agent_id,
                    "agent_name": agent.name,
                    "type": "autostima_critica",
                    "severity": "warning",
                    "message": f"Autostima al minimo: {p.self_esteem}%",
                    "value": p.self_esteem,
                    "threshold": 20,
                }
            )

        # Burnout imminente (combinazione di fattori)
        if p.stress >= 70 and p.health <= 30 and p.energy <= 30:
            alerts.append(
                {
                    "agent_id": agent_id,
                    "agent_name": agent.name,
                    "type": "burnout_imminente",
                    "severity": "critical",
                    "message": f"Burnout imminente! Stress:{p.stress} Salute:{p.health} Energia:{p.energy}",
                    "value": round(
                        (p.stress + (100 - p.health) + (100 - p.energy)) / 3
                    ),
                    "threshold": 70,
                }
            )

        # Trend anomalo (peggioramento rapido)
        history = agent.engine.stats_history
        if len(history) >= 5:
            recent_stress = [s.get("stress", 0) for s in history[-5:]]
            if recent_stress[-1] - recent_stress[0] > 15:
                alerts.append(
                    {
                        "agent_id": agent_id,
                        "agent_name": agent.name,
                        "type": "trend_stress_rapido",
                        "severity": "warning",
                        "message": f"Incremento stress rapido: +{recent_stress[-1] - recent_stress[0]} in 5 turni",
                        "value": recent_stress[-1] - recent_stress[0],
                        "threshold": 15,
                    }
                )

        return alerts

    def get_history(self) -> List[Dict]:
        return self._alert_history[-100:]


class Reports:
    """
    Reportistica avanzata per analisi HR.
    Genera report testuali e strutturati.
    """

    def __init__(self, swarm: Optional[AgentSwarm] = None):
        self.swarm = swarm

    def generate_report(self, report_type: str = "summary") -> Dict:
        if not self.swarm:
            return {"error": "No swarm attached"}
        if report_type == "summary":
            return self._summary_report()
        elif report_type == "hr_dss":
            return self._hr_dss_report()
        elif report_type == "turnover_risk":
            return self._turnover_risk_report()
        return {}

    def _summary_report(self) -> Dict:
        analytics = self.swarm.get_swarm_analytics()
        return {
            "type": "summary",
            "timestamp": __import__("datetime").datetime.now().isoformat(),
            "total_agents": analytics.get("total_decisions", 0),
            "avg_stress": analytics.get("avg_stress", 0),
            "alive_count": analytics.get("alive_count", 0),
            "profile_impact": analytics.get("profile_impact", {}),
            "archetype_avg_stress": analytics.get("archetype_avg_stress", {}),
        }

    def _hr_dss_report(self) -> Dict:
        if not self.swarm.agents:
            return {}
        total = len(self.swarm.agents)
        alive = sum(
            1
            for a in self.swarm.agents.values()
            if a.engine and a.engine.player.is_alive
        )
        avg_stress = (
            sum(a.engine.player.stress for a in self.swarm.agents.values() if a.engine)
            / total
            if total
            else 0
        )
        avg_energy = (
            sum(a.engine.player.energy for a in self.swarm.agents.values() if a.engine)
            / total
            if total
            else 0
        )

        profile_breakdown = {}
        for a in self.swarm.agents.values():
            pn = a.profile.name
            if pn not in profile_breakdown:
                profile_breakdown[pn] = {
                    "count": 0,
                    "stress": [],
                    "energy": [],
                    "days": [],
                }
            profile_breakdown[pn]["count"] += 1
            if a.engine:
                profile_breakdown[pn]["stress"].append(a.engine.player.stress)
                profile_breakdown[pn]["energy"].append(a.engine.player.energy)
                profile_breakdown[pn]["days"].append(a.engine.player.days_survived)

        return {
            "type": "hr_dss",
            "timestamp": __import__("datetime").datetime.now().isoformat(),
            "workforce_health": {
                "avg_stress": round(avg_stress, 1),
                "avg_energy": round(avg_energy, 1),
                "alive_ratio": round(alive / total * 100, 1) if total else 0,
                "total_agents": total,
            },
            "profile_breakdown": {
                name: {
                    "count": d["count"],
                    "avg_stress": round(sum(d["stress"]) / len(d["stress"]), 1)
                    if d["stress"]
                    else 0,
                    "avg_energy": round(sum(d["energy"]) / len(d["energy"]), 1)
                    if d["energy"]
                    else 0,
                    "avg_survival": round(sum(d["days"]) / len(d["days"]), 1)
                    if d["days"]
                    else 0,
                }
                for name, d in profile_breakdown.items()
            },
            "recommendations": self._generate_recommendations(
                avg_stress, avg_energy, alive, total
            ),
        }

    def _turnover_risk_report(self) -> Dict:
        risks = []
        for agent_id, agent in self.swarm.agents.items():
            if not agent.engine:
                continue
            p = agent.engine.player
            # Fattori di rischio turnover
            turnover_score = 0
            factors = []
            if p.stress > 70:
                turnover_score += 30
                factors.append("stress_cronico")
            if p.manager_rep < 20:
                turnover_score += 25
                factors.append("rapporto_manager_danneggiato")
            if p.employability > 70:
                turnover_score += 20
                factors.append("alta_occupabilita_esterna")
            if p.self_esteem < 20:
                turnover_score += 15
                factors.append("autostima_distrutta")
            if p.integrity > 70 and p.factions.get("Fedelissimi", 0) < 30:
                turnover_score += 10
                factors.append("integrita_compromessa")
            risks.append(
                {
                    "agent_id": agent_id,
                    "name": agent.name,
                    "profile": agent.profile.name,
                    "turnover_risk": min(100, turnover_score),
                    "factors": factors,
                    "days_survived": p.days_survived,
                }
            )
        risks.sort(key=lambda x: -x["turnover_risk"])
        return {
            "type": "turnover_risk",
            "timestamp": __import__("datetime").datetime.now().isoformat(),
            "high_risk_count": sum(1 for r in risks if r["turnover_risk"] > 60),
            "risk_distribution": {
                "low": sum(1 for r in risks if r["turnover_risk"] <= 30),
                "medium": sum(1 for r in risks if 30 < r["turnover_risk"] <= 60),
                "high": sum(1 for r in risks if r["turnover_risk"] > 60),
            },
            "rankings": risks[:10],
        }

    def _generate_recommendations(
        self, avg_stress: float, avg_energy: float, alive: int, total: int
    ) -> List[str]:
        recs = []
        if avg_stress > 65:
            recs.append(
                "CRITICO: Stress medio superiore a 65%. Intervento HR immediato richiesto."
            )
        elif avg_stress > 50:
            recs.append(
                "ATTENZIONE: Stress medio elevato. Valutare programmi di welfare aziendale."
            )
        if avg_energy < 40:
            recs.append(
                "CRITICO: Energia media insufficiente. Ridurre carichi di lavoro."
            )
        if alive / total < 0.5:
            recs.append(
                "CRITICO: Meno del 50% degli agenti sopravvive. Revisione culturale necessaria."
            )
        if not recs:
            recs.append(
                "OK: Parametri ambientali nella norma. Monitoraggio consigliato."
            )
        return recs

    def get_agent_report(self, agent_id: str) -> Optional[Dict]:
        if not self.swarm or agent_id not in self.swarm.agents:
            return None
        agent = self.swarm.agents[agent_id]
        if not agent.engine:
            return None
        p = agent.engine.player
        return {
            "name": agent.name,
            "profile": agent.profile.name,
            "company_type": agent.company_type,
            "stats": p.to_dict()["stats"],
            "tags": dict(p.tags),
            "achievements": list(p.achievements),
            "days_survived": p.days_survived,
            "status": p.status,
            "total_decisions": agent.total_decisions,
            "auto_decisions": agent.auto_decisions,
            "possession_count": len(agent.possession_history),
            "strategic_analysis": __import__(
                "engine.analysis", fromlist=["StrategicAnalyzer"]
            ).StrategicAnalyzer.analyze_agent(agent),
        }


class TimelineViewer:
    """
    Visualizzatore della timeline delle decisioni e degli eventi.
    """

    def __init__(self, swarm: Optional[AgentSwarm] = None):
        self.swarm = swarm

    def get_timeline(self, agent_id: Optional[str] = None) -> List[Dict]:
        if not self.swarm:
            return []
        if agent_id:
            if agent_id not in self.swarm.agents:
                return []
            agent = self.swarm.agents[agent_id]
            return self._agent_timeline(agent)
        # Timeline globale
        timeline = []
        for agent in self.swarm.agents.values():
            timeline.extend(self._agent_timeline(agent))
        timeline.sort(key=lambda x: (x["day"], x["agent_name"]))
        return timeline[-100:]

    def _agent_timeline(self, agent) -> List[Dict]:
        entries = []
        for d in agent.memory.decisions:
            entries.append(
                {
                    "agent_id": agent.agent_id,
                    "agent_name": agent.name,
                    "profile": agent.profile.name,
                    "day": d.day,
                    "event_id": d.event_id,
                    "choice_text": d.choice_text,
                    "category": d.category,
                    "was_auto": d.was_auto,
                }
            )
        return entries

    def get_swarm_timeline(self) -> List[Dict]:
        return self.get_timeline()

    def get_events_by_day(self, day: int) -> List[Dict]:
        return [e for e in self.get_timeline() if e.get("day") == day]
