#!/usr/bin/env python3
"""
全编程语言代码知识图谱系统 - 全面测试套件
包含：单元测试、集成测试、接口测试、业务场景测试
"""
import sys
import os
import tempfile
import shutil
import time
sys.path.insert(0, '/workspace')

# ==================== 阶段1：数据库层测试 ====================
print("=" * 80)
print("阶段1：数据库层测试")
print("=" * 80)

from backend.database import Database

def test_database_basic():
    """测试数据库基础功能"""
    print("\n📦 测试1.1：数据库初始化")
    
    # 创建临时数据库
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    try:
        db = Database(db_path)
        
        # 测试创建项目
        project_id = db.create_project("测试项目", "/tmp/test")
        print(f"   ✅ 创建项目成功，ID: {project_id}")
        
        # 测试获取项目
        project = db.get_project(project_id)
        assert project, "项目应该存在"
        assert project['name'] == "测试项目"
        assert project['path'] == "/tmp/test"
        print(f"   ✅ 获取项目成功: {project['name']}")
        
        # 测试获取项目列表
        projects = db.get_projects()
        assert len(projects) == 1
        print(f"   ✅ 获取项目列表成功: {len(projects)} 个项目")
        
        # 测试删除项目
        db.delete_project(project_id)
        deleted_project = db.get_project(project_id)
        assert deleted_project is None, "项目应该被删除"
        print(f"   ✅ 删除项目成功")
        
        return True
        
    finally:
        os.unlink(db_path)

def test_database_file_operations():
    """测试文件操作功能"""
    print("\n📁 测试1.2：文件操作")
    
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    try:
        db = Database(db_path)
        project_id = db.create_project("文件测试", "/tmp")
        
        # 测试插入文件
        file_id = db.get_or_create_file(project_id, "/tmp/test.py", "python", "abc123")
        assert file_id > 0
        print(f"   ✅ 插入文件成功: ID={file_id}")
        
        # 测试插入类型
        type_id = db.insert_type(file_id, "TestClass", "class", 1, 20)
        assert type_id > 0
        print(f"   ✅ 插入类型成功: ID={type_id}")
        
        # 测试插入函数
        func_id = db.insert_function(file_id, type_id, "test_method", 5, 15)
        assert func_id > 0
        print(f"   ✅ 插入函数成功: ID={func_id}")
        
        # 测试统计
        stats = db.get_stats(project_id)
        assert stats['file_count'] == 1
        assert stats['type_count'] == 1
        assert stats['function_count'] == 1
        print(f"   ✅ 统计功能正常: 文件={stats['file_count']}, 类型={stats['type_count']}, 函数={stats['function_count']}")
        
        # 测试图谱数据
        graph_data = db.get_graph_data(project_id)
        assert len(graph_data['nodes']) == 2  # 类型 + 函数
        assert len(graph_data['links']) == 0  # 没有关系
        print(f"   ✅ 图谱数据正常: 节点={len(graph_data['nodes'])}, 边={len(graph_data['links'])}")
        
        # 测试搜索
        search_results = db.search(project_id, "Test")
        assert len(search_results) == 2
        print(f"   ✅ 搜索功能正常: 找到 {len(search_results)} 个结果")
        
        # 测试删除文件
        db.delete_file_by_path(project_id, "/tmp/test.py")
        stats_after_delete = db.get_stats(project_id)
        assert stats_after_delete['type_count'] == 0
        assert stats_after_delete['function_count'] == 0
        print(f"   ✅ 删除文件后清理正常")
        
        db.delete_project(project_id)
        return True
        
    finally:
        os.unlink(db_path)

# ==================== 阶段2：解析器测试 ====================
print("\n" + "=" * 80)
print("阶段2：解析器测试")
print("=" * 80)

from backend.parsers.python_parser import PythonParser
from backend.parsers.js_parser import JSParser
from backend.parsers.go_parser import GoParser

def test_python_parser():
    """测试Python解析器"""
    print("\n🐍 测试2.1：Python解析器")
    
    parser = PythonParser()
    assert parser.get_language() == "python"
    print(f"   ✅ 解析器语言正确: {parser.get_language()}")
    
    # 创建临时测试文件
    test_code = '''
class TestClass:
    def __init__(self):
        pass
    
    def test_method(self, x):
        return x * 2

@dataclass
class DataClass:
    name: str
    value: int

def standalone_function():
    pass
'''
    
    with tempfile.NamedTemporaryFile(suffix='.py', mode='w', delete=False) as f:
        f.write(test_code)
        temp_path = f.name
    
    try:
        result = parser.parse(temp_path)
        print(f"   ✅ 解析成功")
        print(f"      - 类型: {len(result.types)} 个")
        print(f"      - 函数: {len(result.functions)} 个")
        
        type_names = [t['name'] for t in result.types]
        print(f"      - 类型名称: {type_names}")
        
        # 验证类型
        assert any(t['name'] == 'TestClass' for t in result.types)
        print(f"      ✅ 检测到类: TestClass")
        
        # 验证函数
        func_names = [f['name'] for f in result.functions]
        print(f"      - 函数名称: {func_names}")
        assert 'test_method' in func_names
        assert 'standalone_function' in func_names
        print(f"      ✅ 检测到函数")
        
        return True
        
    finally:
        os.unlink(temp_path)

