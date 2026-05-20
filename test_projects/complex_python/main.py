# 复杂Python项目测试
# 包含各种边界情况和复杂结构

import os
import sys
from typing import List, Dict, Optional, Union, Generic, TypeVar, Callable, Any
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import asyncio
from contextlib import asynccontextmanager, contextmanager
from enum import Enum, auto

T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')

class BaseProcessor(ABC):
    """抽象基类处理器"""
    @abstractmethod
    def process(self, data: Any) -> Any:
        pass

    @abstractmethod
    async def async_process(self, data: Any) -> Any:
        pass

@dataclass
class Config:
    """配置数据类"""
    name: str
    enabled: bool = True
    timeout: int = 30
    retry_count: int = 3
    metadata: Dict[str, Any] = field(default_factory=dict)

class DatabaseError(Exception):
    """数据库异常"""
    def __init__(self, message: str, code: int = 0):
        super().__init__(message)
        self.code = code

class Validator:
    """验证器类"""
    @staticmethod
    def validate_email(email: str) -> bool:
        return '@' in email and '.' in email.split('@')[1]

    @staticmethod
    def validate_phone(phone: str) -> bool:
        return phone.isdigit() and len(phone) == 11

class UserService:
    """用户服务"""
    def __init__(self, config: Config):
        self.config = config
        self._cache = {}
        self._users = []

    async def create_user(self, name: str, email: str) -> Dict[str, Any]:
        """创建用户"""
        if not Validator.validate_email(email):
            raise ValueError("Invalid email format")

        user = {
            'id': len(self._users) + 1,
            'name': name,
            'email': email,
            'created_at': asyncio.get_event_loop().time()
        }
        self._users.append(user)
        return user

    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """获取用户"""
        return next((u for u in self._users if u['id'] == user_id), None)

    async def list_users(self, page: int = 1, page_size: int = 10) -> List[Dict[str, Any]]:
        """列出用户"""
        start = (page - 1) * page_size
        end = start + page_size
        return self._users[start:end]

class OrderStatus(Enum):
    """订单状态枚举"""
    PENDING = auto()
    PROCESSING = auto()
    COMPLETED = auto()
    CANCELLED = auto()

@dataclass
class Order:
    """订单类"""
    order_id: str
    user_id: int
    amount: float
    status: OrderStatus = OrderStatus.PENDING
    items: List[Dict[str, Any]] = field(default_factory=list)

class OrderProcessor(BaseProcessor):
    """订单处理器"""
    def __init__(self, user_service: UserService):
        self.user_service = user_service
        self._orders = []

    def process(self, order_data: Dict[str, Any]) -> Order:
        """处理订单"""
        user = self.user_service.get_user(order_data['user_id'])
        if not user:
            raise DatabaseError("User not found", code=404)

        order = Order(
            order_id=order_data['order_id'],
            user_id=order_data['user_id'],
            amount=order_data['amount']
        )
        self._orders.append(order)
        return order

    async def async_process(self, order_data: Dict[str, Any]) -> Order:
        """异步处理订单"""
        return self.process(order_data)

    async def cancel_order(self, order_id: str) -> bool:
        """取消订单"""
        for order in self._orders:
            if order.order_id == order_id:
                if order.status == OrderStatus.COMPLETED:
                    raise ValueError("Cannot cancel completed order")
                order.status = OrderStatus.CANCELLED
                return True
        return False

class AdvancedCache(Generic[K, V]):
    """高级缓存类"""
    def __init__(self, max_size: int = 1000):
        self._cache: Dict[K, V] = {}
        self._max_size = max_size
        self._access_count: Dict[K, int] = {}

    def get(self, key: K) -> Optional[V]:
        """获取缓存"""
        if key in self._cache:
            self._access_count[key] = self._access_count.get(key, 0) + 1
            return self._cache[key]
        return None

    def set(self, key: K, value: V) -> None:
        """设置缓存"""
        if len(self._cache) >= self._max_size:
            least_used = min(self._access_count.items(), key=lambda x: x[1])[0]
            del self._cache[least_used]
            del self._access_count[least_used]

        self._cache[key] = value
        self._access_count[key] = 1

