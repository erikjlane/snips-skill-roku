#!/usr/local/bin/python
# -*-: coding utf-8 -*-
import requests
import re
import xml.etree.ElementTree as ET


class SnipsRoku:

    def __init__(self, roku_device_ip=None, locale=None):
        if roku_device_ip is None:
            raise ValueError('You need to provide a Roku device IP')
        self.roku_device_ip = roku_device_ip
        self.apps = {}
        self.apps_string_list = ""

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
        requests.post(
            "http://{}:8060/launch/{}".format(self.roku_device_ip, app_id))

    def get_app_id(self, app_name):
        # we call set_available_apps every time just in case new apps have been installed
        self.set_available_apps()
        return self.apps[app_name.lower()]

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

        payload = {'type': content_type, 'launch': SnipsRoku.bool2string(launch),
                   'season': season}

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
        requests.post(
            "http://{}:8060/keypress/Play".format(self.roku_device_ip))

    def home_screen(self):
        requests.post(
            "http://{}:8060/keypress/Home".format(self.roku_device_ip))

    @staticmethod
    def parse_season(season_string):
        """
        Return the season as integer. It expects a string with the structure
        string literal 'season' + ordinal number. Example season 10
        :param season_string:
        :return: integer
        """
        p = re.compile('\d+')
        match = p.findall(season_string)
        if match:
            return int(match[0])
        return None

    @staticmethod
    def bool2string(boolean):
        if boolean:
            return 'true'
        elif boolean is False:
            return 'false'
        else:
            return 'false'
