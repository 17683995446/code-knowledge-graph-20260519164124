class Userdeploy_24Manager:
    def __init__(self):
        self.users = []
    def add_user(self, user):
        self.users.append(user)

async def fetch_deploy_24_async(url):
    return url


from dataclasses import dataclass

@dataclass
class Configdeploy_24:
    name: str
    value: int
    enabled: bool = True

