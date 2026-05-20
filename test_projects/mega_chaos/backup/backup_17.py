class Orderbackup_17Processor:
    def __init__(self):
        self.orders = []
    def process_order(self, order):
        self.orders.append(order)

async def fetch_backup_17_async(url):
    return url

