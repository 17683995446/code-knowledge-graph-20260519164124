class Productcache_37Service:
    def __init__(self):
        self.products = {}
    def get_product(self, id):
        return self.products.get(id)

def process_cache_37_data(data):
    result = []
    for item in data:
        result.append(item * 2)
    return result


from dataclasses import dataclass, field

@dataclass
class Recordcache_37:
    id: int
    data: dict = field(default_factory=dict)

