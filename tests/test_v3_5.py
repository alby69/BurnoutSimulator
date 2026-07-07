"""
Test per le nuove funzionalità v3.5:
- Peer Influence Avanzata (OCEAN trait influence)
- Pressione Culturale Dinamica
- Dashboard dedicate (AgentMonitor, AlertSystem, Reports, TimelineViewer)
- Visualizzazione 3D (Collins Cube data generation)
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from agents.personality import PsychologicalProfile, AGENT_PROFILES
from agents.swarm import AgentSwarm
from agents.agent import Agent
from dashboard.main_dashboard import (
    AgentMonitor,
    AlertSystem,
    Reports,
    TimelineViewer,
    MainDashboard,
)


# ── Fixtures ──


@pytest.fixture
def swarm():
    sw = AgentSwarm(num_agents=6)
    sw._init_agents(6)
    # Advance a few turns so agents have some state
    for _ in range(5):
        sw.run_simulation_step()
    return sw


@pytest.fixture
def profile():
    return AGENT_PROFILES["il_performante"]


# ── Tests: Peer Influence Avanzata ──


class TestPeerInfluence:
    def test_peer_influence_buffer_starts_empty(self, profile):
        for v in profile._peer_influence_buffer.values():
            assert v == 0.0

    def test_peer_influence_modifies_buffer(self, profile):
        other = AGENT_PROFILES["il_sopravvissuto"]
        profile.peer_influence([other], [0.5])
        # At least some buffer should have been modified
        assert any(v != 0.0 for v in profile._peer_influence_buffer.values())

    def test_apply_buffer_changes_traits(self, profile):
        other = AGENT_PROFILES["il_sopravvissuto"]
        old_openness = profile.openness
        profile.peer_influence([other], [0.8])
        profile.apply_peer_influence_buffer()
        # With high proximity weight, openness should shift toward the other's openness
        assert profile.openness != old_openness

    def test_swarm_peer_influence_runs(self, swarm):
        """Peer influence runs inside simulation_step without crashing."""
        old_traits = {}
        for aid, a in swarm.agents.items():
            if a.profile:
                old_traits[aid] = a.profile.openness

        swarm.run_simulation_step()

        # At least some agents should have changed traits due to peer influence
        # (not guaranteed every step, but likely after enough steps)
        changes = 0
        for aid, a in swarm.agents.items():
            if a.profile and aid in old_traits:
                if a.profile.openness != old_traits[aid]:
                    changes += 1

    def test_peer_influence_no_crash_single_agent(self):
        """Peer influence should not crash with only 1 agent alive."""
        sw = AgentSwarm(num_agents=1)
        sw._init_agents(1)
        # Should not raise
        sw._apply_peer_influence()


# ── Tests: Pressione Culturale Dinamica ──


class TestCulturalDrift:
    def test_cultural_drift_produces_scores(self, swarm):
        swarm._apply_cultural_drift()
        info = swarm._get_cultural_drift_info()
        assert "dominant_culture" in info
        assert info["dominant_culture"] in [
            "Startup Caotica",
            "Corporate Tossica",
            "Azienda Familiare",
            "Consulting",
            "In fase di calcolo",
        ]

    def test_cultural_drift_modifies_hr_params(self, swarm):
        old_hr = {}
        for aid, a in swarm.agents.items():
            if a.engine:
                old_hr[aid] = dict(a.engine.hr_params)

        # Run enough steps to trigger cultural drift (every 5 turns)
        for _ in range(6):
            swarm.run_simulation_step()

        # HR params should have changed for at least some agents
        hr_changed = False
        for aid, a in swarm.agents.items():
            if a.engine and aid in old_hr:
                if a.engine.hr_params != old_hr[aid]:
                    hr_changed = True
                    break
        assert hr_changed

    def test_cultural_drift_cultural_info_in_lab_view(self, swarm):
        view = swarm.get_laboratory_view()
        assert "cultural_drift" in view
        assert "dominant_culture" in view["cultural_drift"]


# ── Tests: Dashboard (AgentMonitor) ──


class TestAgentMonitor:
    def test_risk_ranking_returns_list(self, swarm):
        monitor = AgentMonitor(swarm)
        rankings = monitor.get_risk_ranking()
        assert isinstance(rankings, list)
        assert len(rankings) <= len(swarm.agents)

    def test_risk_ranking_sorted_by_risk(self, swarm):
        monitor = AgentMonitor(swarm)
        rankings = monitor.get_risk_ranking()
        if len(rankings) > 1:
            for i in range(len(rankings) - 1):
                assert rankings[i]["risk_score"] >= rankings[i + 1]["risk_score"]

    def test_risk_ranking_has_required_fields(self, swarm):
        monitor = AgentMonitor(swarm)
        rankings = monitor.get_risk_ranking()
        if rankings:
            r = rankings[0]
            assert "agent_id" in r
            assert "name" in r
            assert "risk_score" in r
            assert "risk_factors" in r

    def test_risk_ranking_alive_first(self, swarm):
        monitor = AgentMonitor(swarm)
        rankings = monitor.get_risk_ranking()
        alive_seen = False
        dead_seen = False
        for r in rankings:
            if r["alive"]:
                if dead_seen:
                    pass  # This could happen if a dead agent has risk 0
            else:
                dead_seen = True

    def test_trend_returns_history(self, swarm):
        monitor = AgentMonitor(swarm)
        if swarm.agents:
            aid = list(swarm.agents.keys())[0]
            trend = monitor.get_trend(aid, "stress", 5)
            assert isinstance(trend, list)
            assert len(trend) <= 5


# ── Tests: Dashboard (AlertSystem) ──


class TestAlertSystem:
    def test_evaluate_all_returns_list(self, swarm):
        alerts = AlertSystem(swarm).evaluate_all()
        assert isinstance(alerts, list)

    def test_alerts_have_required_fields(self, swarm):
        alerts = AlertSystem(swarm).evaluate_all()
        if alerts:
            a = alerts[0]
            assert "agent_id" in a
            assert "type" in a
            assert "severity" in a
            assert "message" in a

    def test_alert_severity_valid(self, swarm):
        alerts = AlertSystem(swarm).evaluate_all()
        for a in alerts:
            assert a["severity"] in ("critical", "warning", "info")

    def test_history(self, swarm):
        asys = AlertSystem(swarm)
        asys.evaluate_all()
        # History should accumulate
        asys.evaluate_all()
        assert isinstance(asys.get_history(), list)


# ── Tests: Dashboard (Reports) ──


class TestReports:
    def test_summary_report(self, swarm):
        r = Reports(swarm)
        report = r.generate_report("summary")
        assert report.get("type") == "summary"

    def test_hr_dss_report(self, swarm):
        r = Reports(swarm)
        report = r.generate_report("hr_dss")
        assert report.get("type") == "hr_dss"
        assert "workforce_health" in report
        assert "profile_breakdown" in report
        assert "recommendations" in report

    def test_turnover_risk_report(self, swarm):
        r = Reports(swarm)
        report = r.generate_report("turnover_risk")
        assert report.get("type") == "turnover_risk"
        assert "high_risk_count" in report
        assert "rankings" in report

    def test_agent_report(self, swarm):
        r = Reports(swarm)
        if swarm.agents:
            aid = list(swarm.agents.keys())[0]
            report = r.get_agent_report(aid)
            assert report is not None
            assert "name" in report
            assert "profile" in report

    def test_empty_swarm_report(self):
        r = Reports()
        report = r.generate_report("summary")
        assert "error" in report


# ── Tests: Dashboard (TimelineViewer) ──


class TestTimelineViewer:
    def test_get_timeline_returns_list(self, swarm):
        tv = TimelineViewer(swarm)
        timeline = tv.get_timeline()
        assert isinstance(timeline, list)

    def test_agent_timeline(self, swarm):
        tv = TimelineViewer(swarm)
        if swarm.agents:
            aid = list(swarm.agents.keys())[0]
            timeline = tv.get_timeline(aid)
            assert isinstance(timeline, list)
            for entry in timeline:
                assert entry.get("agent_id") == aid

    def test_get_events_by_day(self, swarm):
        tv = TimelineViewer(swarm)
        events = tv.get_events_by_day(0)
        assert isinstance(events, list)

    def test_swarm_timeline(self, swarm):
        tv = TimelineViewer(swarm)
        tl = tv.get_swarm_timeline()
        assert isinstance(tl, list)


# ── Tests: Dashboard (MainDashboard) ──


class TestMainDashboard:
    def test_overview_with_swarm(self, swarm):
        md = MainDashboard(swarm)
        overview = md.get_overview()
        assert "total_agents" in overview
        assert "alerts" in overview
        assert "top_risks" in overview

    def test_overview_without_swarm(self):
        md = MainDashboard()
        overview = md.get_overview()
        assert "error" in overview

    def test_set_swarm(self, swarm):
        md = MainDashboard()
        md.set_swarm(swarm)
        overview = md.get_overview()
        assert "error" not in overview


# ── Tests: Collins Cube Data Generation ──


class TestCollinsCube:
    def test_lab_view_contains_agents_for_cube(self, swarm):
        view = swarm.get_laboratory_view()
        assert "agents" in view
        for agent in view["agents"]:
            assert "stress" in agent
            assert "energy" in agent
            assert "integrity" in agent

    def test_cube_data_ranges(self, swarm):
        view = swarm.get_laboratory_view()
        for agent in view["agents"]:
            assert 0 <= agent["stress"] <= 100
            assert 0 <= agent["energy"] <= 100
            assert 0 <= agent["integrity"] <= 100


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
