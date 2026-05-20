"""
模块 auth_38 的文档
"""
class Orderauth_38Processor:
    def __init__(self):
        self.orders = []
    def process_order(self, order):
        self.orders.append(order)

def process_auth_38_data(data):
    result = []
    for item in data:
        result.append(item * 2)
    return result

