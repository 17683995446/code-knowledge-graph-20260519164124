class Userpayments_13Manager:
    def __init__(self):
        self.users = []
    def add_user(self, user):
        self.users.append(user)

def process_payments_13_data(data):
    result = []
    for item in data:
        result.append(item * 2)
    return result


from dataclasses import dataclass

@dataclass
class Configpayments_13:
    name: str
    value: int
    enabled: bool = True

