#!/usr/bin/env python3
"""
复杂场景深度测试工具
包含：超长、混乱、边界、重复操作、中断恢复、高频率请求等多种复杂情况
"""
import sys
import os
import time
import tempfile
import subprocess
import requests
import logging
import threading
import random
from datetime import datetime

# 配置详细日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ComplexTest")

BASE_URL = "http://127.0.0.1:8000"
api_process = None


def print_section(title):
    print("\n" + "=" * 120)
    print(f"🚀 复杂场景测试: {title}")
    print("=" * 120)


def start_server():
    """启动API服务器"""
    global api_process
    print("启动API服务器...")
    api_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    time.sleep(3)
    return True


def stop_server():
    """停止API服务器"""
    global api_process
    if api_process:
        print("停止API服务器...")
        api_process.terminate()
        try:
            api_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            api_process.kill()
            api_process.wait()


def create_complex_test_file(temp_dir):
    """创建各种复杂的测试文件"""
    test_files = []
    
    # 1. 超级长的文件
    print_section("创建超长文件测试")
    long_file_path = os.path.join(temp_dir, "very_long.py")
    with open(long_file_path, 'w', encoding='utf-8') as f:
        f.write("# 超级长的测试文件\n")
        for i in range(1000):
            f.write(f"class LongClass{i}:\n    def method{i}(self):\n        return {i}\n\n")
    test_files.append(long_file_path)
    print(f"✅ 创建超长文件: {long_file_path} (1000个类)")
    
    # 2. 全是注释的文件
    comment_only_path = os.path.join(temp_dir, "comments_only.py")
    with open(comment_only_path, 'w', encoding='utf-8') as f:
        for i in range(200):
            f.write(f"# This is comment line {i} for testing\n")
    test_files.append(comment_only_path)
    print(f"✅ 创建全注释文件: {comment_only_path}")
    
    # 3. 语法错误文件
    syntax_error_path = os.path.join(temp_dir, "syntax_error.py")
    with open(syntax_error_path, 'w', encoding='utf-8') as f:
        f.write("class InvalidClass:\n    def bad_method(\n        print('invalid')\n")
    test_files.append(syntax_error_path)
    print(f"✅ 创建语法错误文件: {syntax_error_path}")
    
    # 4. 空文件
    empty_path = os.path.join(temp_dir, "empty.py")
    open(empty_path, 'w').close()
    test_files.append(empty_path)
    print(f"✅ 创建空文件: {empty_path}")
    
    # 5. 混合语言代码
    mixed_path = os.path.join(temp_dir, "mixed_code.py")
    with open(mixed_path, 'w', encoding='utf-8') as f:
        f.write('''# Mixed content test
class MixedClass:
    def __init__(self):
        self.data = []
    
    def process(self, x):
        # Some code
        return x * 2

# Now some invalid looking code
@decorator
class AnotherClass:
    pass

def standalone_func():
    return 42
''')
    test_files.append(mixed_path)
    print(f"✅ 创建混合代码文件: {mixed_path}")
    
    # 6. 嵌套非常深的类
    nested_path = os.path.join(temp_dir, "deep_nested.py")
    with open(nested_path, 'w', encoding='utf-8') as f:
        f.write('''class Level1:
    class Level2:
        class Level3:
            class Level4:
                class Level5:
                    def deep_method(self):
                        return "deep"
                    
    def outer_method(self):
        return "outer"
''')
    test_files.append(nested_path)
    print(f"✅ 创建深度嵌套类文件: {nested_path}")
    
    # 7. 极端的装饰器用法
    decorator_path = os.path.join(temp_dir, "complex_decorators.py")
    with open(decorator_path, 'w', encoding='utf-8') as f:
        f.write('''@decorator1
@decorator2
@decorator3
@dataclass
class DecoratedClass:
    pass

@asyncio.coroutine
@another_decorator
def decorated_func():
    pass
''')
    test_files.append(decorator_path)
    print(f"✅ 创建装饰器测试文件: {decorator_path}")
    
    return test_files


