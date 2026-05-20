"""
模块 api_20 的文档
"""
class Userapi_20Manager:
    def __init__(self):
        self.users = []
    def add_user(self, user):
        self.users.append(user)

def process_api_20_data(data):
    result = []
    for item in data:
        result.append(item * 2)
    return result

