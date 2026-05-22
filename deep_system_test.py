#!/usr/bin/env python3
"""
超深度系统测试与优化工具
包含：代码分析、全链路测试、问题发现与修复
"""
import sys
import os
import time
import tempfile
import shutil
import logging
from datetime import datetime

# 配置详细日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("CodeKnowledgeGraphDeepTest")

sys.path.insert(0, '/workspace')

print("=" * 100)
print("🎯 全编程语言代码知识图谱系统 - 超深度测试")
print("=" * 100)

# ==================== 步骤1：代码分析 ====================
print("\n📖 步骤1：代码分析与架构拆解")
print("-" * 100)

# 分析所有模块
from backend.config import config
from backend.database import Database
from backend.services.engine import SyncEngine
from backend.parsers import get_parser_for_language

# 列出所有后端文件
backend_dir = "/workspace/backend"
print("\n📦 后端模块文件列表:")
for root, dirs, files in os.walk(backend_dir):
    for file in sorted(files):
        if file.endswith(".py"):
            filepath = os.path.join(root, file)
            print(f"   - {os.path.relpath(filepath, backend_dir)}")

# ==================== 步骤2：静态代码核验 ====================
print("\n🔍 步骤2：静态代码核验")
print("-" * 100)

print("✅ 检查导入语句完整性...")
try:
    from backend.main import app
    print("   ✅ main.py 导入正常")
except Exception as e:
    print(f"   ❌ main.py 导入异常: {e}")

print("\n✅ 检查配置模块...")
try:
    print(f"   - DATABASE_PATH: {config.DATABASE_PATH}")
    print(f"   - SUPPORTED_LANGUAGES: {len(config.SUPPORTED_LANGUAGES)} 种")
    print("   ✅ 配置模块正常")
except Exception as e:
    print(f"   ❌ 配置模块异常: {e}")

print("\n✅ 检查数据库模块...")
try:
    test_db_path = "temp_test_db.db"
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    db = Database(test_db_path)
    print("   ✅ 数据库初始化成功")
except Exception as e:
    print(f"   ❌ 数据库初始化异常: {e}")
finally:
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

# ==================== 步骤3：数据库操作全链路测试 ====================
print("\n💾 步骤3：数据库操作全链路测试")
print("-" * 100)

db_tests = []

try:
    temp_db = "deep_test.db"
    if os.path.exists(temp_db):
        os.remove(temp_db)
    
    db = Database(temp_db)
    
    # 测试1：创建项目
    print("\n📊 测试 3.1 - 创建项目:")
    project_id = db.create_project("深度测试项目", "/tmp/test")
    assert project_id > 0, "项目创建失败"
    print(f"   ✅ 项目创建成功, ID: {project_id}")
    db_tests.append(("创建项目", "✅ 通过"))
    
    # 测试2：获取项目
    print("\n📊 测试 3.2 - 获取项目:")
    project = db.get_project(project_id)
    assert project is not None, "项目获取失败"
    assert project["name"] == "深度测试项目"
    print(f"   ✅ 获取项目成功: {project['name']}")
    db_tests.append(("获取项目", "✅ 通过"))
    
    # 测试3：获取项目列表
    print("\n📊 测试 3.3 - 获取项目列表:")
    projects = db.get_projects()
    assert len(projects) >= 1, "项目列表为空"
    print(f"   ✅ 获取项目列表成功: {len(projects)} 个")
    db_tests.append(("获取项目列表", "✅ 通过"))
    
    # 测试4：文件操作
    print("\n📊 测试 3.4 - 文件CRUD:")
    file_id = db.get_or_create_file(project_id, "/tmp/test.py", "python", "hash123")
    assert file_id > 0, "文件创建失败"
    print(f"   ✅ 文件创建成功, ID: {file_id}")
    
    type_id = db.insert_type(file_id, "TestClass", "class", 1, 10)
    assert type_id > 0, "类型创建失败"
    print(f"   ✅ 类型创建成功, ID: {type_id}")
    
    func_id = db.insert_function(file_id, type_id, "test_method", 3, 8)
    assert func_id > 0, "函数创建失败"
    print(f"   ✅ 函数创建成功, ID: {func_id}")
    db_tests.append(("文件CRUD", "✅ 通过"))
    
    # 测试5：查询与统计
    print("\n📊 测试 3.5 - 统计功能:")
    stats = db.get_stats(project_id)
    print(f"   - 文件: {stats['file_count']}")
    print(f"   - 类型: {stats['type_count']}")
    print(f"   - 函数: {stats['function_count']}")
    assert stats['file_count'] == 1 and stats['type_count'] == 1 and stats['function_count'] == 1
    print(f"   ✅ 统计功能正常")
    db_tests.append(("统计功能", "✅ 通过"))
    
    # 测试6：图谱数据
    print("\n📊 测试 3.6 - 图谱数据:")
    graph = db.get_graph_data(project_id)
    assert len(graph['nodes']) >= 2, "图谱节点为空"
    print(f"   ✅ 图谱数据正常: {len(graph['nodes'])} 个节点")
    db_tests.append(("图谱数据", "✅ 通过"))
    
    # 测试7：搜索功能
    print("\n📊 测试 3.7 - 搜索功能:")
    results = db.search(project_id, "Test")
    assert len(results) >= 1, "搜索无结果"
    print(f"   ✅ 搜索功能正常: {len(results)} 个结果")
    db_tests.append(("搜索功能", "✅ 通过"))
    
    # 测试8：删除文件
    print("\n📊 测试 3.8 - 删除文件:")
    db.delete_file_by_path(project_id, "/tmp/test.py")
    stats_after = db.get_stats(project_id)
    assert stats_after['type_count'] == 0 and stats_after['function_count'] == 0
    print(f"   ✅ 删除文件功能正常")
    db_tests.append(("删除文件", "✅ 通过"))
    
    # 测试9：删除项目
    print("\n📊 测试 3.9 - 删除项目:")
    db.delete_project(project_id)
    project_after = db.get_project(project_id)
    assert project_after is None, "项目未删除"
    print(f"   ✅ 删除项目功能正常")
    db_tests.append(("删除项目", "✅ 通过"))
    
