
import os
import sqlite3
import json
from agents.swarm import AgentSwarm
from database.agent_db import init_agent_db, AGENT_DB_PATH

def verify_v3_1():
    print("--- Verifying BurnoutSimulator v3.1 Improvements ---")

    # 1. Reset and Init DB
    if os.path.exists(AGENT_DB_PATH):
        os.remove(AGENT_DB_PATH)
    init_agent_db()
    print("[OK] Database initialized.")

    # 2. Setup Swarm
    swarm = AgentSwarm(num_agents=3)
    print(f"[OK] Swarm initialized with {len(swarm.agents)} agents.")

    # Verify agents saved in DB
    conn = sqlite3.connect(str(AGENT_DB_PATH))
    count = conn.execute("SELECT COUNT(*) FROM agents").fetchone()[0]
    conn.close()
    print(f"[VERIFY] Agents in DB: {count}")
    assert count == 3

    # 3. Register Human
    human = swarm.register_human(name="Test Human")
    human_id = human.human_id
    print(f"[OK] Human registered: {human_id}")

    # Verify human in DB
    conn = sqlite3.connect(str(AGENT_DB_PATH))
    count = conn.execute("SELECT COUNT(*) FROM human_profiles").fetchone()[0]
    conn.close()
    print(f"[VERIFY] Humans in DB: {count}")
    assert count == 1

    # 4. First Possession
    agent_ids = list(swarm.agents.keys())
    agent_id1 = agent_ids[0]
    swarm.possess_agent(human_id, agent_id1)
    print(f"[OK] Human possessed agent {agent_id1}")

    # Verify stay duration (should be 0 since it's the first agent)
    # Actually, verify jump history
    conn = sqlite3.connect(str(AGENT_DB_PATH))
    jumps = conn.execute("SELECT from_agent_id, to_agent_id, from_day, to_day FROM human_jumps").fetchall()
    conn.close()
    print(f"[VERIFY] Jumps in DB: {len(jumps)}")
    assert len(jumps) == 1
    assert jumps[0][0] is None
    assert jumps[0][1] == agent_id1

    # 5. Make a Choice
    # Advance agent to day 1 (already at day 1 after init and next_turn)
    day_before = swarm.agents[agent_id1].engine.player.days_survived
    swarm.human_make_choice(human_id, 0)
    day_after = swarm.agents[agent_id1].engine.player.days_survived
    print(f"[OK] Choice made. Day: {day_before} -> {day_after}")

    # Verify decision in DB
    conn = sqlite3.connect(str(AGENT_DB_PATH))
    decisions = conn.execute("SELECT * FROM agent_decisions").fetchall()
    conn.close()
    print(f"[VERIFY] Decisions in DB: {len(decisions)}")
    assert len(decisions) >= 1

    # 6. Jump to another agent
    agent_id2 = agent_ids[1]
    # Simulate some days passed for agent 1
    swarm.agents[agent_id1].engine.player.days_survived = 5

    swarm.possess_agent(human_id, agent_id2)
    print(f"[OK] Jumped from {agent_id1} to {agent_id2}")

    # Verify second jump record
    conn = sqlite3.connect(str(AGENT_DB_PATH))
    jumps = conn.execute("SELECT from_agent_id, to_agent_id, from_day, to_day FROM human_jumps").fetchall()
    conn.close()
    print(f"[VERIFY] Jumps in DB: {len(jumps)}")
    assert len(jumps) == 2
    # Second jump should have from_day = 1 (joined agent1 at day 1) and to_day = 5 (left agent1 at day 5)
    print(f"[DEBUG] Jump 2: from={jumps[1][0]}, to={jumps[1][1]}, from_day={jumps[1][2]}, to_day={jumps[1][3]}")
    assert jumps[1][0] == agent_id1
    assert jumps[1][1] == agent_id2
    assert jumps[1][2] == 1 # Initial join day for agent1 was 1 (it advances to 1 on init)
    assert jumps[1][3] == 5

    # 7. Check memory outcome
    agent1 = swarm.agents[agent_id1]
    outcomes = sum(len(o) for o in agent1.memory.choice_outcomes.values())
    print(f"[VERIFY] Agent1 memory outcomes: {outcomes}")
    assert outcomes >= 1

    print("--- All Verifications Passed! ---")

if __name__ == "__main__":
    verify_v3_1()
