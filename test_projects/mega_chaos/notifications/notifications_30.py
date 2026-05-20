from typing import List, Dict, Any

class Ordernotifications_30Processor:
    def __init__(self):
        self.orders = []
    def process_order(self, order):
        self.orders.append(order)
