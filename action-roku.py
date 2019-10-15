#!/usr/bin/env python3
# -*-: coding utf-8 -*-

from snipsroku.snipsroku import SnipsRoku
from snipsroku.clientMPU import ClientMPU
from hermes_demo_helper import *

CONFIG_INI = "config.ini"

config = SnipsConfigParser.read_configuration_file(CONFIG_INI).get('global')
config_s = SnipsConfigParser.read_configuration_file(CONFIG_INI).get('secret')

MQTT_ADDR_LOCAL_HOST = str(config.get('addr_local_host', 'localhost'))
MQTT_ADDR_LOCAL_PORT = str(config.get('addr_local_port', '1883'))
MQTT_ADDR_LOCAL = "{}:{}".format(MQTT_ADDR_LOCAL_HOST, MQTT_ADDR_LOCAL_PORT)

lang_config = Lang_config(config.get('ressources'))

roku_ip = config_s.get("roku_device_ip")
roku_player = SnipsRoku(roku_device_ip=roku_ip)

#Default configuration
clientLocal = ClientMPU(MQTT_ADDR_LOCAL, lang_config, roku_player)

if __name__ == "__main__":
    try:
        clientLocal.start()
        while True:
            pass
    except KeyboardInterrupt:
        print("Please force to kill this process!")
