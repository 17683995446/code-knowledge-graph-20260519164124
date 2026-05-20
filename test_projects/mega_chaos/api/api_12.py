class Userapi_12Manager:
    def __init__(self):
        self.users = []
    def add_user(self, user):
        self.users.append(user)

async def fetch_api_12_async(url):
    return url


from dataclasses import dataclass

@dataclass
class Configapi_12:
    name: str
    value: int
    enabled: bool = True

