class Producttesting_12Service:
    def __init__(self):
        self.products = {}
    def get_product(self, id):
        return self.products.get(id)

def process_testing_12_data(data):
    result = []
    for item in data:
        result.append(item * 2)
    return result


from dataclasses import dataclass, field

@dataclass
class Recordtesting_12:
    id: int
    data: dict = field(default_factory=dict)

