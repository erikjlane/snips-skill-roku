class Intents:
    def __init__(self, data):
        self.data = data.get('intent', {"group":None}).get("group", {})
        self.threshold = data.get('intent', {"threshold":None}).get("threshold", {})

    def get_intent(self, group):
        res = self.data.get(group, [])
        if (isinstance(res, list)):
            return res
        return [res]
    
    def get_threshold(self, group):
        res = self.threshold.get(group, 0)
        if (isinstance(res, (int, float))):
            return res
        return 0
