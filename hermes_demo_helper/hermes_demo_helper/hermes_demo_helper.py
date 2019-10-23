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
            if confidence_score <= threshold_1:
                tts = self.config.tts.get_value("ErrorIntentGood")
            elif confidence_score <= threshold_2:
                tts = self.config.tts.get_value("ErrorIntentBad")
            else:
                tts = func(self, hermes, intent_message)
            hermes.publish_end_session(intent_message.session_id, tts)
        return wrapper_check
    if _func is None:
        return decorator_check
    return decorator_check(_func)

class ContinueObject():
    def __init__(self, intent_funcs, tts, not_recognized_func=None, nb=0,nb_second=-1,sound_feedback = True):
        self.handlers = {}
        self.intent_funcs = intent_funcs
        self.tts = tts,
        self.not_recognized_func = not_recognized_func
        self.nb = nb
        self.nb_second = nb_second
        self.sound_feedback = sound_feedback
        self.max_time = 0
    
    def send_intent_not_regognized(self):
        return self.nb == 0 \
            or self.nb_second != -1 \
            or self.not_recognized_func is not None
    
    def _create_handlers(self, config):
        for key,val in self.intent_funcs.items():
            self.handlers[config.intents.get_intent(key)] = val

    def get_intents(self, config):
        return list(self.intent_funcs.keys.map(
            lambda key: config.intents.get_intent(key)))
    
    def continue_session(self):
            if (self.nb == 0):
                return False
            if (False): #diff current time
                pass
            self.nb -= 1
            return True


def is_continue_intent_callback(_func):
    def decorator_check(func):
        @functools.wraps(func)
        def wrapper_check(self, hermes, intent_message):
            confidence_score = intent_message.intent.confidence_score
            threshold_1 = self.config.intents.get_threshold("intentBad")
            threshold_2 = self.config.intents.get_threshold("intentGood")
            if confidence_score <= threshold_1:
                tts = self.config.tts.get_value("ErrorIntentGood")
                hermes.publish_end_session(intent_message.session_id, tts)
            elif confidence_score <= threshold_2:
                tts = self.config.tts.get_value("ErrorIntentBad")
                hermes.publish_end_session(intent_message.session_id, tts)
            else:
                continueObject = func(self, hermes, intent_message)
                continueObject._create_handlers(self.config)
                self.save_continue_object(intent_message.session_id, continueObject)
                if continueObject.sound_feedback:
                    hermes.enable_sound_feeback(intent_message.site_id)
                else:
                    hermes.enable_sound_feeback(intent_message.site_id)
                hermes.publish_continue_session(intent_message.session_id,
                    continueObject.tts,
                    send_intent_not_recognized = continueObject.send_intent_not_regognized(),
                    intent_filter = continueObject.get_intents()
                )
        return wrapper_check
    if _func is None:
        return decorator_check
    return decorator_check(_func)

class ClientAction():

    def __init__(self, mqtt_addr, lang_config):
        threading.Thread.__init__(self)
        self.__mqtt_addr = mqtt_addr
        self.config = lang_config
        self.default_intents = {}
        self.continue_session_ids = {}
        self.default_sound_feedback = True

    def save_continue_object(self, session_id, obj):
        self.continue_session_ids[session_id] = obj

    def register_handler(self, func, config_intent_name):
        for name in self.config.intents.get_intent(config_intent_name):
            self.default_intents[name] = func

    def handler(self, hermes, intent_message):
        if intent_message.session_id in self.continue_session_ids:
            func = self.continue_session_ids[intent_message.session_id]\
                .handlers(intent_message.intent.intent_name)
            func(hermes, intent_message)
        elif  intent_message.intent.intent_name in self.default_intents:
            func = self.default_intents[intent_message.intent.intent_name]
            func(hermes, intent_message)
    
    def not_recognized_function(self, hermes, message):
        if message.session_id not in self.continue_session_ids:
            return
        continue_obj = self.continue_session_ids[message.session_id]
        if continue_obj.continue_session():
            tts = "" if continue_obj.sound_feedback else continue_obj.tts
            hermes.publish_continue_session(message.session_id,
                tts,
                send_intent_not_recognized = True,
                intent_filter = continue_obj.get_intents()
            )
        elif continue_obj.not_recognized_func is not None:
            continue_obj.not_recognized_func(hermes, message)

    
    def end_session_handler(self, hermes, message):
        continue_obj = self.continue_session_ids.pop(message.session_id)
        if continue_obj is None:
            return
        if self.default_sound_feedback:
            hermes.enable_sound_feeback(message.site_id)
        else:
            hermes.enable_sound_feeback(message.site_id)
        
    
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
    
    def start(self, loop=False):
        try:
            with Hermes(self.__mqtt_addr) as h:
                print("connected to: {}".format(self.__mqtt_addr))
                h.subscribe_intents(self.handler)
                h.subscribe_session_ended(self.end_session_handler)
                h.subscribe_intent_not_recognized(self.not_recognized_function)
                for site_id in ["default"]:
                    h.publish_start_session_notification(site_id,
                        self.config.tts.get_value("Ready"), None)
                if (loop):
                    h.loop_forever()
                else:
                    h.loop_start()
        except LibException:
            print("could not connect to broker: {}".format(self.__mqtt_addr))
            time.sleep(60)
