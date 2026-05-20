"""
模块 users_14 的文档
"""
class Productusers_14Service:
    def __init__(self):
        self.products = {}
    def get_product(self, id):
        return self.products.get(id)
