from nicegui import ui

from ui.pages.questionnaire_page import render_questionnaire
from ui.pages.logic import play_again
import game.state as state

def page(screen, render_start, render_laboratory, render_game, render_tutorial, render_game_over, render_analytics, on_start_cb, show_help, show_config, go_analytics, _tutorial_active):
    if screen == "start":
        render_start(on_start_cb, show_help, show_config, go_analytics)
    elif screen == "questionnaire_pre":
        render_questionnaire("PRE", on_complete=on_start_cb)
    elif screen == "questionnaire_post":
        render_questionnaire("POST", on_complete=lambda: setattr(state, "screen", "game_over"))
    elif screen == "laboratory":
        render_laboratory()
    elif screen == "game":
        render_game()
        if _tutorial_active:
            render_tutorial()
    elif screen == "game_over":
        render_game_over()
    elif screen == "analytics":
        render_analytics()
