class Userbackup_23Manager:
    def __init__(self):
        self.users = []
    def add_user(self, user):
        self.users.append(user)

def process_backup_23_data(data):
    result = []
    for item in data:
        result.append(item * 2)
    return result