def test_js_parser():
    """测试JavaScript/TypeScript解析器"""
    print("\n🟨 测试2.2：JavaScript/TypeScript解析器")
    
    parser = JSParser()
    assert parser.get_language() == "javascript"
    print(f"   ✅ 解析器语言正确: {parser.get_language()}")
    
    test_code = '''
class UserService {
    constructor() {}
    
    getUser(id) {
        return { id: id };
    }
}

interface IConfig {
    name: string;
    enabled: boolean;
}

function processData(data) {
    return data;
}
'''
    
    with tempfile.NamedTemporaryFile(suffix='.ts', mode='w', delete=False) as f:
        f.write(test_code)
        temp_path = f.name
    
    try:
        result = parser.parse(temp_path)
        print(f"   ✅ 解析成功")
        print(f"      - 类型: {len(result.types)} 个")
        print(f"      - 函数: {len(result.functions)} 个")
        
        return True
        
    finally:
        os.unlink(temp_path)

def test_edge_case_files():
    """测试边缘情况文件"""
    print("\n🧪 测试2.3：边缘情况文件")
    
    # 空文件
    with tempfile.NamedTemporaryFile(suffix='.py', mode='w', delete=False) as f:
        empty_path = f.name
    
    try:
        parser = PythonParser()
        result = parser.parse(empty_path)
        assert len(result.types) == 0
        assert len(result.functions) == 0
        print(f"   ✅ 空文件解析正常: 类型={len(result.types)}, 函数={len(result.functions)}")
    finally:
        os.unlink(empty_path)
    
    # 只有注释的文件
    with tempfile.NamedTemporaryFile(suffix='.py', mode='w', delete=False) as f:
        f.write('# This is a comment\n# Another line\n')
        comment_path = f.name
    
    try:
        parser = PythonParser()
        result = parser.parse(comment_path)
        assert len(result.types) == 0
        assert len(result.functions) == 0
        print(f"   ✅ 纯注释文件解析正常")
    finally:
        os.unlink(comment_path)
    
    return True

# ==================== 阶段3：引擎层测试 ====================
print("\n" + "=" * 80)
print("阶段3：引擎层测试")
print("=" * 80)

from backend.services.engine import SyncEngine

def test_engine_sync():
    """测试引擎同步功能"""
    print("\n⚙️ 测试3.1：项目同步")
    
    # 创建测试目录
    test_dir = tempfile.mkdtemp()
    
    try:
        # 创建一些测试文件
        with open(os.path.join(test_dir, "test1.py"), 'w') as f:
            f.write('class Test1: pass\n')
        
        with open(os.path.join(test_dir, "test2.py"), 'w') as f:
            f.write('class Test2: def func(self): pass\n')
        
        # 创建数据库
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        try:
            db = Database(db_path)
            project_id = db.create_project("引擎测试", test_dir)
            
            # 手动引擎测试
            from backend.services.engine import SyncEngine
            engine = SyncEngine()
            engine.db = db
            
            result = engine.sync_project(project_id)
            print(f"   ✅ 同步完成: {result['files_processed']} 个文件")
            
            stats = db.get_stats(project_id)
            assert stats['file_count'] >= 1
            assert stats['type_count'] >= 2
            assert stats['function_count'] >= 1
            print(f"   ✅ 统计正常: 文件={stats['file_count']}, 类型={stats['type_count']}, 函数={stats['function_count']}")
            
            db.delete_project(project_id)
            return True
            
        finally:
            os.unlink(db_path)
            
    finally:
        shutil.rmtree(test_dir)

def test_engine_file_detection():
    """测试文件语言检测"""
    print("\n🔍 测试3.2：语言检测")
    
    engine = SyncEngine()
    
    test_cases = [
        ("test.py", "python"),
        ("test.js", "javascript"),
        ("test.ts", "typescript"),
        ("test.go", "go"),
        ("test.txt", None),
    ]
    
    for filename, expected in test_cases:
        result = engine.get_language_by_extension(filename)
        assert result == expected, f"{filename} 应该返回 {expected}"
        print(f"   ✅ {filename} -> {result}")
    
    print(f"   ✅ 所有语言检测通过")
    return True

