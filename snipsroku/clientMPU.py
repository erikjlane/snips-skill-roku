
from hermes_demo_helper.hermes_demo_helper import SnipsFlow, ContinueObject
flow = SnipsFlow()

@flow.intent("play_content", "media_provider", "season", "media_content", "roku_player")
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
    return ""

@flow.intent("search_content", "content_type", "search_keyword", "roku_player")
def search_content(content_type, search_keyword, roku_player):
    roku_player.search_content(content_type, search_keyword)
    return ""

@flow.intent("go_home", "roku_player")
def go_home(roku_player):
    roku_player.home_screen()
    return ""

@flow.intent("launch_app", "roku_player", "app_name")
def launch_app(app_name, roku_player):
    app_id = roku_player.get_app_id(app_name)
    roku_player.launch_app(app_id)
    return ""

@flow.intent_on_continue("tv_play", "roku_player")
@flow.intent("tv_play", "roku_player")
def tv_play(roku_player):
    roku_player.play()
    return ""

@flow.intent("tv_pause", "roku_player")
def tv_pause(roku_player):
    roku_player.pause()
    return ""

@flow.intent_with_continue("tv_forward", "roku_player")
def tv_forward(roku_player):
    roku_player.forward()
    return ContinueObject(
        [tv_play],
        "",
        not_recognized_func,
        nb_second=10,
        sound_feedback=False)

@flow.intent_with_continue("tv_reverse", "roku_player")
def tv_reverse(roku_player):
    roku_player.reverse()
    return ContinueObject(
        [tv_play],
        "",
        not_recognized_func,
        nb_second=10,
        sound_feedback=False)
@flow.not_recognized("roku_player")
def not_recognized_func(roku_player):
    roku_player.play()