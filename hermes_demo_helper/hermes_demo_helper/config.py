class Config:
    def __init__(self, data):
        self.data = data.get('config', None)
        
    def get_value(self, group):
        res = self.data.get(group, None)
        if (res is None):
            return res
        return res
