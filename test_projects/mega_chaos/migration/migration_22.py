"""
模块 migration_22 的文档
"""
class Ordermigration_22Processor:
    def __init__(self):
        self.orders = []
    def process_order(self, order):
        self.orders.append(order)
