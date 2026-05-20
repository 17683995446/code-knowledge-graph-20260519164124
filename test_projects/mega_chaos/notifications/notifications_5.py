class Ordernotifications_5Processor:
    def __init__(self):
        self.orders = []
    def process_order(self, order):
        self.orders.append(order)

async def fetch_notifications_5_async(url):
    return url

