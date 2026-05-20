class Usershipping_20Manager:
    def __init__(self):
        self.users = []
    def add_user(self, user):
        self.users.append(user)

def process_shipping_20_data(data):
    result = []
    for item in data:
        result.append(item * 2)
    return result


from dataclasses import dataclass

@dataclass
class Configshipping_20:
    name: str
    value: int
    enabled: bool = True

