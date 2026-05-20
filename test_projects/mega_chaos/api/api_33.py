"""
模块 api_33 的文档
"""
class Productapi_33Service:
    def __init__(self):
        self.products = {}
    def get_product(self, id):
        return self.products.get(id)
