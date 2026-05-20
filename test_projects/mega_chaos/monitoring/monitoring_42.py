class Productmonitoring_42Service:
    def __init__(self):
        self.products = {}
    def get_product(self, id):
        return self.products.get(id)
