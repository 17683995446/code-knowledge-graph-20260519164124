class Orderlogging_20Processor:
    def __init__(self):
        self.orders = []
    def process_order(self, order):
        self.orders.append(order)

def process_logging_20_data(data):
    result = []
    for item in data:
        result.append(item * 2)
    return result


from dataclasses import dataclass, field

@dataclass
class Recordlogging_20:
    id: int
    data: dict = field(default_factory=dict)

