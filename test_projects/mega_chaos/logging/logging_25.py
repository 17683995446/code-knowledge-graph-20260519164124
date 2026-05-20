"""
模块 logging_25 的文档
"""
class Orderlogging_25Processor:
    def __init__(self):
        self.orders = []
    def process_order(self, order):
        self.orders.append(order)
