from .tts import Tts
from .slots import Slots
from .intents import Intents
from .config import Config
import json

class Lang_config:
    def __init__(self, dir_path, lang='en'):
        ASSISTANT = '/var/lib/snips/assistant/assistant.json'
        try:
            with open(ASSISTANT, encoding='utf-8') as f:
                data = json.load(f)
                lang = json.get('language', lang)
        except :
            pass
        DEFAULT_PATH = '{}/{}.json'
        try:
            path = DEFAULT_PATH.format(dir_path, lang)
            with open(path) as f:
                data = json.load(f)
                self.tts = Tts(data)
                self.intents = Intents(data)
                self.slots = Slots(data)
                self.config = Config(data)
        except :
            path = DEFAULT_PATH.format(dir_path, 'en')
            with open(path) as f:
                data = json.load(f)
                self.tts = Tts(data)
                self.intents = Intents(data)
                self.slots = Slots(data)
                self.config = Config(data)
