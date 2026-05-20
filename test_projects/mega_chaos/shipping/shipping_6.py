"""
模块 shipping_6 的文档
"""
class Ordershipping_6Processor:
    def __init__(self):
        self.orders = []
    def process_order(self, order):
        self.orders.append(order)

def process_shipping_6_data(data):
    result = []
    for item in data:
        result.append(item * 2)
    return result

