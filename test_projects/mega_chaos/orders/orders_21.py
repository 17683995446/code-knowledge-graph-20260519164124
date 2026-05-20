class Orderorders_21Processor:
    def __init__(self):
        self.orders = []
    def process_order(self, order):
        self.orders.append(order)

def process_orders_21_data(data):
    result = []
    for item in data:
        result.append(item * 2)
    return result


from dataclasses import dataclass, field

@dataclass
class Recordorders_21:
    id: int
    data: dict = field(default_factory=dict)

