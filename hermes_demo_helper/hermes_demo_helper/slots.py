class Slots:
    def __init__(self, data):
        self.data = data.get('slot', None)
        
    def get_value(self, group):
        res = self.data.get(group, {"name":None}).get("name")
        if (res is None):
            return None
        if (isinstance(res, (str))):
            return res
        return None

    def get_threshold(self, group):
        res = self.data.get(group, {"threshold": 0}).get("threshold")
        if (res is None):
            return 0
        if (isinstance(res, (int, float))):
            return res
        return 0
