class Ordertesting_1Processor:
    def __init__(self):
        self.orders = []
    def process_order(self, order):
        self.orders.append(order)

async def fetch_testing_1_async(url):
    return url

