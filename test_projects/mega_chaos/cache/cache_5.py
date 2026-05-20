class Productcache_5Service:
    def __init__(self):
        self.products = {}
    def get_product(self, id):
        return self.products.get(id)

def process_cache_5_data(data):
    result = []
    for item in data:
        result.append(item * 2)
    return result