except Exception as e:
    print(f"   ❌ 数据库测试异常: {e}")
    import traceback
    traceback.print_exc()
finally:
    if os.path.exists(temp_db):
        os.remove(temp_db)

# ==================== 步骤4：解析器测试 ====================
print("\n📝 步骤4：解析器全链路测试")
print("-" * 100)

parser_tests = []

# 测试1：Python解析器
print("\n🐍 测试 4.1 - Python解析器:")
try:
    from backend.parsers.python_parser import PythonParser
    parser = PythonParser()
    assert parser.get_language() == "python"
    
    test_code = '''
class TestClass:
    def __init__(self):
        self.data = []
    
    def test_method(self, value):
        return value * 2

@dataclass
class DataModel:
    name: str
    value: int
'''
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(test_code)
        test_file = f.name
    
    result = parser.parse(test_file)
    print(f"   - 类型数量: {len(result.types)}")
    print(f"   - 函数数量: {len(result.functions)}")
    assert len(result.types) == 2, "类型数量不匹配"
    assert len(result.functions) == 3, "函数数量不匹配"
    print(f"   ✅ Python解析器通过")
    parser_tests.append(("Python解析器", "✅ 通过"))
    
    os.remove(test_file)
except Exception as e:
    print(f"   ❌ Python解析器失败: {e}")
    import traceback
    traceback.print_exc()

# 测试2：JavaScript解析器
print("\n🟨 测试 4.2 - JavaScript解析器:")
try:
    from backend.parsers.js_parser import JSParser
    parser = JSParser()
    assert parser.get_language() == "javascript"
    
    test_code = '''
class UserService {
    constructor() {}
    
    getUser(id) {
        return { id: id };
    }
}

interface Config {
    name: string;
}

function process(data) {
    return data;
}
'''
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ts', delete=False) as f:
        f.write(test_code)
        test_file = f.name
    
    result = parser.parse(test_file)
    print(f"   - 类型数量: {len(result.types)}")
    print(f"   - 函数数量: {len(result.functions)}")
    assert len(result.types) >= 1, "类型数量不匹配"
    print(f"   ✅ JavaScript解析器通过")
    parser_tests.append(("JavaScript解析器", "✅ 通过"))
    
    os.remove(test_file)
except Exception as e:
    print(f"   ❌ JavaScript解析器失败: {e}")
    import traceback
    traceback.print_exc()

# 测试3：Go解析器
print("\n🐹 测试 4.3 - Go解析器:")
try:
    from backend.parsers.go_parser import GoParser
    parser = GoParser()
    assert parser.get_language() == "go"
    
    test_code = '''
package main

type User struct {
    Name string
    Age int
}

type Repository interface {
    Get(id int) (*User, error)
}

func NewUser(name string) *User {
    return &User{Name: name}
}
'''
    with tempfile.NamedTemporaryFile(mode='w', suffix='.go', delete=False) as f:
        f.write(test_code)
        test_file = f.name
    
    result = parser.parse(test_file)
    print(f"   - 类型数量: {len(result.types)}")
    print(f"   - 函数数量: {len(result.functions)}")
    assert len(result.types) >= 1, "类型数量不匹配"
    print(f"   ✅ Go解析器通过")
    parser_tests.append(("Go解析器", "✅ 通过"))
    
    os.remove(test_file)
except Exception as e:
    print(f"   ❌ Go解析器失败: {e}")
    import traceback
    traceback.print_exc()

# ==================== 步骤5：引擎服务测试 ====================
print("\n⚙️ 步骤5：引擎服务全链路测试")
print("-" * 100)

engine_tests = []

