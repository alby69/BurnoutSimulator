# HR Decision Support System (DSS) - Technical & Anthropological Documentation

## Overview
The **BurnoutSimulator v3.5** functions as an Agent-Based Modeling (ABM) engine that generates longitudinal data to support HR strategic decisions. The system tracks the evolution of an "Agent Swarm" over time, providing predictive insights into organizational risk (Burnout, Churn, Toxic Culture).

By combining psychometrics (OCEAN model + Dark Triad) with anthropological analysis of work environments, the DSS provides executive-level decision support that is qualitative, systemic, and predictive.

For detailed anthropological specifications, refer to [SPECIFICHE_DSS_ANTROPOLOGICO.md](SPECIFICHE_DSS_ANTROPOLOGICO.md).

## Longitudinal Data Tracking
The DSS relies on the `swarm_history` table in the SQLite database, which records snapshots of the swarm state at every simulation step:
- **Profile Distribution**: A JSON mapping of agent profile names to their current count in the swarm.
- **Average Stats**: Global metrics (Stress, Energy, Manager Rep) to identify macro-trends.
- **Trait Averages**: Turn-by-turn tracking of the average OCEAN and Dark Triad levels of the entire swarm.

## Dynamic Visualization (ECharts & 3D Collins Cube)
The Laboratory Dashboard uses high-performance **ECharts** widgets to render:
1. **Dominance Shift (Stacked Area / Line Chart)**: Displays how agent archetypes and average traits (e.g., Cynicism vs. Idealism) expand or collapse under different management pressures.
2. **Biodiversity Loss**: A collapse in the variety of profiles is a leading indicator of upcoming mass churn.
3. **Collins Cube 3D**: A 3D scatter chart displaying all agents mapped onto the axes of **Stress (X)**, **Energy (Y)**, and **Integrity (Z)**. It rotates automatically to help HR visualize clusters of risk and polarization within the team.

## Performance & Risk Analytics
The dashboard implements automated tracking modules located in `dashboard/main_dashboard.py`:
- **AgentMonitor (Risk Ranking)**: Analyzes stress, energy, health, self-esteem, manager reputation, and psychological vulnerability to rank agents by risk (0 to 100).
- **AlertSystem**: Continuously monitors the swarm and raises alerts (Critical, Warning, Info) for critical thresholds and rapid stress escalation (e.g., rapid stress increases of +15 in 5 turns).
- **Turnover Risk Report**: Correlates high external employability with stress and poor manager relationship to identify high-retention-risk individuals.
- **Top Performer**: An agent is flagged as a "Top Performer" if their `days_survived` is significantly higher (>20%) than the average survival of agents with the same psychometric profile. This identifies individuals with "informal resilience" factors.
- **Decision Categorization**: Decisions are classified into `COMPLIANCE`, `RESISTANCE`, `NEGOTIATION`, and `ESCAPE`. The DSS correlates these categories with environmental toxicity parameters to predict how policy changes (e.g., increasing transparency) will shift the ratio of Resistance vs. Compliance.

## HR Training Parameters & Social Physics (v3.5)
The simulation can be calibrated using four key sliders:
- **Environmental Toxicity**: Increases the baseline stress impact of all events.
- **Resource Pressure**: Accelerates energy depletion during mini-events.
- **Social Support / Cohesion**: Modulates the "Peer Influence" logic, reducing stress for agents aligned with the dominant faction.
- **Transparency / Internal Competition**: Modulates how management actions impact fear and trust recovery.

Furthermore, **Peer Influence** and **Cultural Drift** ensure that agents interact and influence each other's OCEAN traits while dynamically shifting the overall company culture and parameters, establishing a realistic feedback loop between individuals and their environment.
