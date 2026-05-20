"""
模块 logging_7 的文档
"""
class Orderlogging_7Processor:
    def __init__(self):
        self.orders = []
    def process_order(self, order):
        self.orders.append(order)

def process_logging_7_data(data):
    result = []
    for item in data:
        result.append(item * 2)
    return result