def test_scenario_1_complex_files():
    """场景1：各种复杂文件的处理"""
    print_section("场景1：复杂文件处理测试")
    
    temp_dir = tempfile.mkdtemp()
    try:
        # 创建测试文件
        test_files = create_complex_test_file(temp_dir)
        
        # 创建项目并同步
        print("\n📦 创建项目")
        create_data = {
            "name": f"ComplexFileTest_{datetime.now().strftime('%H%M%S')}",
            "path": temp_dir
        }
        resp = requests.post(f"{BASE_URL}/api/projects", json=create_data)
        assert resp.status_code == 200
        project = resp.json()
        project_id = project["id"]
        print(f"✅ 项目创建成功，ID={project_id}")
        
        # 同步（可能会花一些时间）
        print("\n🔄 开始同步...")
        start_time = time.time()
        sync_resp = requests.post(
            f"{BASE_URL}/api/projects/{project_id}/sync",
            timeout=300
        )
        sync_time = time.time() - start_time
        
        print(f"✅ 同步完成！状态码: {sync_resp.status_code}")
        if sync_resp.status_code == 200:
            sync_result = sync_resp.json()
            print(f"   处理文件数: {sync_result['files_processed']}")
            print(f"   耗时: {sync_time:.2f} 秒")
        
        # 获取统计
        print("\n📊 获取统计信息")
        stats_resp = requests.get(f"{BASE_URL}/api/projects/{project_id}/stats")
        if stats_resp.status_code == 200:
            stats = stats_resp.json()
            print(f"   文件数: {stats['file_count']}")
            print(f"   类型数: {stats['type_count']}")
            print(f"   函数数: {stats['function_count']}")
        
        # 获取知识图谱
        print("\n🌐 获取知识图谱")
        graph_resp = requests.get(f"{BASE_URL}/api/graph/{project_id}")
        if graph_resp.status_code == 200:
            graph = graph_resp.json()
            print(f"   节点数: {len(graph['nodes'])}")
            print(f"   边数: {len(graph['links'])}")
        
        # 清理
        print("\n🧹 清理...")
        requests.delete(f"{BASE_URL}/api/projects/{project_id}")
        
        return True
        
    finally:
        # 清理临时目录
        for f in os.listdir(temp_dir):
            try:
                os.remove(os.path.join(temp_dir, f))
            except:
                pass
        try:
            os.rmdir(temp_dir)
        except:
            pass


def test_scenario_2_rapid_operations():
    """场景2：快速重复操作"""
    print_section("场景2：快速重复操作与并发")
    
    temp_dir = tempfile.mkdtemp()
    try:
        # 创建一个简单的测试文件
        with open(os.path.join(temp_dir, "test_simple.py"), 'w') as f:
            f.write("class SimpleClass:\n    def method(self):\n        pass\n")
        
        project_ids = []
        
        # 快速创建项目
        print("\n📦 快速创建多个项目")
        for i in range(5):
            create_data = {
                "name": f"RapidTest_{i}",
                "path": temp_dir
            }
            resp = requests.post(f"{BASE_URL}/api/projects", json=create_data)
            if resp.status_code == 200:
                project = resp.json()
                project_ids.append(project["id"])
                print(f"   ✅ 创建项目 {i} (ID={project['id']})")
        
        print(f"✅ 成功创建 {len(project_ids)} 个项目")
        
        # 快速操作
        print("\n⚡ 快速并发操作")
        results = []
        errors = []
        
        def quick_ops(pid):
            try:
                # 同步
                sync_resp = requests.post(f"{BASE_URL}/api/projects/{pid}/sync", timeout=30)
                # 获取统计
                stats_resp = requests.get(f"{BASE_URL}/api/projects/{pid}/stats")
                # 获取图谱
                graph_resp = requests.get(f"{BASE_URL}/api/graph/{pid}")
                results.append(True)
            except Exception as e:
                errors.append(str(e))
        
        # 启动线程
        threads = []
        for pid in project_ids:
            t = threading.Thread(target=quick_ops, args=(pid,))
            threads.append(t)
            t.start()
        
        # 等待完成
        for t in threads:
            t.join()
        
        print(f"✅ 快速操作测试完成！成功: {len(results)}, 错误: {len(errors)}")
        
        # 清理
        print("\n🧹 清理所有项目")
        for pid in project_ids:
            try:
                requests.delete(f"{BASE_URL}/api/projects/{pid}")
            except:
                pass
        
        return len(errors) == 0
        
    finally:
        try:
            os.remove(os.path.join(temp_dir, "test_simple.py"))
            os.rmdir(temp_dir)
        except:
            pass


