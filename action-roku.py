#!/usr/bin/env python2
# -*-: coding utf-8 -*-

import ConfigParser
from hermes_python.hermes import Hermes
import io
from snipsroku.snipsroku import SnipsRoku

CONFIGURATION_ENCODING_FORMAT = "utf-8"
CONFIG_INI = "config.ini"

MQTT_IP_ADDR = "localhost"
MQTT_PORT = 1883
MQTT_ADDR = "{}:{}".format(MQTT_IP_ADDR, str(MQTT_PORT))

class SnipsConfigParser(ConfigParser.SafeConfigParser):
    def to_dict(self):
        return {section: {option_name : option for option_name, option in self.items(section)} for section in self.sections()}

def read_configuration_file(configuration_file):
    try:
        with io.open(configuration_file,
                     encoding=CONFIGURATION_ENCODING_FORMAT) as f:
            conf_parser = SnipsConfigParser()
            conf_parser.readfp(f)
            return conf_parser.to_dict()
    except (IOError, ConfigParser.Error) as e:
        return dict()

def playContent(hermes, intent_message):
    media_provider = None
    season = None
    if hermes.slots.mediaProvider is not None:
        media_provider = hermes.slots.mediaProvider.first().value
    if hermes.slots.season is not None:
        season = hermes.skill.parse_season(hermes.slots.season.first().value)
    if hermes.slots.mediaContent is not None:
        media_content = hermes.slots.mediaContent.first().value
    try:
        hermes.skill.search_content(None, media_content, None, True,
                                    media_provider, season)
    except ValueError as e:
        hermes.publish_end_session(intent_message.session_id, e.message)
    else:
        hermes.publish_end_session(intent_message.session_id, e.message)

def searchContent(hermes, intent_message):
    hermes.publish_end_session(intent_message.session_id, "")
    content_type = None
    keyword = None
    if hermes.slots.contentType is not None:
        content_type = hermes.slots.contentType.first().value
    if hermes.slots.contentType is not None:
        keyword = hermes.slots.searchKeyword.first().value
        hermes.skill.search_content(content_type, keyword)

def goHome(hermes, intent_message):
    hermes.publish_end_session(intent_message.session_id, "")
    hermes.skill.home_screen()

def launchApp(hermes, intent_message):
    hermes.publish_end_session(intent_message.session_id, "")
    if hermes.slots.appName is not None:
        app_name = hermes.slots.appName.first().value
        app_id = hermes.skill.get_app_id(app_name)
        hermes.skill.launch_app(app_id)

def tvPlay(hermes, intent_message):
    hermes.publish_end_session(intent_message.session_id, "")
    hermes.skill.play()

if __name__ == "__main__":
    config = read_configuration_file("config.ini")
    skill_locale = config.get("global", {"locale":"en_US"}).get("locale", u"en_US")
    roku_ip = config.get("secret").get("roku_device_ip")
    with Hermes(MQTT_ADDR) as h:
        h.skill = SnipsRoku(roku_device_ip=roku_ip, locale=skill_locale)
        h.subscribe_intent("tvPlay", tvPlay) \
                .subscribe_intent("tvPause", tvPlay) \
                .subscribe_intent("launchApp", launchApp) \
                .subscribe_intent("goHome", goHome) \
                .subscribe_intent("searchContent", searchContent) \
                .subscribe_intent("playContent", playContent) \
                .loop_forever()
