"""
模块 logging_2 的文档
"""
class Orderlogging_2Processor:
    def __init__(self):
        self.orders = []
    def process_order(self, order):
        self.orders.append(order)
