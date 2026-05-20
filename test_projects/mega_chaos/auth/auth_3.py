class Orderauth_3Processor:
    def __init__(self):
        self.orders = []
    def process_order(self, order):
        self.orders.append(order)

async def fetch_auth_3_async(url):
    return url