@contextmanager
def managed_resource(name: str):
    """上下文管理器资源"""
    print(f"Acquiring resource: {name}")
    yield f"Resource: {name}"
    print(f"Releasing resource: {name}")

@asynccontextmanager
async def async_managed_resource(name: str):
    """异步上下文管理器"""
    print(f"Async acquiring: {name}")
    yield f"Async: {name}"
    print(f"Async releasing: {name}")

def process_with_retry(func: Callable, max_retries: int = 3):
    """带重试的处理器"""
    def wrapper(*args, **kwargs):
        last_error = None
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    print(f"Retry {attempt + 1}/{max_retries}")
        raise last_error
    return wrapper

class DataPipeline:
    """数据管道"""
    def __init__(self):
        self._transformers: List[Callable] = []

    def add_transformer(self, transformer: Callable) -> 'DataPipeline':
        """添加转换器"""
        self._transformers.append(transformer)
        return self

    def process(self, data: Any) -> Any:
        """处理数据"""
        result = data
        for transformer in self._transformers:
            result = transformer(result)
        return result

# 嵌套类和内部类
class OuterClass:
    """外部类"""
    class InnerClass:
        """内部类"""
        class DeepInnerClass:
            """深层内部类"""
            def deep_method(self):
                pass

    def outer_method(self):
        class LocalClass:
            """局部类"""
            def local_method(self):
                pass
        return LocalClass()

# 多继承和Mixin
class Loggable:
    """日志混入类"""
    def log(self, message: str):
        print(f"[LOG] {message}")

class Serializable:
    """可序列化混入类"""
    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__

class UserWithMixin(UserService, Loggable, Serializable):
    """带混入的用户服务"""
    pass

# 装饰器
def timer(func):
    """计时装饰器"""
    def wrapper(*args, **kwargs):
        import time
        start = time.time()
        result = func(*args, **kwargs)
        print(f"{func.__name__} took {time.time() - start:.4f}s")
        return result
    return wrapper

@timer
def complex_computation(n: int) -> int:
    """复杂计算"""
    if n <= 1:
        return n
    return complex_computation(n-1) + complex_computation(n-2)

# 工厂模式
class Shape(ABC):
    """形状抽象类"""
    @abstractmethod
    def draw(self):
        pass

class Circle(Shape):
    def draw(self):
        print("Drawing circle")

class Square(Shape):
    def draw(self):
        print("Drawing square")

class ShapeFactory:
    """形状工厂"""
    _shapes = {
        'circle': Circle,
        'square': Square
    }

    @classmethod
    def create(cls, shape_type: str) -> Shape:
        shape_class = cls._shapes.get(shape_type)
        if not shape_class:
            raise ValueError(f"Unknown shape: {shape_type}")
        return shape_class()

# 闭包
def create_counter(initial: int = 0):
    """计数器闭包"""
    count = initial
    def counter():
        nonlocal count
        count += 1
        return count
    return counter

# Lambda和高级函数
numbers = [1, 2, 3, 4, 5]
squared = list(map(lambda x: x ** 2, numbers))
evens = list(filter(lambda x: x % 2 == 0, numbers))
total = reduce(lambda x, y: x + y, numbers)

# 生成器
def fibonacci_generator():
    """斐波那契生成器"""
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

# 协程
async def async_generator():
    """异步生成器"""
    for i in range(10):
        await asyncio.sleep(0.1)
        yield i

# 元编程
class MetaClass(type):
    """元类"""
    def __new__(cls, name, bases, attrs):
        attrs['created_by_meta'] = True
        return super().__new__(cls, name, bases, attrs)

class Metaclassed(metaclass=MetaClass):
    """使用元类的类"""
    pass

# 类型别名
Vector = List[float]
Matrix = List[List[float]]
Result = Union[str, int, None]
Callback = Callable[[int, str], None]

def process_vector(vec: Vector, callback: Optional[Callback] = None) -> float:
    """处理向量"""
    result = sum(x**2 for x in vec) ** 0.5
    if callback:
        callback(200, "Success")
    return result
