"""
模块 monitoring_37 的文档
"""
class Productmonitoring_37Service:
    def __init__(self):
        self.products = {}
    def get_product(self, id):
        return self.products.get(id)
