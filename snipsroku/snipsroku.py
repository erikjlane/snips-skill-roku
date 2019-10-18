#!/usr/local/bin/python
# -*-: coding utf-8 -*-
import requests
import re
import xml.etree.ElementTree as ET
from roku import Roku

class SnipsRoku:

    def __init__(self, roku_device_ip=None):
        if roku_device_ip is None:
            devices = Roku.discover()
            self.device = None
            for device in devices:
                try:
                    device.home()
                    self.device = device
                    roku_device_ip = device.host
                except:
                    pass
            if self.device is None:
                raise ValueError('You need to provide a Roku device IP')
        else:
            self.device = Roku(roku_device_ip)
            try:
                self.device.home()
            except:
                raise ValueError('You need to provide a Roku device IP')
        print("connected to ROKU device on: " + roku_device_ip)
        self.roku_device_ip = roku_device_ip
        self.apps = {}
        self.apps_string_list = ""
        self._is_playing = False

    def set_available_apps(self):
        r = requests.get(
            "http://{}:8060/query/apps".format(self.roku_device_ip))

        parsed_data = ET.fromstring(r.content)
        apps_array = []
        for app in parsed_data:
            self.apps[app.text.lower()] = app.attrib['id']
            apps_array.append(app.text)

        # comma separated list of providers to use when automatically launching content
        self.apps_string_list = ",".join(apps_array)

    def get_apps(self):
        return self.apps

    def launch_app(self, app_id):
        self._is_playing = False
        requests.post(
            "http://{}:8060/launch/{}".format(self.roku_device_ip, app_id))

    def get_app_id(self, app_name):
        # we call set_available_apps every time just in case new apps have been installed
        self.set_available_apps()
        return self.apps.get(app_name.lower())

    def search_content(self, content_type, keyword=None, title=None, launch=False, provider=None,
                       season=None):
        """
        :param content_type: tv-show, movie, persona, channel or game
        :param keyword: Keyword contained in movie or serie title, person name, channel name or game
        :param title: Exact content title, channel name, person name, or keyword. Case sensitive.
        :param launch: When true it automatically launches the selected content. True or false have
        to be string literals
        :param provider: The name of the provider where to launch the content. Case sensitive and
        :param season: The season of the series you the user wants to watch
        """
        self._is_playing = True
        
        payload = {'type': content_type, 'launch': SnipsRoku.bool2string(launch),
                                               'season': SnipsRoku.parse_season(season)}

        # when launching pick the first content and provider available if not specified
        if launch:
            payload['match-any'] = 'true'
            if provider is None:
            # we call set_available_apps every time just in case new apps have been installed
                self.set_available_apps()
                payload['provider'] = self.apps_string_list
            else:
                payload['provider'] = provider

        if title is not None:
            payload['title'] = title
        elif keyword is not None:
            payload['keyword'] = keyword
        else:
            raise ValueError('Either keyword or title need to be specified')
        requests.post(
            "http://{}:8060/search/browse?".format(self.roku_device_ip), params=payload)

    def play(self):
        if self._is_playing:
            return
        self.device.play()
        self._is_playing = True

    def pause(self):
        if not self._is_playing:
            return
        self.device.play()
        self._is_playing = False
    
    def home_screen(self):
        self._is_playing = False
        self.device.home()

    @staticmethod
    def parse_season(season_string):
        """
        Return the season as integer. It expects a string with the structure
        string literal 'season' + ordinal number. Example season 10
        :param season_string:
        :return: integer
        """
        if(season_string is None):
            return None
        p = re.compile('\d+')
        match = p.findall(season_string)
        if match:
            return int(match[0])
        return None

    @staticmethod
    def bool2string(boolean):
        if boolean:
            return 'true'
        else:
            return 'false'
