class Productcache_2Service:
    def __init__(self):
        self.products = {}
    def get_product(self, id):
        return self.products.get(id)

def calculate_cache_2(a, b):
    return a + b


from dataclasses import dataclass, field

@dataclass
class Recordcache_2:
    id: int
    data: dict = field(default_factory=dict)

