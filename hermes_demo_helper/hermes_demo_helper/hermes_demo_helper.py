#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import json
import random
import functools
import threading
from hermes_python.ffi import LibException
from hermes_python.hermes import Hermes
from hermes_python.ontology.feedback import SiteMessage
import time
import threading

from .snipsConfig import Snips_config



class ContinueObject():
    def __init__(self, funcs, tts, not_recognized_func=None, nb=0,nb_second=-1,sound_feedback = True):
        self.handlers = {}
        self.funcs = funcs
        self.tts = tts
        self.not_recognized_func = not_recognized_func
        self.nb_second = nb_second
        self.sound_feedback = sound_feedback
        if nb_second != -1:
            nb = -1
        self.nb = nb

    def send_intent_not_regognized(self):
        return self.nb == 0 \
            or self.nb_second != -1 \
            or self.not_recognized_func is not None

    def continue_session(self):
            if (self.nb == 0):
                return False
            if (self.nb == -1): #diff current time
                return True
            self.nb -= 1
            return True

class SnipsFlow():

    def __init__(self):
        self.__mqtt_addr = None
        self.config = None
        self.default_intents = {}
        self.continue_session_ids = {}
        self.default_sound_feedback = Snips_config.get_default_enable_feedback()
        self.data = None
        self.default_intent_map = {}
        self._default_intent_map = {}
        self.continue_intent_map ={}
        self._continue_intent_map ={}

    def set_lang_config(self, lang_config):
        self.config = lang_config
        for key, f in self._default_intent_map.items():
            for name in self.config.intents.get_intent(key):
                self.default_intent_map[name] = f
        for f, key in self._continue_intent_map.items():
            for name in self.config.intents.get_intent(key):
                self.continue_intent_map[f] = name

    def set_data(self, **kwarg):
        self.data = kwarg
    
    def set_host(self, host):
        self.__mqtt_addr = host
    
    def slots(self, intent_message, hermes, *argv):
        result = {}
        for args in argv:
            for arg in args:
                if arg == 'hermes':
                    result['hermes'] = hermes
                elif arg == 'intent_message':
                    result["intent_message"] = intent_message
                elif arg in self.data:
                    result[arg] = self.data[arg]
                else:
                    result[arg] = self.extract_value(intent_message, arg)
        return result

    def save_continue_object(self, session_id, obj, hermes):
        self.continue_session_ids[session_id] = obj
        if obj.nb_second <= -1:
            return
        threading.Timer(obj.nb_second,
            self.run_not_recognized_time,
            args=(hermes, session_id)
        ).start()

    def intent_with_continue(self, intent, *options):
        def decorator(f):
            def wrapper(hermes, intent_message):
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
                    continueObject = f(**self.slots(intent_message, hermes, options))
                    self.save_continue_object(intent_message.session_id, continueObject, hermes)
                    if continueObject.sound_feedback:
                        hermes.enable_sound_feedback(SiteMessage(intent_message.site_id))
                    else:
                        hermes.disable_sound_feedback(SiteMessage(intent_message.site_id))
                    hermes.publish_continue_session(intent_message.session_id,
                        continueObject.tts,
                        send_intent_not_recognized = continueObject.send_intent_not_regognized(),
                        intent_filter = self.get_intent_continue(continueObject.funcs)
                    )
            self._default_intent_map[intent] = wrapper
            return wrapper
        return decorator

    def not_recognized(self, *options):
        def decorator(f):
            def wrapper(hermes, intent_message):
                f(**self.slots(intent_message, hermes, options))
            return wrapper
        return decorator

    def intent(self, intent, *options):
        def decorator(f):
            def wrapper(hermes, intent_message):
                confidence_score = intent_message.intent.confidence_score
                threshold_1 = self.config.intents.get_threshold("intentBad")
                threshold_2 = self.config.intents.get_threshold("intentGood")
                if confidence_score <= threshold_1:
                    tts = self.config.tts.get_value("ErrorIntentGood")
                elif confidence_score <= threshold_2:
                    tts = self.config.tts.get_value("ErrorIntentBad")
                else:
                    tts = f(**self.slots(intent_message, hermes, options))
                hermes.publish_end_session(intent_message.session_id, tts)
            self._default_intent_map[intent] = wrapper
            return wrapper
        return decorator
    def get_intent_continue(self, funcs):
        result = []
        for func in funcs:
            if func in self.continue_intent_map:
                result.append(self.continue_intent_map[func])
        return result
    def intent_on_continue(self, intent, *options):
        def decorator(f):
            self._continue_intent_map[f] = intent
            def wrapper(hermes, intent_message):
                confidence_score = intent_message.intent.confidence_score
                threshold_1 = self.config.intents.get_threshold("intentBad")
                threshold_2 = self.config.intents.get_threshold("intentGood")
                if confidence_score <= threshold_1:
                    tts = self.config.tts.get_value("ErrorIntentGood")
                elif confidence_score <= threshold_2:
                    tts = self.config.tts.get_value("ErrorIntentBad")
                else:
                    tts = f(**self.slots(intent_message, hermes, options))
                hermes.publish_end_session(intent_message.session_id, tts)
            return wrapper
        return decorator
    
    def run_not_recognized_time(self, hermes, session_id):
        if session_id not in self.continue_session_ids:
            return
        obj = self.continue_session_ids[session_id]
        hermes.publish_end_session(session_id, obj.not_recognized_func(hermes, None))

    def handler(self, hermes, intent_message):
        if intent_message.session_id in self.continue_session_ids:
            funcs = self.continue_session_ids[intent_message.session_id].funcs
            for func in funcs:
                if func in self.continue_intent_map and intent_message.intent.intent_name == self.continue_intent_map[func]:
                    func(hermes, intent_message)
        elif  intent_message.intent.intent_name in self.default_intent_map:
            func = self.default_intent_map[intent_message.intent.intent_name]
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
                intent_filter = self.get_intent_continue(continue_obj.funcs)
            )
        elif continue_obj.not_recognized_func is not None:
            hermes.publish_end_session(message.session_id, continue_obj.not_recognized_func(hermes, message))
        else:
            hermes.publish_end_session(message.session_id, "")

    def end_session_handler(self, hermes, message):
        continue_obj = self.continue_session_ids.pop(message.session_id, None)
        if continue_obj is None:
            return
        if self.default_sound_feedback:
            hermes.enable_sound_feedback(SiteMessage(message.site_id))
        else:
            hermes.enable_sound_feedback(SiteMessage(message.site_id))
        
    
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
                    self.h = h
        except LibException:
            print("could not connect to broker: {}".format(self.__mqtt_addr))

    def stop(self):
        self.h.loop_stop()
