#!/usr/bin/env python3
"""
第二阶段：长时间压力与并发测试
"""
import sys
import os
import tempfile
import time
import threading
import random
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.config import config
from backend.database import Database
from backend.services.engine import SyncEngine
from backend.parsers import get_parser_for_language

# 初始化
db = Database()
engine = SyncEngine()

def print_section(title):
    print("\n" + "=" * 100)
    print(f"🚀 {title}")
    print("=" * 100)

def create_test_project_files(temp_dir, num_files=10):
    """创建测试项目文件"""
    for i in range(num_files):
        file_path = os.path.join(temp_dir, f"module_{i}.py")
        with open(file_path, 'w') as f:
            f.write(f"""class Class{i}:
    def method1(self):
        pass
    def method2(self):
        pass

def function{i}():
    return {i}
""")

def test_single_project_operations(project_path, project_name):
    """单个项目的操作序列"""
    results = []
    try:
        # 创建项目
        proj_id = db.create_project(project_name, project_path)
        results.append(("create", True))
        
        # 同步项目
        sync_result = engine.sync_project(proj_id)
        results.append(("sync", sync_result['success']))
        
        # 获取项目信息
        project = db.get_project(proj_id)
        results.append(("get", project is not None))
        
        # 获取统计
        stats = db.get_stats(proj_id)
        results.append(("stats", stats is not None))
        
        # 获取图谱
        graph = db.get_graph_data(proj_id)
        results.append(("graph", graph is not None))
        
        # 搜索
        search_results = db.search(proj_id, "Class")
        results.append(("search", True))
        
        # 删除
        db.delete_project(proj_id)
        results.append(("delete", True))
        
    except Exception as e:
        results.append(("error", False))
    
    return results

def test_concurrent_operations(temp_dir, num_threads=10):
    """并发操作测试"""
    print(f"\n🔄 测试并发操作 (线程数: {num_threads})")
    
    threads = []
    all_results = []
    errors = []
    
    def worker(thread_id):
        try:
            proj_name = f"并发测试项目_{thread_id}_{int(time.time())}"
            # 每个线程使用唯一的子目录
            thread_dir = os.path.join(temp_dir, f"thread_{thread_id}")
            os.makedirs(thread_dir, exist_ok=True)
            create_test_project_files(thread_dir, num_files=5)
            
            results = test_single_project_operations(thread_dir, proj_name)
            all_results.extend(results)
            
        except Exception as e:
            errors.append(f"线程 {thread_id}: {e}")
    
    start_time = time.time()
    for i in range(num_threads):
        t = threading.Thread(target=worker, args=(i,))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    elapsed = time.time() - start_time
    
    # 统计
    success_count = sum(1 for _, ok in all_results if ok)
    total = len(all_results)
    
    print(f"\n   📊 并发测试结果:")
    print(f"      - 总操作数: {total}")
    print(f"      - 成功: {success_count}")
    print(f"      - 失败: {total - success_count}")
    print(f"      - 总耗时: {elapsed:.2f}s")
    print(f"      - 平均每线程耗时: {elapsed/num_threads:.2f}s")
    
    if errors:
        print(f"\n   ⚠️ 错误: {len(errors)} 个")
        for err in errors[:5]:  # 只显示前5个
            print(f"      - {err}")
        if len(errors) > 5:
            print(f"      ... 还有 {len(errors) - 5} 个")
    
    return len(errors) == 0, errors

def test_rapid_sequential_operations(temp_dir, num_iterations=50):
    """快速连续操作测试"""
    print(f"\n⚡ 快速连续操作 (迭代次数: {num_iterations})")
    
    errors = []
    start_time = time.time()
    
    for i in range(num_iterations):
        try:
            proj_name = f"快速测试_{i}_{int(time.time())}"
            proj_id = db.create_project(proj_name, temp_dir)
            # 同步一下
            engine.sync_project(proj_id)
            # 获取项目
            _ = db.get_project(proj_id)
            # 删除
            db.delete_project(proj_id)
            
            if (i + 1) % 10 == 0:
                print(f"      ... 完成 {i + 1}/{num_iterations}")
                
        except Exception as e:
            errors.append(f"迭代 {i}: {e}")
    
    elapsed = time.time() - start_time
    
    print(f"\n   📊 快速操作结果:")
    print(f"      - 总迭代: {num_iterations}")
    print(f"      - 错误: {len(errors)}")
    print(f"      - 耗时: {elapsed:.2f}s")
    print(f"      - 平均每个迭代: {elapsed/num_iterations:.4f}s")
    
    return len(errors) == 0

