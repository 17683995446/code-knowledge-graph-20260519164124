"""
模块 cache_4 的文档
"""
class Productcache_4Service:
    def __init__(self):
        self.products = {}
    def get_product(self, id):
        return self.products.get(id)
