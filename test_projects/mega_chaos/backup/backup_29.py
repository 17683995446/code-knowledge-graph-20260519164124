class Userbackup_29Manager:
    def __init__(self):
        self.users = []
    def add_user(self, user):
        self.users.append(user)

def process_backup_29_data(data):
    result = []
    for item in data:
        result.append(item * 2)
    return result