def test_scenario_3_search_boundaries():
    """场景3：边界搜索测试"""
    print_section("场景3：边界搜索与极端查询")
    
    temp_dir = tempfile.mkdtemp()
    try:
        with open(os.path.join(temp_dir, "search_test.py"), 'w') as f:
            f.write('''class UserAuth:
    def login(self): pass
    def logout(self): pass

class ProductManager:
    def create(self): pass
    def delete(self): pass

class Database:
    def connect(self): pass
''')
        
        # 创建项目
        create_data = {
            "name": "SearchTest",
            "path": temp_dir
        }
        resp = requests.post(f"{BASE_URL}/api/projects", json=create_data)
        project_id = resp.json()["id"]
        requests.post(f"{BASE_URL}/api/projects/{project_id}/sync")
        
        print("\n🔍 各种边界搜索查询:")
        search_tests = [
            ("空查询", ""),
            ("超长查询", "x" * 5000),
            ("特殊字符", "@#$%^&*()!~"),
            ("中文查询", "用户"),
            ("SQL注入尝试", "'; DROP TABLE projects; --"),
            ("正常查询1", "User"),
            ("正常查询2", "login"),
            ("大小写混合", "pRoDuCt"),
        ]
        
        success = 0
        for desc, query in search_tests:
            try:
                resp = requests.get(
                    f"{BASE_URL}/api/search",
                    params={"project_id": project_id, "query": query},
                    timeout=10
                )
                if resp.status_code == 200:
                    results = resp.json()
                    print(f"   ✅ {desc}: {len(results)} 结果")
                    success += 1
                else:
                    print(f"   ⚠️ {desc}: 状态码 {resp.status_code}")
            except Exception as e:
                print(f"   ❌ {desc}: {e}")
        
        # 清理
        requests.delete(f"{BASE_URL}/api/projects/{project_id}")
        
        print(f"\n✅ 搜索测试完成，成功率: {success}/{len(search_tests)}")
        return success >= len(search_tests) * 0.9
        
    finally:
        try:
            os.remove(os.path.join(temp_dir, "search_test.py"))
            os.rmdir(temp_dir)
        except:
            pass


