import reflex as rx
from engine.psych_engine import PsychologicalProfile

class State(rx.State):
    """The app state."""
    # Using rx.Base for nested structures would be better,
    # but for simplicity we'll manage properties directly or via dicts
    stress_level: float = 0.0
    openness: float = 50.0
    conscientiousness: float = 50.0
    extraversion: float = 50.0
    agreeableness: float = 50.0
    neuroticism: float = 50.0

    def increment_stress(self):
        self.stress_level = min(100.0, self.stress_level + 10.0)

    @rx.var
    def radar_data(self) -> list[dict]:
        return [
            {"subject": "Openness", "A": self.openness},
            {"subject": "Conscientiousness", "A": self.conscientiousness},
            {"subject": "Extraversion", "A": self.extraversion},
            {"subject": "Agreeableness", "A": self.agreeableness},
            {"subject": "Neuroticism", "A": self.neuroticism},
        ]

def index() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.heading("BurnoutSimulator v3.0", size="9"),
            rx.text("Simulation Behavioral Platform", color_scheme="gray"),
            rx.divider(),
            rx.heading("Psychological State", size="5"),
            rx.text(f"Stress Level: {State.stress_level}%"),
            rx.progress(value=State.stress_level, max=100, width="100%"),
            rx.button("Simulate Stress", on_click=State.increment_stress),
            rx.divider(),
            rx.heading("Big Five Profile", size="5"),
            rx.list(
                rx.list_item(f"Openness: {State.openness}"),
                rx.list_item(f"Conscientiousness: {State.conscientiousness}"),
                rx.list_item(f"Extraversion: {State.extraversion}"),
                rx.list_item(f"Agreeableness: {State.agreeableness}"),
                rx.list_item(f"Neuroticism: {State.neuroticism}"),
            ),
            align="center",
            spacing="5",
        ),
        padding="2em",
        height="100vh",
    )

app = rx.App()
app.add_page(index)
