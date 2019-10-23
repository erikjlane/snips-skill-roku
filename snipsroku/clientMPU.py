#!/usr/bin/env python3
# -*-: coding utf-8 -*-

from hermes_demo_helper.hermes_demo_helper import ClientAction
from hermes_demo_helper.hermes_demo_helper import is_simple_intent_callback



class ClientMPU(ClientAction):
    def __init__(self, mqtt_addr, lang_config, roku_player):
        ClientAction.__init__(self, mqtt_addr, lang_config)
        # init intent subscribe
        intent_funcs = [
            (self.play_content, "play_content"),
            (self.search_content, "search_content"),
            (self.go_home, "go_home"),
            (self.launch_app, "launch_app"),
            (self.tv_play, "tv_play"),
            (self.tv_pause, "tv_pause")
        ]
        for intent_func in intent_funcs:
            self.register_handler(intent_func[0],intent_func[1])
        self.roku_player = roku_player

    @is_simple_intent_callback
    def play_content(self, hermes, intent_message):
        media_provider = self.extract_value(intent_message, "media_provider")
        season = self.extract_value(intent_message, "season")
        media_content = self.extract_value(intent_message, "media_content")
        try:
            self.roku_player.search_content(content_type=None,
                                            keyword=media_content,
                                            title=None,
                                            launch=True,
                                            provider=media_provider,
                                            season=season)
        except ValueError as e:
            return e
        return ""

    @is_simple_intent_callback
    def search_content(self, hermes, intent_message):
        content_type = self.extract_value(intent_message, "content_type")
        keyword = self.extract_value(intent_message, "search_keyword")
        self.roku_player.search_content(content_type, keyword)
        return ""
 
    @is_simple_intent_callback
    def go_home(self, hermes, intent_message):
        self.roku_player.home_screen()
        return ""
 
    @is_simple_intent_callback
    def launch_app(self, hermes, intent_message):
        app_name = self.extract_value(intent_message, "app_name")
        app_id = self.roku_player.get_app_id(app_name)
        self.roku_player.launch_app(app_id)
        return ""
  
    @is_simple_intent_callback
    def tv_play(self, hermes, intent_message):
        self.roku_player.play()
        return ""
    
    @is_simple_intent_callback
    def tv_pause(self, hermes, intent_message):
        self.roku_player.pause()
        return ""
