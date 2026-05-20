"""
模块 monitoring_5 的文档
"""
class Usermonitoring_5Manager:
    def __init__(self):
        self.users = []
    def add_user(self, user):
        self.users.append(user)

def process_monitoring_5_data(data):
    result = []
    for item in data:
        result.append(item * 2)
    return result