def test_long_running_project_sync(temp_dir, num_files=100):
    """长时间同步测试"""
    print(f"\n🔧 长时间同步测试 (文件数: {num_files})")
    
    # 创建很多文件
    print(f"   📄 创建 {num_files} 个测试文件...")
    project_dir = os.path.join(temp_dir, "long_test")
    os.makedirs(project_dir, exist_ok=True)
    
    for i in range(num_files):
        file_path = os.path.join(project_dir, f"file_{i}.py")
        with open(file_path, 'w') as f:
            num_classes = random.randint(1, 5)
            for c in range(num_classes):
                f.write(f"class File{i}Class{c}:\n")
                f.write(f"    def method{c}(self):\n")
                f.write(f"        return {i}\n\n")
    
    # 同步项目
    print("   🔄 开始同步...")
    proj_id = db.create_project(f"长时间同步测试_{int(time.time())}", project_dir)
    
    start_time = time.time()
    sync_result = engine.sync_project(proj_id)
    elapsed = time.time() - start_time
    
    if sync_result['success']:
        print(f"   ✅ 同步成功!")
        print(f"      - 处理文件: {sync_result['files_processed']}")
        print(f"      - 耗时: {elapsed:.2f}s")
        
        stats = db.get_stats(proj_id)
        if stats:
            print(f"      - 总文件数: {stats['file_count']}")
            print(f"      - 总类型数: {stats['type_count']}")
            print(f"      - 总函数数: {stats['function_count']}")
    else:
        print(f"   ❌ 同步失败: {sync_result['message']}")
    
    db.delete_project(proj_id)
    return sync_result['success']

def test_phase2_concurrent_and_stress():
    """第二阶段测试：压力与并发"""
    print_section("第二阶段：长时间压力与并发测试")
    
    overall_results = []
    
    temp_dir = tempfile.mkdtemp()
    try:
        # 创建一些基础文件用于测试
        base_dir = os.path.join(temp_dir, "base")
        os.makedirs(base_dir, exist_ok=True)
        create_test_project_files(base_dir, num_files=5)
        
        print_section("测试1：并发操作")
        try:
            success, errors = test_concurrent_operations(temp_dir, num_threads=10)
            overall_results.append(("并发操作(10线程)", success, len(errors)))
        except Exception as e:
            print(f"   ❌ 并发测试异常: {e}")
            import traceback
            traceback.print_exc()
            overall_results.append(("并发操作(10线程)", False, str(e)))
        
        print_section("测试2：快速连续操作")
        try:
            success = test_rapid_sequential_operations(base_dir, num_iterations=50)
            overall_results.append(("快速连续操作(50次)", success, 0))
        except Exception as e:
            print(f"   ❌ 快速操作异常: {e}")
            import traceback
            traceback.print_exc()
            overall_results.append(("快速连续操作(50次)", False, str(e)))
        
        print_section("测试3：长时间同步测试")
        try:
            success = test_long_running_project_sync(temp_dir, num_files=100)
            overall_results.append(("长时间同步(100文件)", success, 0))
        except Exception as e:
            print(f"   ❌ 长时间同步异常: {e}")
            import traceback
            traceback.print_exc()
            overall_results.append(("长时间同步(100文件)", False, str(e)))
        
        print_section("测试4：更多并发压力")
        try:
            success, errors = test_concurrent_operations(temp_dir, num_threads=20)
            overall_results.append(("高并发(20线程)", success, len(errors)))
        except Exception as e:
            print(f"   ❌ 高并发测试异常: {e}")
            import traceback
            traceback.print_exc()
            overall_results.append(("高并发(20线程)", False, str(e)))
        
    finally:
        # 清理
        print("\n🧹 清理...")
        try:
            for root, dirs, files in os.walk(temp_dir, topdown=False):
                for name in files:
                    try:
                        os.remove(os.path.join(root, name))
                    except:
                        pass
                for name in dirs:
                    try:
                        os.rmdir(os.path.join(root, name))
                    except:
                        pass
            try:
                os.rmdir(temp_dir)
            except:
                pass
    
    # 结果总结
    print_section("📊 第二阶段测试结果总结")
    passed = sum(1 for _, ok, _ in overall_results if ok)
    total = len(overall_results)
    
    for desc, ok, err_count in overall_results:
        status = "✅" if ok else "❌"
        print(f"   {status} {desc:30s} - 错误: {err_count}")
    
    print(f"\n总体: {passed}/{total} 通过")
    return passed == total

if __name__ == "__main__":
    print_section("代码知识图谱系统 - 第二阶段压力与并发测试")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        success = test_phase2_concurrent_and_stress()
        print_section("第二阶段测试完成")
        
        if success:
            print("✅ 第二阶段测试通过！")
        else:
            print("⚠️  第二阶段有测试失败")
        
    except Exception as e:
        print_section("严重错误")
        print(f"❌ {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
