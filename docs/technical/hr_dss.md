# HR Decision Support System (DSS) - Technical Documentation

## Overview
The **BurnoutSimulator v3.2** functions as an Agent-Based Modeling (ABM) engine that generates longitudinal data to support HR strategic decisions. The system tracks the evolution of an "Agent Swarm" over time, providing predictive insights into organizational risk (Burnout, Churn, Toxic Culture).

## Longitudinal Data Tracking
The DSS relies on the `swarm_history` table in the SQLite database, which records snapshots of the swarm state at every simulation step:
- **Profile Distribution**: A JSON mapping of agent profile names to their current count in the swarm.
- **Average Stats**: Global metrics (Stress, Energy, Manager Rep) to identify macro-trends.

## Dynamic Visualization (ECharts)
The Laboratory Dashboard uses **ECharts** to render a stacked area chart of profile evolution. This visualization allows management to see:
1. **Dominance Shift**: Which agent archetypes are expanding (e.g., Cynics) and which are being displaced (e.g., Idealists).
2. **Systemic Resilience**: If "The Survivor" profile becomes dominant, it indicates an organization in "maintenance mode" with zero innovation potential.
3. **Biodiversity Loss**: A collapse in the variety of profiles is a leading indicator of upcoming mass churn.

## Performance Analytics
The **Report Finale** uses a statistical approach to identify outliers:
- **Top Performer**: An agent is flagged as a "Top Performer" if their `days_survived` is significantly higher (>20%) than the average survival of agents with the same psychometric profile. This identifies individuals with "informal resilience" factors.
- **Decision Categorization**: Decisions are classified into `COMPLIANCE`, `RESISTANCE`, `NEGOTIATION`, and `ESCAPE`. The DSS correlates these categories with environmental toxicity parameters to predict how policy changes (e.g., increasing transparency) will shift the ratio of Resistance vs. Compliance.

## HR Training Parameters
The simulation can be calibrated using four key sliders:
- **Environmental Toxicity**: Increases the baseline stress impact of all events.
- **Resource Pressure**: Accelerates energy depletion during mini-events.
- **Social Support**: Modulates the "Peer Influence" logic, reducing stress for agents aligned with the dominant faction.
- **Transparency**: Reduces the "Fear" impact of management actions and improves trust recovery.

## Implementation Details
- **Backend**: `game/engine.py` manages the state machine and stat modulation.
- **Frontend**: `app.py` uses NiceGUI for the reactive dashboard and ECharts for high-performance data rendering.
- **Database**: `database/agent_db.py` handles persistent storage of swarm history.
