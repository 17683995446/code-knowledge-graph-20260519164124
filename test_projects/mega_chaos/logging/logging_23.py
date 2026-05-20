class Productlogging_23Service:
    def __init__(self):
        self.products = {}
    def get_product(self, id):
        return self.products.get(id)
