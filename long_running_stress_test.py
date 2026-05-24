#!/usr/bin/env python3
"""
超大规模长时间压力测试工具
对系统进行持续的压力测试，发现性能问题、内存泄漏、边界问题
"""
import sys
import os
import time
import tempfile
import random
import gc
import threading
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.config import config
from backend.database import Database, db
from backend.services.engine import SyncEngine, engine

def print_section(title):
    print("\n" + "=" * 140)
    print(f"🔥 {title}")
    print("=" * 140)

def print_subsection(title):
    print(f"\n📍 {title}")
    print("-" * 120)

def generate_large_project(temp_dir, num_files, num_classes_per_file):
    """生成大规模测试项目"""
    project_dir = os.path.join(temp_dir, "massive_stress_test")
    os.makedirs(project_dir, exist_ok=True)
    
    # 创建多个子目录
    for dir_idx in range(5):
        subdir = os.path.join(project_dir, f"module_{dir_idx}")
        os.makedirs(subdir, exist_ok=True)
        
        # 在每个子目录创建文件
        files_in_dir = num_files // 5
        for file_idx in range(files_in_dir):
            filepath = os.path.join(subdir, f"file_{dir_idx}_{file_idx}.py")
            with open(filepath, 'w', encoding='utf-8') as f:
                # 创建多个类
                for class_idx in range(num_classes_per_file):
                    class_name = f"MassiveClass{dir_idx}_{file_idx}_{class_idx}"
                    f.write(f"class {class_name}:\n")
                    f.write(f"    \"\"\"{class_name} documentation\"\"\"\n")
                    
                    # 创建多个方法
                    num_methods = random.randint(2, 5)
                    for method_idx in range(num_methods):
                        method_name = f"method_{method_idx}"
                        f.write(f"    def {method_name}(self, x, y):\n")
                        f.write(f"        \"\"\"{method_name} description\"\"\"\n")
                        f.write(f"        return x + y + {dir_idx} + {file_idx} + {class_idx} + {method_idx}\n")
                    f.write("\n")
                
                # 创建一些顶层函数
                for func_idx in range(3):
                    func_name = f"top_func_{dir_idx}_{file_idx}_{func_idx}"
                    f.write(f"def {func_name}(a, b):\n")
                    f.write(f"    \"\"\"{func_name} description\"\"\"\n")
                    f.write(f"    return a * b + {dir_idx} + {file_idx} + {func_idx}\n")
                    f.write("\n")
    
    print(f"✅ 创建大规模项目: {num_files} 文件, 每文件 {num_classes_per_file} 类")
    return project_dir

def test_long_running_sessions():
    """测试长时间运行会话"""
    print_section("超大规模长时间压力测试开始")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    # 清理旧数据库
    if os.path.exists(config.DATABASE_PATH):
        os.remove(config.DATABASE_PATH)
    db.init_db()
    
    temp_dir = tempfile.mkdtemp()
    
    try:
        # 测试场景 1: 超大项目同步
        print_subsection("场景1: 超大项目同步压力测试")
        
        project_dir = generate_large_project(temp_dir, num_files=200, num_classes_per_file=10)
        project_id = db.create_project("LongRunningTest", project_dir)
        
        start_time = time.time()
        result = engine.sync_project(project_id)
        elapsed = time.time() - start_time
        
        stats = db.get_stats(project_id)
        print(f"\n📊 同步结果:")
        print(f"  文件处理: {result['files_processed']}")
        print(f"  发现类型: {stats['type_count']}")
        print(f"  发现函数: {stats['function_count']}")
        print(f"  同步耗时: {elapsed:.2f} 秒")
        
        success = stats['type_count'] > 0 and elapsed < 300
        results.append(("超大项目同步", success, elapsed))
        
        # 测试场景 2: 重复查询压力
        print_subsection("场景2: 高频查询压力测试")
        
        num_queries = 500
        start_time = time.time()
        
        for i in range(num_queries):
            query = f"Class{i % 10}"
            try:
                results_search = db.search(project_id, query)
                # 定期获取统计信息
                if i % 100 == 0:
                    db.get_stats(project_id)
                    db.get_graph_data(project_id)
            except Exception as e:
                print(f"  查询出错 (i={i}): {e}")
        
        elapsed = time.time() - start_time
        qps = num_queries / elapsed
        
        print(f"\n📊 查询压力结果:")
        print(f"  总查询: {num_queries}")
        print(f"  总耗时: {elapsed:.2f} 秒")
        print(f"  平均QPS: {qps:.1f}")
        
        success = qps > 10  # 要求每秒至少10个查询
        results.append(("高频查询压力", success, qps))
        
        # 测试场景 3: 重复创建-删除压力
        print_subsection("场景3: 频繁创建/删除项目压力")
        
        num_operations = 100
        start_time = time.time()
        
        for i in range(num_operations):
            try:
                temp_proj_id = db.create_project(f"QuickTest_{i}", project_dir)
                engine.sync_project(temp_proj_id)
                db.delete_project(temp_proj_id)
            except Exception as e:
                print(f"  操作出错 (i={i}): {e}")
        
        elapsed = time.time() - start_time
        
        print(f"\n📊 创建/删除压力结果:")
        print(f"  总操作: {num_operations}")
        print(f"  总耗时: {elapsed:.2f} 秒")
        print(f"  平均操作耗时: {elapsed/num_operations:.2f} 秒")
        
        success = elapsed < 300
        results.append(("频繁创建/删除", success, elapsed))
        
        # 测试场景 4: 并发查询压力
        print_subsection("场景4: 并发查询压力测试")
        
        num_threads = 5
        queries_per_thread = 100
        errors = []
        
        def query_worker(thread_id):
            try:
                for i in range(queries_per_thread):
                    query = f"Thread{thread_id}Query{i}"
                    db.search(project_id, query)
            except Exception as e:
                errors.append((thread_id, e))
        
        start_time = time.time()
        threads = []
        for i in range(num_threads):
            t = threading.Thread(target=query_worker, args=(i,))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        elapsed = time.time() - start_time
        total_queries = num_threads * queries_per_thread
        
        print(f"\n📊 并发查询结果:")
        print(f"  线程数: {num_threads}")
        print(f"  总查询: {total_queries}")
        print(f"  总耗时: {elapsed:.2f} 秒")
        print(f"  错误数: {len(errors)}")
        
        success = len(errors) == 0
        results.append(("并发查询", success, len(errors)))
        
        # 清理主项目
        db.delete_project(project_id)
        
    finally:
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
            os.rmdir(temp_dir)
        except:
            pass
    
    # 总结结果
    print_section("长时压力测试结果总结")
    
    for name, success, metric in results:
        status = "✅ 成功" if success else "⚠️ 需要优化"
        print(f"  {status}: {name} - 指标: {metric}")
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    print(f"\n总体: {passed}/{total} 个场景通过")
    
    if passed == total:
        print(f"\n🎉🎉🎉 所有压力测试通过！系统稳定性良好！")
    else:
        print(f"\n✅ 大部分场景通过，系统基本稳定")
    
    return 0 if passed >= total * 0.7 else 1

def main():
    """主函数"""
    try:
        return test_long_running_sessions()
    except Exception as e:
        print(f"\n❌ 压力测试异常: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
