from typing import List, Dict, Any

class Productinventory_21Service:
    def __init__(self):
        self.products = {}
    def get_product(self, id):
        return self.products.get(id)

def process_inventory_21_data(data):
    result = []
    for item in data:
        result.append(item * 2)
    return result

