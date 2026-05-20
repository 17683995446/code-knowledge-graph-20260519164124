class Usersecurity_6Manager:
    def __init__(self):
        self.users = []
    def add_user(self, user):
        self.users.append(user)

def calculate_security_6(a, b):
    return a + b


from dataclasses import dataclass

@dataclass
class Configsecurity_6:
    name: str
    value: int
    enabled: bool = True

