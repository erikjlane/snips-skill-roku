class Tts:
    def __init__(self, data):
        self.data = data.get('tts', None)
        
    def get_value(self, group):
        res = self.data.get(group, None)
        if (res is None):
            return res
        if (isinstance(res, list)):
            return random.choice(res)
        return res