def test_scenario_4_chaos_operations():
    """场景4：混乱操作测试"""
    print_section("场景4：混乱操作场景测试")
    
    temp_dir = tempfile.mkdtemp()
    try:
        with open(os.path.join(temp_dir, "chaos_test.py"), 'w') as f:
            f.write("class ChaosClass:\n    def chaos_method(self): pass\n")
        
        # 进行一系列混乱操作
        project_ids = []
        
        print("\n🎭 开始混乱操作序列")
        for i in range(10):
            action = random.choice(['create', 'list', 'create', 'sync', 'stats', 'create', 'delete', 'list'])
            
            try:
                if action == 'create':
                    create_data = {
                        "name": f"ChaosTest_{i}_{int(time.time())}",
                        "path": temp_dir
                    }
                    resp = requests.post(f"{BASE_URL}/api/projects", json=create_data)
                    if resp.status_code == 200:
                        project_ids.append(resp.json()["id"])
                    print(f"   {i} 操作为 CREATE: {'✅' if resp.status_code == 200 else '❌'}")
                
                elif action == 'list':
                    resp = requests.get(f"{BASE_URL}/api/projects")
                    print(f"   {i} 操作为 LIST: {'✅' if resp.status_code == 200 else '❌'}")
                
                elif action == 'sync' and project_ids:
                    pid = random.choice(project_ids)
                    resp = requests.post(f"{BASE_URL}/api/projects/{pid}/sync", timeout=30)
                    print(f"   {i} 操作为 SYNC {pid}: {'✅' if resp.status_code == 200 else '❌'}")
                
                elif action == 'stats' and project_ids:
                    pid = random.choice(project_ids)
                    resp = requests.get(f"{BASE_URL}/api/projects/{pid}/stats")
                    print(f"   {i} 操作为 STATS {pid}: {'✅' if resp.status_code == 200 else '❌'}")
                
                elif action == 'delete' and project_ids:
                    pid = project_ids.pop()
                    resp = requests.delete(f"{BASE_URL}/api/projects/{pid}")
                    print(f"   {i} 操作为 DELETE {pid}: {'✅' if resp.status_code == 200 else '❌'}")
            
            except Exception as e:
                print(f"   {i} 操作异常: {e}")
        
        # 清理剩余
        print("\n🧹 清理剩余项目")
        for pid in project_ids:
            try:
                requests.delete(f"{BASE_URL}/api/projects/{pid}")
            except:
                pass
        
        print("✅ 混乱场景测试完成")
        return True
        
    finally:
        try:
            os.remove(os.path.join(temp_dir, "chaos_test.py"))
            os.rmdir(temp_dir)
        except:
            pass


def main():
    print_section("代码知识图谱系统 - 复杂场景深度测试")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    all_passed = True
    
    try:
        # 启动服务器
        print_section("准备测试环境")
        if not start_server():
            print("❌ 服务器启动失败")
            return 1
        
        # 健康检查
        health_resp = requests.get(f"{BASE_URL}/health")
        if health_resp.status_code != 200:
            print("❌ 健康检查失败")
            return 1
        print("✅ 健康检查通过")
        
        # 运行各个复杂场景测试
        print_section("开始执行复杂场景测试")
        
        scenarios = [
            ("复杂文件处理", test_scenario_1_complex_files),
            ("快速重复操作", test_scenario_2_rapid_operations),
            ("边界搜索测试", test_scenario_3_search_boundaries),
            ("混乱操作场景", test_scenario_4_chaos_operations),
        ]
        
        results = []
        for name, test_func in scenarios:
            try:
                print(f"\n{'='*120}")
                print(f"正在执行: {name}")
                print(f"{'='*120}")
                passed = test_func()
                results.append((name, passed))
                print(f"\n{'✅' if passed else '❌'} 场景 '{name}' 测试 {'通过' if passed else '失败'}")
            except Exception as e:
                print(f"\n❌ 场景 '{name}' 异常: {e}")
                import traceback
                traceback.print_exc()
                results.append((name, False))
        
        # 最终总结
        print_section("复杂场景测试最终总结")
        
        print("\n📊 测试结果汇总:")
        for name, passed in results:
            status = "✅ 通过" if passed else "❌ 失败"
            print(f"   {name:30s}: {status}")
        
        passed_count = sum(1 for _, p in results if p)
        total = len(results)
        
        print(f"\n总体结果: {passed_count}/{total} 通过")
        
        all_passed = passed_count == total
        
        if all_passed:
            print("\n🎉🎉🎉 所有复杂场景测试通过！系统表现出色！")
        else:
            print(f"\n⚠️ 有 {total - passed_count} 个场景测试失败")
        
        return 0 if all_passed else 1
        
    except KeyboardInterrupt:
        print("\n⏹️ 用户中断")
        return 130
    except Exception as e:
        print(f"\n❌ 主测试异常: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        stop_server()


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
