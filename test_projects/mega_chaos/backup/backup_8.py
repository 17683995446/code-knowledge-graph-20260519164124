class Userbackup_8Manager:
    def __init__(self):
        self.users = []
    def add_user(self, user):
        self.users.append(user)

def process_backup_8_data(data):
    result = []
    for item in data:
        result.append(item * 2)
    return result


from dataclasses import dataclass, field

@dataclass
class Recordbackup_8:
    id: int
    data: dict = field(default_factory=dict)

