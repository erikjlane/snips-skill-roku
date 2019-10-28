
from hermes_demo_helper.hermes_demo_helper import SnipsFlow
flow = SnipsFlow()

@flow.intent(intent="play_content", slots=("media_provider", "season", "media_content"), data=("roku_player"))
def play_content(media_provider, season, media_content, roku_player):
    try:
        roku_player.search_content(content_type=None,
                                        keyword=media_content,
                                        title=None,
                                        launch=True,
                                        provider=media_provider,
                                        season=season)
    except ValueError as e:
        return e
    return flow.end_session()

@flow.intent(intent="search_content", slots=("content_type", "search_keyword"), data=("roku_player"))
def search_content(content_type, search_keyword, roku_player):
    roku_player.search_content(content_type, search_keyword)
    return flow.end_session()

@flow.intent(intent="go_home", data=("roku_player"))
def go_home(roku_player):
    roku_player.home_screen()
    return flow.end_session()

@flow.intent(intent="launch_app", slots=("app_name"), data=("roku_player"))
def launch_app(app_name, roku_player):
    app_id = roku_player.get_app_id(app_name)
    roku_player.launch_app(app_id)
    return flow.end_session()

@flow.on_continue(intent="tv_play", data=("roku_player"))
@flow.intent(intent="tv_play", data=("roku_player"))
def tv_play(roku_player):
    roku_player.play()
    return flow.end_session()

@flow.intent(intent="tv_pause", data=("roku_player"))
def tv_pause(roku_player):
    roku_player.pause()
    return flow.end_session()

@flow.intent(intent="tv_forward", data=("roku_player"))
def tv_forward(roku_player):
    roku_player.forward()
    return flow.continue_session(
        [tv_play],
        "",
        not_recognized_func,
        timeout=10,
        sound_feedback=False)

@flow.intent(intent="tv_reverse", data=("roku_player"))
def tv_reverse(roku_player):
    roku_player.reverse()
    return flow.continue_session(
        [tv_play],
        "",
        not_recognized_func,
        timeout=10,
        sound_feedback=False)

@flow.not_recognized("roku_player")
def not_recognized_func(roku_player):
    roku_player.play()
    return ""