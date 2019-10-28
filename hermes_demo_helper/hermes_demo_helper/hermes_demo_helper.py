from hermes_python.ffi import LibException
from hermes_python.hermes import Hermes
from hermes_python.ontology.feedback import SiteMessage
import time
import threading

from .snipsConfig import Snips_config


class SnipsFlow():
    """
    A class to wrap hermes python
    Snips flow handle the connection, and the language setting
    """

    class EndSession():
        def __init__(self, tts):
            self.tts = tts

    class ContinueSession():
        def __init__(self, funcs, tts, not_recognized_func=None, retry_count=0, timeout=-1, sound_feedback=True):
            self.funcs = funcs
            self.tts = tts
            self.not_recognized_func = not_recognized_func
            self.timeout = timeout
            self.sound_feedback = sound_feedback
            if timeout != -1:
                retry_count = -1
            self.retry_count = retry_count

        def send_intent_not_recognized(self):
            return self.retry_count == 0 \
                or self.timeout != -1 \
                or self.not_recognized_func is not None

        def continue_session(self):
            if (self.retry_count == 0):
                return False
            if (self.retry_count == -1):
                return True
            self.retry_count -= 1
            return True

    def __init__(self):
        self.__mqtt_addr = None
        self.config = None
        self.continue_session_ids = {}
        self.default_sound_feedback = Snips_config.get_default_enable_feedback()
        self.data = None
        self.default_intent_map = {}
        self._default_intent_map = {}
        self.continue_intent_map = {}
        self._continue_intent_map = {}
        self.h = None

    def start(self, loop=False):
        try:
            with Hermes(self.__mqtt_addr) as h:
                print("connected to: {}".format(self.__mqtt_addr))
                h.subscribe_intents(self._handler)
                h.subscribe_session_ended(self._end_session_handler)
                h.subscribe_intent_not_recognized(self._not_recognized_handler)
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
        if self.h is not None:
            self.h.loop_stop()

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

    def intent(self, intent, *options, slots=[], data=[]):
        """ Decorator for function that handle intent for the first iteration of the flow

        Parameter
        --------
        self : SnipsFlow
        intent : str
            string corresponding to a intent inside the language configuration file
            the function will be called after the corresponding intent is trigger
        slots : Tuple(string)
            tuple of string corresponding to Slots inside the language configuration file
            this will be the argument of you function, you will find into those argument the value
            of the slot decribe in its name
        option : str
            all other arguments that you might need, ex: hermes, intent_message, and the object you
            save thanks to set_data
        """
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
                    continueObject = f(
                        **self._slots(intent_message, hermes, slots, data, options))
                    if isinstance(continueObject, str):
                        hermes.publish_end_session(
                            intent_message.session_id, continueObject)
                        return
                    if isinstance(continueObject, SnipsFlow.EndSession):
                        hermes.publish_end_session(
                            intent_message.session_id, continueObject.tts)
                        return
                    self._save_continue_object(
                        intent_message.session_id, continueObject, hermes)
                    if continueObject.sound_feedback:
                        hermes.enable_sound_feedback(
                            SiteMessage(intent_message.site_id))
                    else:
                        hermes.disable_sound_feedback(
                            SiteMessage(intent_message.site_id))
                    hermes.publish_continue_session(intent_message.session_id,
                                                    continueObject.tts,
                                                    send_intent_not_recognized=continueObject.send_intent_not_recognized(),
                                                    intent_filter=self._get_intent_continue(
                                                        continueObject.funcs)
                                                    )
            self._default_intent_map[intent] = wrapper
            return wrapper
        return decorator

    def not_recognized(self, *options):
        """ Decorator for function that handle not recognized intent after a continue session
        ie: after you return flow.continue_session(...) in a handler

        Parameter
        --------
        self : SnipsFlow
        option : str
            all other arguments that you might need, ex: hermes, intent_message, and the object you
            save thanks to set_data
        """
        def decorator(f):
            def wrapper(hermes, intent_message):
                f(**self._slots(intent_message, hermes, [], [], options))
            return wrapper
        return decorator

    def on_continue(self, intent, slots=[], data=[], *options):
        """ Decorator for function that handle intent after a continue session
        ie: after you return flow.continue_session(...) in a handler

        Parameter
        --------
        self : SnipsFlow
        intent : str
            string corresponding to a intent inside the language configuration file
            the function will be called after the corresponding intent is trigger
        slots : Tuple(string)
            tuple of string corresponding to Slots inside the language configuration file
            this will be the argument of you function, you will find into those argument the value
            of the slot decribe in its name
        option : str
            all other arguments that you might need, ex: hermes, intent_message, and the object you
            save thanks to set_data
        """
        def decorator(f):
            self._continue_intent_map[f] = intent
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
                    continueObject = f(
                        **self._slots(intent_message, hermes, slots, data, options))
                    if isinstance(continueObject, str):
                        hermes.publish_end_session(
                            intent_message.session_id, continueObject)
                        return
                    if isinstance(continueObject, SnipsFlow.EndSession):
                        hermes.publish_end_session(
                            intent_message.session_id, continueObject.tts)
                        return
                    self._save_continue_object(
                        intent_message.session_id, continueObject, hermes)
                    if continueObject.sound_feedback:
                        hermes.enable_sound_feedback(
                            SiteMessage(intent_message.site_id))
                    else:
                        hermes.disable_sound_feedback(
                            SiteMessage(intent_message.site_id))
                    hermes.publish_continue_session(intent_message.session_id,
                                                    continueObject.tts,
                                                    send_intent_not_recognized=continueObject.send_intent_not_recognized(),
                                                    intent_filter=self._get_intent_continue(
                                                        continueObject.funcs)
                                                    )
            return wrapper
        return decorator

    @staticmethod
    def end_session(tts=None):
        return SnipsFlow.EndSession(tts)

    def continue_session(self, funcs, tts, not_recognized_func=None, retry_count=0, timeout=-1, sound_feedback=True):
        return SnipsFlow.ContinueSession(funcs, tts, not_recognized_func, retry_count, timeout, sound_feedback)

    def _not_recognized_handler(self, hermes, message):
        if message.session_id not in self.continue_session_ids:
            return
        continue_obj = self.continue_session_ids[message.session_id]
        if continue_obj.continue_session():
            tts = "" if continue_obj.sound_feedback else continue_obj.tts
            hermes.publish_continue_session(message.session_id,
                                            tts,
                                            send_intent_not_recognized=True,
                                            intent_filter=self._get_intent_continue(
                                                continue_obj.funcs)
                                            )
        elif continue_obj.not_recognized_func is not None:
            hermes.publish_end_session(
                message.session_id, continue_obj.not_recognized_func(hermes, message))
        else:
            hermes.publish_end_session(message.session_id, "")

    def _slots(self, intent_message, hermes, slots, datas, *argv):
        result = {}
        if isinstance(slots, tuple) or isinstance(slots, list):
            for slot in slots:
                result[slot] = self._extract_value(intent_message, slot)
        elif isinstance(slots, str):
            result[slots] = self._extract_value(intent_message, slots)
        if isinstance(datas, tuple) or isinstance(datas, list):
            for data in datas:
                if data in self.data:
                    result[data] = self.data[data]
                else:
                    result[data] = None
        elif isinstance(datas, str):
                if datas in self.data:
                    result[datas] = self.data[datas]
                else:
                    result[datas] = None
        for args in argv:
            for arg in args:
                if arg == 'hermes':
                    result['hermes'] = hermes
                elif arg == 'intent_message':
                    result["intent_message"] = intent_message
                elif arg in self.data:
                    result[arg] = self.data[arg]
                else:
                    result[arg] = self._extract_value(intent_message, arg)
        return result

    def _save_continue_object(self, session_id, obj, hermes):
        self.continue_session_ids[session_id] = obj
        if obj.retry_count <= -1:
            return
        threading.Timer(obj.timeout,
                        self._run_not_recognized_timeout,
                        args=(hermes, session_id)
                        ).start()

    def _get_intent_continue(self, funcs):
        result = []
        for func in funcs:
            if func in self.continue_intent_map:
                result.append(self.continue_intent_map[func])
        return result

    def _run_not_recognized_timeout(self, hermes, session_id):
        if session_id not in self.continue_session_ids:
            return
        obj = self.continue_session_ids[session_id]
        hermes.publish_end_session(
            session_id, obj.not_recognized_func(hermes, None))

    def _handler(self, hermes, intent_message):
        print("totototototototootoo")
        if intent_message.session_id in self.continue_session_ids:
            funcs = self.continue_session_ids[intent_message.session_id].funcs
            for func in funcs:
                if func in self.continue_intent_map and intent_message.intent.intent_name == self.continue_intent_map[func]:
                    func(hermes, intent_message)
        elif intent_message.intent.intent_name in self.default_intent_map:
            func = self.default_intent_map[intent_message.intent.intent_name]
            func(hermes, intent_message)

    def _end_session_handler(self, hermes, message):
        continue_obj = self.continue_session_ids.pop(message.session_id, None)
        if continue_obj is None:
            return
        if self.default_sound_feedback:
            hermes.enable_sound_feedback(SiteMessage(message.site_id))
        else:
            hermes.enable_sound_feedback(SiteMessage(message.site_id))

    def _extract_defaults(self, intent_message, slot_name):
        result = []
        threshold = self.config.slots.get_threshold(slot_name)
        slot_name = self.config.slots.get_value(slot_name)
        if (intent_message.slots is not None):
            for i in intent_message.slots[slot_name]:
                if i.confidence_score > threshold:
                    result.append(i.slot_value.value)
        return result

    def _extract_default(self, intent_message, slot_name):
        res = self._extract_defaults(intent_message, slot_name)
        if (res is None or len(res) == 0):
            return None
        return res[0]

    def _extract_values(self, intent_message, slot_name):
            result = []
            threshold = self.config.slots.get_threshold(slot_name)
            slot_name = self.config.slots.get_value(slot_name)
            if (intent_message.slots is not None):
                for i in intent_message.slots[slot_name]:
                    if i.confidence_score > threshold:
                        result.append(i.slot_value.value.value)
            return result

    def _extract_value(self, intent_message, slot_name):
        res = self._extract_values(intent_message, slot_name)
        if (res is None or len(res) == 0):
            return None
        return res[0]
