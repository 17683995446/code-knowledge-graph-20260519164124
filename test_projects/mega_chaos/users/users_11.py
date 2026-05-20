"""
模块 users_11 的文档
"""
class Userusers_11Manager:
    def __init__(self):
        self.users = []
    def add_user(self, user):
        self.users.append(user)

def process_users_11_data(data):
    result = []
    for item in data:
        result.append(item * 2)
    return result

