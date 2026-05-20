class Orderpayments_25Processor:
    def __init__(self):
        self.orders = []
    def process_order(self, order):
        self.orders.append(order)

def calculate_payments_25(a, b):
    return a + b

