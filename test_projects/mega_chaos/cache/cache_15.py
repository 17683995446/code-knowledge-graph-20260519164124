class Usercache_15Manager:
    def __init__(self):
        self.users = []
    def add_user(self, user):
        self.users.append(user)

async def fetch_cache_15_async(url):
    return url


from dataclasses import dataclass, field

@dataclass
class Recordcache_15:
    id: int
    data: dict = field(default_factory=dict)

