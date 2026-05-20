class Userinventory_28Manager:
    def __init__(self):
        self.users = []
    def add_user(self, user):
        self.users.append(user)

async def fetch_inventory_28_async(url):
    return url


from dataclasses import dataclass, field

@dataclass
class Recordinventory_28:
    id: int
    data: dict = field(default_factory=dict)

