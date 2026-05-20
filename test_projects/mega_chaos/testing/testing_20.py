class Usertesting_20Manager:
    def __init__(self):
        self.users = []
    def add_user(self, user):
        self.users.append(user)

def calculate_testing_20(a, b):
    return a + b


from dataclasses import dataclass, field

@dataclass
class Recordtesting_20:
    id: int
    data: dict = field(default_factory=dict)

