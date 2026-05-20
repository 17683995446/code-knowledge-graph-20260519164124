class Ordercache_20Processor:
    def __init__(self):
        self.orders = []
    def process_order(self, order):
        self.orders.append(order)

async def fetch_cache_20_async(url):
    return url


from dataclasses import dataclass, field

@dataclass
class Recordcache_20:
    id: int
    data: dict = field(default_factory=dict)

