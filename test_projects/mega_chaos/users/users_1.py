class Orderusers_1Processor:
    def __init__(self):
        self.orders = []
    def process_order(self, order):
        self.orders.append(order)

def process_users_1_data(data):
    result = []
    for item in data:
        result.append(item * 2)
    return result

