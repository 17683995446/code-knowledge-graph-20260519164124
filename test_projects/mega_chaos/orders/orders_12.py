class Productorders_12Service:
    def __init__(self):
        self.products = {}
    def get_product(self, id):
        return self.products.get(id)

def process_orders_12_data(data):
    result = []
    for item in data:
        result.append(item * 2)
    return result

