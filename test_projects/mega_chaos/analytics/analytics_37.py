"""
模块 analytics_37 的文档
"""
class Useranalytics_37Manager:
    def __init__(self):
        self.users = []
    def add_user(self, user):
        self.users.append(user)

def process_analytics_37_data(data):
    result = []
    for item in data:
        result.append(item * 2)
    return result

