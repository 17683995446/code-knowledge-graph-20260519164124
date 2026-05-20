class Orderapi_11Processor:
    def __init__(self):
        self.orders = []
    def process_order(self, order):
        self.orders.append(order)

async def fetch_api_11_async(url):
    return url

