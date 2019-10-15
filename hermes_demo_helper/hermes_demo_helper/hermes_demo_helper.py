#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import json
import random
import functools
import threading
from hermes_python.ffi import LibException
from hermes_python.hermes import Hermes
import time

def is_simple_intent_callback(_func):
    def decorator_check(func):
        @functools.wraps(func)
        def wrapper_check(self, hermes, intent_message):
            confidence_score = intent_message.intent.confidence_score
            threshold_1 = self.config.intents.get_threshold("intentBad")
            threshold_2 = self.config.intents.get_threshold("intentGood")
            tts = ""
            if confidence_score > threshold_1:
                if confidence_score > threshold_2:
                    tts = func(self, hermes, intent_message)
                else:
                    tts = self.config.tts.get_value("ErrorIntentBad")
            else:
                tts = self.config.tts.get_value("ErrorIntentGood")
            hermes.publish_end_session(intent_message.session_id, tts)
        return wrapper_check
    if _func is None:
        return decorator_check
    return decorator_check(_func)

class ClientAction(threading.Thread):

    def __init__(self, mqtt_addr, lang_config):
        threading.Thread.__init__(self)
        self.__mqtt_addr = mqtt_addr
        self.config = lang_config
    
    def extract_defaults(self, intent_message, slot_name):
            result = []
            threshold = self.config.slots.get_threshold(slot_name)
            slot_name = self.config.slots.get_value(slot_name)
            if (intent_message.slots is not None):
                for i in intent_message.slots[slot_name]:
                    if i.confidence_score > threshold:
                        result.append(i.slot_value.value)
            return result
    
    def extract_default(self, intent_message, slot_name):
        res = self.extract_defaults(intent_message, slot_name)
        if (res is None or len(res) == 0):
            return None
        return res[0]

    def extract_values(self, intent_message, slot_name):
            result = []
            threshold = self.config.slots.get_threshold(slot_name)
            slot_name = self.config.slots.get_value(slot_name)
            if (intent_message.slots is not None):
                for i in intent_message.slots[slot_name]:
                    if i.confidence_score > threshold:
                        result.append(i.slot_value.value.value)
            return result
    
    def extract_value(self, intent_message, slot_name):
        res = self.extract_values(intent_message, slot_name)
        if (res is None or len(res) == 0):
            return None
        return res[0]
    
    def run(self):
        while 1:
            try:
                with Hermes(self.__mqtt_addr) as h:
                    for i in self.intent_funcs:
                        for name in self.config.intents.get_intent(i[1]):
                            h.subscribe_intent(name, i[0])
                            print("subscribe to {}".format(name))
                    for site_id in ["default", "cortex_00_2", "cortex_40_2"]:
                        h.publish_start_session_notification(site_id,
                                self.config.tts.get_value("Ready"), None)
                    print("connected to: {}".format(self.__mqtt_addr))
                    h.start()
            except LibException:
                print("could not connect to broker: {}".format(self.__mqtt_addr))
                time.sleep(60)