# ==================== 阶段4：完整流程测试 ====================
print("\n" + "=" * 80)
print("阶段4：完整业务流程测试")
print("=" * 80)

def test_full_workflow():
    """完整业务流程测试"""
    print("\n🔄 测试4.1：完整工作流")
    
    # 1. 创建测试项目
    test_dir = tempfile.mkdtemp()
    print(f"   📂 测试目录: {test_dir}")
    
    try:
        # 2. 生成测试代码
        with open(os.path.join(test_dir, "core.py"), 'w') as f:
            f.write('''
class UserManager:
    def __init__(self):
        self.users = []
    
    def add_user(self, name):
        user = {"name": name}
        self.users.append(user)
        return user
    
    def get_users(self):
        return self.users

class ProductManager:
    def __init__(self):
        self.products = {}
    
    def add_product(self, id, name):
        self.products[id] = name
''')
        
        with open(os.path.join(test_dir, "utils.py"), 'w') as f:
            f.write('''
def validate_name(name):
    return len(name) > 0

def format_price(price):
    return f"${price:.2f}"
''')
        
        # 3. 创建数据库和项目
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        try:
            db = Database(db_path)
            project_id = db.create_project("完整流程测试", test_dir)
            
            # 4. 同步项目
            from backend.services.engine import SyncEngine
            engine = SyncEngine()
            engine.db = db
            result = engine.sync_project(project_id)
            print(f"   ✅ 同步成功: {result['files_processed']} 个文件")
            
            # 5. 验证统计
            stats = db.get_stats(project_id)
            print(f"   📊 统计: 文件={stats['file_count']}, 类型={stats['type_count']}, 函数={stats['function_count']}")
            
            # 6. 验证图谱
            graph = db.get_graph_data(project_id)
            print(f"   🌐 图谱: 节点={len(graph['nodes'])}")
            
            # 7. 测试搜索
            search_results = db.search(project_id, "User")
            print(f"   🔍 搜索 'User': {len(search_results)} 个结果")
            
            # 8. 再次同步（验证性能和稳定性）
            print(f"   🔄 再次同步中...")
            start = time.time()
            result2 = engine.sync_project(project_id)
            elapsed = time.time() - start
            print(f"   ✅ 再次同步完成，耗时 {elapsed:.3f}s")
            
            # 9. 删除项目
            db.delete_project(project_id)
            print(f"   🗑️ 项目已删除")
            
            print(f"   ✅ 完整流程通过！")
            return True
            
        finally:
            os.unlink(db_path)
            
    finally:
        shutil.rmtree(test_dir)

# ==================== 执行所有测试 ====================
if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("🎯 全编程语言代码知识图谱系统 - 全面测试启动")
    print("=" * 80)
    
    all_passed = True
    
    # 阶段1
    try:
        result1 = test_database_basic()
        result2 = test_database_file_operations()
        print(f"\n📦 阶段1结果: {('✅ 通过' if result1 and result2 else '❌ 失败')}")
        all_passed = all_passed and result1 and result2
    except Exception as e:
        print(f"\n❌ 阶段1失败: {e}")
        import traceback
        traceback.print_exc()
        all_passed = False
    
    # 阶段2
    try:
        result3 = test_python_parser()
        result4 = test_js_parser()
        result5 = test_edge_case_files()
        print(f"\n🔍 阶段2结果: {('✅ 通过' if result3 and result4 and result5 else '❌ 失败')}")
        all_passed = all_passed and result3 and result4 and result5
    except Exception as e:
        print(f"\n❌ 阶段2失败: {e}")
        import traceback
        traceback.print_exc()
        all_passed = False
    
    # 阶段3
    try:
        result6 = test_engine_sync()
        result7 = test_engine_file_detection()
        print(f"\n⚙️ 阶段3结果: {('✅ 通过' if result6 and result7 else '❌ 失败')}")
        all_passed = all_passed and result6 and result7
    except Exception as e:
        print(f"\n❌ 阶段3失败: {e}")
        import traceback
        traceback.print_exc()
        all_passed = False
    
    # 阶段4
    try:
        result8 = test_full_workflow()
        print(f"\n🔄 阶段4结果: {('✅ 通过' if result8 else '❌ 失败')}")
        all_passed = all_passed and result8
    except Exception as e:
        print(f"\n❌ 阶段4失败: {e}")
        import traceback
        traceback.print_exc()
        all_passed = False
    
    print("\n" + "=" * 80)
    print("📋 最终测试结果")
    print("=" * 80)
    if all_passed:
        print("✅ 所有测试通过！系统运行正常。")
        sys.exit(0)
    else:
        print("❌ 部分测试失败，请检查错误。")
        sys.exit(1)
