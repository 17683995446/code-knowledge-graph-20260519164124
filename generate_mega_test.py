#!/usr/bin/env python3
"""自动生成超大规模混乱测试项目"""
import os
import random
import string
from pathlib import Path

BASE_PATH = "/workspace/test_projects/mega_chaos"

CLASS_TEMPLATES = [
    '''class User{mid}Manager:
    def __init__(self):
        self.users = []
    def add_user(self, user):
        self.users.append(user)
''',
    '''class Product{mid}Service:
    def __init__(self):
        self.products = {}
    def get_product(self, id):
        return self.products.get(id)
''',
    '''class Order{mid}Processor:
    def __init__(self):
        self.orders = []
    def process_order(self, order):
        self.orders.append(order)
''',
]

FUNCTION_TEMPLATES = [
    '''def calculate_{mid}(a, b):
    return a + b

''',
    '''def process_{mid}_data(data):
    result = []
    for item in data:
        result.append(item * 2)
    return result

''',
    '''async def fetch_{mid}_async(url):
    return url

''',
]

DATACLASS_TEMPLATES = [
    '''from dataclasses import dataclass

@dataclass
class Config{mid}:
    name: str
    value: int
    enabled: bool = True

''',
    '''from dataclasses import dataclass, field

@dataclass
class Record{mid}:
    id: int
    data: dict = field(default_factory=dict)

''',
]

EDGE_CASE_FILES = {
    "unicode_names.py": '''# -*- coding: utf-8 -*-
class 用户管理:
    def __init__(self):
        self.用户列表 = []
    
    def 添加用户(self, 用户):
        self.用户列表.append(用户)

class 产品服务:
    产品字典 = {}

class 订单处理:
    async def 处理订单(订单):
        pass
''',
    
    "special_chars.py": '''class ClassWith@#$:
    def method$with#special(*args):
        pass

def function@with!special():
    pass
''',
    
    "very_long_line.py": ("x" * 10000) + " = " + ("y" * 10000),
    
    "empty.py": "",
    
    "only_comments.py": "# This file only has comments\n# Another comment\n# Yet another",
    
    "encoding_gb2312.py": "# -*- coding: gb2312 -*-\nclass 中文类:\n    pass\n",
    
    "binary_pseudo.py": "x = \\x00\\x01\\x02\ny = \\xff\\xfe",
    
    "tabs_and_spaces.py": """class\tWeird:
	def\ttab_indent(self):
		pass
""",
}

def generate_random_code(mid, complexity=1):
    """生成随机代码"""
    code_parts = []
    
    if complexity >= 1:
        template = random.choice(CLASS_TEMPLATES)
        code_parts.append(template.replace("{mid}", mid))
    
    if complexity >= 2:
        template = random.choice(FUNCTION_TEMPLATES)
        code_parts.append(template.replace("{mid}", mid))
    
    # 使用mid的hash来确保一致性
    if complexity >= 3 and hash(mid) % 3 == 0:
        template = random.choice(DATACLASS_TEMPLATES)
        code_parts.append(template.replace("{mid}", mid))
    
    return "\n".join(code_parts)

def create_mega_project():
    """创建超大规模混乱项目"""
    print(f"📦 正在创建超大规模测试项目: {BASE_PATH}")
    
    # 创建目录结构
    os.makedirs(BASE_PATH, exist_ok=True)
    
    modules = [
        "users", "products", "orders", "inventory", "analytics",
        "reports", "payments", "shipping", "notifications", "auth",
        "api", "database", "cache", "logging", "monitoring",
        "security", "backup", "migration", "testing", "deploy"
    ]
    
    total_files = 0
    
    # 创建模块目录
    for module in modules:
        module_path = os.path.join(BASE_PATH, module)
        os.makedirs(module_path, exist_ok=True)
        
        # 每个模块创建30-50个文件
        files_per_module = random.randint(30, 50)
        
        for i in range(files_per_module):
            mid = f"{module}_{i}"
            filename = f"{module}_{i}.py"
            filepath = os.path.join(module_path, filename)
            
            # 随机选择复杂度
            complexity = random.randint(1, 3)
            
            # 生成代码
            code = generate_random_code(mid, complexity)
            
            # 随机添加一些特殊内容
            if random.random() < 0.1:  # 10%概率添加docstring
                code = f'"""\n模块 {mid} 的文档\n"""\n' + code
            
            if random.random() < 0.05:  # 5%概率添加导入
                imports = random.choice([
                    "import os\nimport sys\n",
                    "from typing import List, Dict, Any\n",
                    "import asyncio\n",
                ])
                code = imports + "\n" + code
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(code)
            
            total_files += 1
    
    # 添加边缘情况文件
    for filename, content in EDGE_CASE_FILES.items():
        filepath = os.path.join(BASE_PATH, filename)
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            total_files += 1
        except Exception as e:
            print(f"⚠️ 边缘文件 {filename} 失败: {e}")
    
    # 创建__init__.py文件
    for module in modules:
        init_path = os.path.join(BASE_PATH, module, "__init__.py")
        with open(init_path, 'w') as f:
            f.write(f'"""模块 {module} """\n')
        total_files += 1
    
    # 创建根目录的__init__.py
    with open(os.path.join(BASE_PATH, "__init__.py"), 'w') as f:
        f.write('"""Mega chaos test project"""')
    total_files += 1
    
    # 创建一些特殊文件
    special_files = [
        ("setup.py", """from setuptools import setup, find_packages
setup(
    name="mega-chaos",
    version="1.0.0",
    packages=find_packages(),
)"""),
        ("conftest.py", """import pytest
@pytest.fixture
def mock_data():
    return {"key": "value"}
"""),
        ("__main__.py", """def main():
    print("Mega chaos main")

if __name__ == "__main__":
    main()
"""),
    ]
    
    for filename, content in special_files:
        filepath = os.path.join(BASE_PATH, filename)
        with open(filepath, 'w') as f:
            f.write(content)
        total_files += 1
    
    print(f"✅ 超大规模测试项目创建完成!")
    print(f"   - 总文件数: {total_files}")
    print(f"   - 模块数: {len(modules)}")
    print(f"   - 位置: {BASE_PATH}")
    
    return total_files

if __name__ == "__main__":
    create_mega_project()
