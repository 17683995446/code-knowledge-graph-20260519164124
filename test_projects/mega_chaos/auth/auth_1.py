class Productauth_1Service:
    def __init__(self):
        self.products = {}
    def get_product(self, id):
        return self.products.get(id)

def process_auth_1_data(data):
    result = []
    for item in data:
        result.append(item * 2)
    return result

