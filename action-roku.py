#!/usr/bin/env python3
# -*-: coding utf-8 -*-

import sys

from hermes_demo_helper.lang_config import Lang_config
from hermes_demo_helper.snipsTools import SnipsConfigParser
from hermes_demo_helper.hermes_demo_helper import SnipsFlow
from snipsroku.clientMPU import flow
from snipsroku.snipsroku import SnipsRoku

CONFIG_INI = "config.ini"

config = SnipsConfigParser.read_configuration_file(CONFIG_INI).get('global')
config_s = SnipsConfigParser.read_configuration_file(CONFIG_INI).get('secret')

MQTT_ADDR_LOCAL_HOST = str(config.get('addr_local_host', 'localhost'))
MQTT_ADDR_LOCAL_PORT = str(config.get('addr_local_port', '1883'))
MQTT_ADDR_LOCAL = "{}:{}".format(MQTT_ADDR_LOCAL_HOST, MQTT_ADDR_LOCAL_PORT)

lang_config = Lang_config(config.get('resources'))

roku_ip = config_s.get("roku_device_ip")

roku_player = None
try:
    roku_player = SnipsRoku(roku_device_ip=roku_ip)
except:
    print("fail to connect to ROKU")
    sys.exit(1)

if __name__ == "__main__":
    flow.set_host(MQTT_ADDR_LOCAL)
    flow.set_lang_config(lang_config)
    flow.set_data(roku_player=roku_player)
    flow.start(loop=True)