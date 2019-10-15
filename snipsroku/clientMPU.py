#!/usr/bin/env python3
# -*-: coding utf-8 -*-

from hermes_demo_helper.hermes_demo_helper import *

class ClientMPU(ClientAction):
    def __init__(self, mqtt_addr, lang_config, roku_player):
        ClientAction.__init__(self, mqtt_addr, lang_config)
        #init intent subscribe 
        self.intent_funcs = [
            (self.playContent, "play_content"),
            (self.searchContent, "search_content"),
            (self.goHome, "go_home"),
            (self.launchApp, "launch_app"),
            (self.tvPlay, "tv_play"),
            (self.tvPause, "tv_pause")
        ]
        self.roku_player = roku_player

    @is_simple_intent_callback
    def playContent(self, hermes, intent_message):
        media_provider = self.extract_value(intent_message, "media_provider")
        season = self.extract_value(intent_message, "season")
        media_content = self.extract_value(intent_message, "media_content")
        try:
            self.roku_player.search_content(None, media_content, None, True,
                    media_provider, season)
        except ValueError as e:
            return e.message
        return ""
    @is_simple_intent_callback
    def searchContent(self, hermes, intent_message):
        content_type = self.extract_value(intent_message, "content_type")
        keyword = self.extract_value(intent_message, "search_keyword")
        self.roku_player.search_content(content_type, keyword)
        return ""
 
    @is_simple_intent_callback
    def goHome(self, hermes, intent_message):
        self.roku_player.home_screen()
        return ""
 
    @is_simple_intent_callback
    def launchApp(self, hermes, intent_message):
        app_name = self.extract_value(intent_message, "app_name")
        app_id = self.roku_player.get_app_id(app_name)
        self.roku_player.launch_app(app_id)
        return ""
  
    @is_simple_intent_callback
    def tvPlay(self, hermes, intent_message):
        self.roku_player.play()
        return ""
    
    @is_simple_intent_callback
    def tvPause(self, hermes, intent_message):
        self.roku_player.pause()
        return ""
