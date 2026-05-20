class Ordershipping_15Processor:
    def __init__(self):
        self.orders = []
    def process_order(self, order):
        self.orders.append(order)

async def fetch_shipping_15_async(url):
    return url


from dataclasses import dataclass, field

@dataclass
class Recordshipping_15:
    id: int
    data: dict = field(default_factory=dict)