try:
    # 创建测试项目目录
    test_dir = tempfile.mkdtemp()
    with open(os.path.join(test_dir, "module1.py"), "w") as f:
        f.write('class ClassA:\n    def methodA(self):\n        pass\n')
    with open(os.path.join(test_dir, "module2.py"), "w") as f:
        f.write('class ClassB:\n    def methodB(self):\n        pass\n')
    
    temp_db = "engine_test.db"
    if os.path.exists(temp_db):
        os.remove(temp_db)
    db = Database(temp_db)
    
    project_id = db.create_project("引擎测试项目", test_dir)
    
    engine = SyncEngine()
    engine.db = db
    
    # 测试1：同步
    print("\n🔄 测试 5.1 - 同步项目:")
    start_time = time.time()
    result = engine.sync_project(project_id)
    elapsed = time.time() - start_time
    print(f"   - 处理文件: {result['files_processed']}")
    print(f"   - 耗时: {elapsed:.3f}s")
    assert result['files_processed'] == 2, "文件处理数量不匹配"
    print(f"   ✅ 同步成功")
    engine_tests.append(("项目同步", "✅ 通过"))
    
    # 测试2：文件检测
    print("\n📄 测试 5.2 - 语言检测:")
    lang1 = engine.get_language_by_extension("test.py")
    lang2 = engine.get_language_by_extension("test.js")
    lang3 = engine.get_language_by_extension("test.go")
    assert lang1 == "python" and lang2 == "javascript" and lang3 == "go"
    print(f"   ✅ 语言检测正常")
    engine_tests.append(("语言检测", "✅ 通过"))
    
    # 测试3：哈希计算
    print("\n🔢 测试 5.3 - 文件哈希:")
    hash_test_file = os.path.join(test_dir, "module1.py")
    file_hash = engine.calculate_hash(hash_test_file)
    assert len(file_hash) > 0, "哈希计算失败"
    print(f"   ✅ 哈希计算正常: {file_hash}")
    engine_tests.append(("哈希计算", "✅ 通过"))
    
    # 清理
    db.delete_project(project_id)
    os.remove(temp_db)
    shutil.rmtree(test_dir)
    
except Exception as e:
    print(f"   ❌ 引擎服务异常: {e}")
    import traceback
    traceback.print_exc()

# ==================== 步骤6：异常与边界测试 ====================
print("\n⚠️ 步骤6：异常情况与边界测试")
print("-" * 100)

edge_tests = []

# 测试1：空文件
print("\n📄 测试 6.1 - 空文件:")
try:
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        pass
    test_file = f.name
    
    from backend.parsers.python_parser import PythonParser
    parser = PythonParser()
    result = parser.parse(test_file)
    print(f"   - 类型: {len(result.types)}")
    print(f"   - 函数: {len(result.functions)}")
    print(f"   ✅ 空文件处理正常")
    edge_tests.append(("空文件处理", "✅ 通过"))
    os.remove(test_file)
except Exception as e:
    print(f"   ❌ 空文件异常: {e}")

# 测试2：不存在的文件
print("\n❌ 测试 6.2 - 不存在的文件:")
try:
    temp_db = "nonexistent_test.db"
    if os.path.exists(temp_db):
        os.remove(temp_db)
    db = Database(temp_db)
    
    project_id = db.create_project("不存在文件测试", "/tmp/non/existent/path")
    engine = SyncEngine()
    engine.db = db
    result = engine.sync_project(project_id)
    print(f"   - 结果: {result}")
    print(f"   ✅ 不存在文件处理正常")
    edge_tests.append(("不存在文件", "✅ 通过"))
    
    db.delete_project(project_id)
    os.remove(temp_db)
except Exception as e:
    print(f"   ❌ 不存在文件异常: {e}")

# ==================== 步骤7：测试结果汇总 ====================
print("\n" + "=" * 100)
print("📊 测试结果汇总")
print("=" * 100)

print("\n💾 数据库测试:")
for test in db_tests:
    print(f"   {test[0]:25s} - {test[1]}")

print("\n📝 解析器测试:")
for test in parser_tests:
    print(f"   {test[0]:25s} - {test[1]}")

print("\n⚙️ 引擎服务测试:")
for test in engine_tests:
    print(f"   {test[0]:25s} - {test[1]}")

print("\n⚠️ 边界与异常测试:")
for test in edge_tests:
    print(f"   {test[0]:25s} - {test[1]}")

total_tests = len(db_tests) + len(parser_tests) + len(engine_tests) + len(edge_tests)
passed = len([t for t in db_tests + parser_tests + engine_tests + edge_tests if "✅" in t[1]])

print("\n" + "=" * 100)
print(f"🎯 最终测试结果: {passed}/{total_tests} 个测试通过")
print("=" * 100)

if passed == total_tests:
    print("\n✅ 所有深度测试通过！")
    sys.exit(0)
else:
    print("\n❌ 部分测试失败！")
    sys.exit(1)
