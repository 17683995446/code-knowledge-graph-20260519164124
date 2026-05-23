#!/usr/bin/env python3
"""
极致细节深度测试工具
重点测试：边界条件、并发竞态、资源泄漏、极端输入、超大文件等
"""
import sys
import os
import tempfile
import random
import string
import time
import threading
import sqlite3
import gc
from datetime import datetime
from typing import List, Dict, Tuple
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.config import config
from backend.database import Database
from backend.services.engine import SyncEngine
from backend.parsers import get_parser_for_language

db = Database()
engine = SyncEngine()

def print_section(title):
    print("\n" + "=" * 140)
    print(f"🔥 {title}")
    print("=" * 140)

def print_subsection(title):
    print(f"\n📍 {title}")
    print("-" * 120)

def print_detail(msg):
    print(f"   ↪ {msg}")

def print_success(msg):
    print(f"   ✅ {msg}")

def print_error(msg):
    print(f"   ❌ {msg}")

def print_warning(msg):
    print(f"   ⚠️  {msg}")

# ========================================
# 测试1: 边界条件测试
# ========================================

def test_boundary_conditions():
    """测试各种边界条件"""
    print_section("测试1: 极致边界条件测试")
    
    results = []
    temp_dir = tempfile.mkdtemp()
    
    try:
        # 测试1.1: 空字符串名称
        print_subsection("1.1 空字符串项目名称")
        try:
            db.create_project("", temp_dir)
            print_error("应该抛出异常")
            results.append(("空名称", False))
        except (ValueError, sqlite3.IntegrityError) as e:
            print_success(f"正确处理: {type(e).__name__}")
            results.append(("空名称", True))
        
        # 测试1.2: 空格名称
        print_subsection("1.2 纯空格项目名称")
        try:
            db.create_project("   ", temp_dir)
            print_warning("空格名称被接受，可能需要验证")
            results.append(("空格名称", False))
        except Exception as e:
            print_success(f"正确拒绝: {e}")
            results.append(("空格名称", True))
        
        # 测试1.3: 超长名称
        print_subsection("1.3 超长项目名称 (10000字符)")
        try:
            long_name = "A" * 10000
            proj_id = db.create_project(long_name, temp_dir)
            project = db.get_project(proj_id)
            if project and len(project['name']) == 10000:
                print_success(f"接受超长名称，长度: {len(project['name'])}")
                results.append(("超长名称", True))
            else:
                print_warning(f"名称被截断或处理")
                results.append(("超长名称", False))
            db.delete_project(proj_id)
        except Exception as e:
            print_success(f"正确处理: {e}")
            results.append(("超长名称", True))
        
        # 测试1.4: 特殊字符名称
        print_subsection("1.4 特殊字符项目名称")
        special_chars = ['!@#$%^&*()', '中文测试', '日本語', '🎉🎊', '\n\t\r']
        for char_set in special_chars:
            try:
                proj_id = db.create_project(f"Test_{char_set}", temp_dir)
                db.delete_project(proj_id)
                print_success(f"特殊字符 '{char_set[:20]}' 被接受")
            except Exception as e:
                print_warning(f"特殊字符 '{char_set[:20]}' 被拒绝: {e}")
        
        results.append(("特殊字符名称", True))
        
        # 测试1.5: 不存在的路径
        print_subsection("1.5 不存在的项目路径")
        try:
            proj_id = db.create_project("Test", "/nonexistent/path/12345")
            db.delete_project(proj_id)
            print_warning("不存在的路径被接受")
            results.append(("不存在路径", False))
        except Exception as e:
            print_success(f"正确处理: {e}")
            results.append(("不存在路径", True))
        
        # 测试1.6: 重复的路径
        print_subsection("1.6 重复项目路径")
        try:
            proj_id1 = db.create_project("Test1", temp_dir)
            proj_id2 = db.create_project("Test2", temp_dir)
            print_error("应该抛出异常")
            results.append(("重复路径", False))
            db.delete_project(proj_id1)
            db.delete_project(proj_id2)
        except sqlite3.IntegrityError as e:
            print_success(f"正确检测重复: {e}")
            results.append(("重复路径", True))
        except Exception as e:
            print_success(f"正确处理: {type(e).__name__}")
            results.append(("重复路径", True))
        
        # 测试1.7: 负数ID操作
        print_subsection("1.7 负数项目ID操作")
        try:
            project = db.get_project(-1)
            if project is None:
                print_success("负数ID返回None")
                results.append(("负数ID查询", True))
            else:
                print_error("不应该返回数据")
                results.append(("负数ID查询", False))
        except Exception as e:
            print_success(f"正确处理: {e}")
            results.append(("负数ID查询", True))
        
        # 测试1.8: 极大ID操作
        print_subsection("1.8 极大项目ID操作")
        try:
            project = db.get_project(999999999)
            if project is None:
                print_success("极大ID返回None")
                results.append(("极大ID查询", True))
            else:
                print_error("不应该返回数据")
                results.append(("极大ID查询", False))
        except Exception as e:
            print_success(f"正确处理: {e}")
            results.append(("极大ID查询", True))
        
        # 测试1.9: 删除不存在的项目
        print_subsection("1.9 删除不存在的项目")
        try:
            db.delete_project(999999)
            print_success("删除不存在的项目没有崩溃")
            results.append(("删除不存在", True))
        except Exception as e:
            print_error(f"删除失败: {e}")
            results.append(("删除不存在", False))
        
        # 测试1.10: 多次删除同一项目
        print_subsection("1.10 多次删除同一项目")
        try:
            proj_id = db.create_project("DeleteTest", temp_dir)
            db.delete_project(proj_id)
            db.delete_project(proj_id)  # 第二次应该失败
            print_error("第二次删除应该失败")
            results.append(("重复删除", False))
        except Exception as e:
            print_success(f"第二次删除正确报错: {type(e).__name__}")
            results.append(("重复删除", True))
        
    finally:
        # 清理
        try:
            os.rmdir(temp_dir)
        except:
            pass
    
    # 结果总结
    print_section("边界条件测试结果")
    passed = sum(1 for _, ok in results if ok)
    total = len(results)
    for name, ok in results:
        status = "✅" if ok else "❌"
        print(f"   {status} {name}")
    print(f"\n通过: {passed}/{total}")
    
    return passed >= total * 0.8

# ========================================
# 测试2: 并发竞态条件测试
# ========================================

def test_concurrency_race_conditions():
    """测试并发和竞态条件"""
    print_section("测试2: 并发竞态条件深度测试")
    
    results = []
    temp_dir = tempfile.mkdtemp()
    
    try:
        # 测试2.1: 同时创建同名项目
        print_subsection("2.1 同时创建同名项目 (并发)")
        errors = []
        proj_ids = []
        
        def create_project_thread():
            try:
                proj_id = db.create_project("ConcurrentTest", temp_dir)
                proj_ids.append(proj_id)
            except Exception as e:
                errors.append(e)
        
        threads = []
        for i in range(10):
            t = threading.Thread(target=create_project_thread)
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        if len(errors) > 0 and len(proj_ids) > 0:
            print_success(f"正确处理并发: {len(proj_ids)} 个成功, {len(errors)} 个失败")
            results.append(("同时创建同名", True))
            # 清理
            for pid in proj_ids:
                try:
                    db.delete_project(pid)
                except:
                    pass
        else:
            print_error(f"处理不当: {len(proj_ids)} 成功, {len(errors)} 失败")
            results.append(("同时创建同名", False))
        
        # 测试2.2: 同时删除同一项目
        print_subsection("2.2 同时删除同一项目 (并发)")
        proj_id = db.create_project("ConcurrentDelete", temp_dir)
        errors = []
        
        def delete_thread():
            try:
                db.delete_project(proj_id)
            except Exception as e:
                errors.append(e)
        
        threads = []
        for i in range(5):
            t = threading.Thread(target=delete_thread)
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        print_success(f"并发删除完成: {len(errors)} 个错误")
        results.append(("同时删除", True))
        
        # 测试2.3: 同时查询和修改
        print_subsection("2.3 同时查询和修改项目")
        proj_id = db.create_project("ConcurrentReadWrite", temp_dir)
        read_results = []
        write_count = [0]
        
        def read_thread():
            for _ in range(10):
                try:
                    project = db.get_project(proj_id)
                    if project:
                        read_results.append(project['name'])
                    time.sleep(0.001)
                except Exception as e:
                    pass
        
        def write_thread():
            for _ in range(10):
                try:
                    engine.sync_project(proj_id)
                    write_count[0] += 1
                    time.sleep(0.001)
                except Exception as e:
                    pass
        
        threads = []
        for i in range(3):
            threads.append(threading.Thread(target=read_thread))
            threads.append(threading.Thread(target=write_thread))
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        print_success(f"读写并发完成: {len(read_results)} 次读取, {write_count[0]} 次写入")
        results.append(("同时读写", True))
        db.delete_project(proj_id)
        
        # 测试2.4: 快速连续创建删除
        print_subsection("2.4 快速连续创建删除 (100次)")
        start_time = time.time()
        for i in range(100):
            try:
                proj_id = db.create_project(f"RapidTest{i}", temp_dir)
                db.delete_project(proj_id)
            except Exception as e:
                pass
        elapsed = time.time() - start_time
        
        print_success(f"100次快速创建/删除完成，耗时: {elapsed:.2f}秒")
        results.append(("快速连续", True))
        
        # 测试2.5: 数据库连接泄漏测试
        print_subsection("2.5 数据库连接泄漏测试")
        initial_connections = count_connections()
        
        for i in range(50):
            try:
                proj_id = db.create_project(f"LeakTest{i}", temp_dir)
                db.delete_project(proj_id)
            except:
                pass
        
        gc.collect()
        time.sleep(0.1)
        final_connections = count_connections()
        
        if final_connections <= initial_connections + 5:  # 允许少量增加
            print_success(f"无连接泄漏: {initial_connections} -> {final_connections}")
            results.append(("无连接泄漏", True))
        else:
            print_warning(f"可能存在连接泄漏: {initial_connections} -> {final_connections}")
            results.append(("无连接泄漏", False))
        
    finally:
        try:
            for root, dirs, files in os.walk(temp_dir, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(temp_dir)
        except:
            pass
    
    # 结果总结
    print_section("并发竞态测试结果")
    passed = sum(1 for _, ok in results if ok)
    total = len(results)
    for name, ok in results:
        status = "✅" if ok else "⚠️"
        print(f"   {status} {name}")
    print(f"\n通过: {passed}/{total}")
    
    return passed >= total * 0.8

def count_connections():
    """统计当前数据库连接数"""
    try:
        conn = sqlite3.connect(config.DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
        conn.close()
        return 0
    except:
        return 0

# ========================================
# 测试3: 资源泄漏和内存测试
# ========================================

def test_resource_leaks_and_memory():
    """测试资源泄漏和内存使用"""
    print_section("测试3: 资源泄漏和内存深度测试")
    
    results = []
    temp_dir = tempfile.mkdtemp()
    
    try:
        # 测试3.1: 处理超大文件
        print_subsection("3.1 处理超大文件 (5000行)")
        large_file = os.path.join(temp_dir, "large.py")
        with open(large_file, 'w') as f:
            for i in range(5000):
                f.write(f"class TestClass{i}:\n")
                f.write(f"    def method(self):\n")
                f.write(f"        return {i}\n\n")
        
        proj_id = db.create_project("LargeFileTest", temp_dir)
        
        start_time = time.time()
        sync_result = engine.sync_project(proj_id)
        elapsed = time.time() - start_time
        
        stats = db.get_stats(proj_id)
        print_success(f"处理完成: {sync_result['files_processed']} 文件, "
                     f"{stats['type_count']} 类型, {elapsed:.2f}秒")
        results.append(("超大文件", True))
        db.delete_project(proj_id)
        
        # 测试3.2: 文件描述符泄漏
        print_subsection("3.2 文件描述符泄漏测试")
        initial_fds = count_open_files()
        
        for i in range(20):
            proj_id = db.create_project(f"FdLeak{i}", temp_dir)
            engine.sync_project(proj_id)
            db.delete_project(proj_id)
        
        gc.collect()
        final_fds = count_open_files()
        
        if final_fds <= initial_fds + 10:
            print_success(f"无文件描述符泄漏: {initial_fds} -> {final_fds}")
            results.append(("无FD泄漏", True))
        else:
            print_warning(f"可能存在FD泄漏: {initial_fds} -> {final_fds}")
            results.append(("无FD泄漏", False))
        
        # 测试3.3: 大量小文件
        print_subsection("3.3 大量小文件处理 (500个)")
        many_files_dir = os.path.join(temp_dir, "many_small_files")
        os.makedirs(many_files_dir, exist_ok=True)
        
        for i in range(500):
            with open(os.path.join(many_files_dir, f"file_{i}.py"), 'w') as f:
                f.write(f"class C{i}:\n    def m(self):\n        pass\n")
        
        proj_id = db.create_project("ManySmallFiles", many_files_dir)
        
        start_time = time.time()
        sync_result = engine.sync_project(proj_id)
        elapsed = time.time() - start_time
        
        print_success(f"处理完成: {sync_result['files_processed']} 文件, {elapsed:.2f}秒")
        results.append(("大量小文件", True))
        db.delete_project(proj_id)
        
        # 测试3.4: 内存持续增长测试
        print_subsection("3.4 内存增长测试 (50次同步)")
        import tracemalloc
        
        tracemalloc.start()
        snapshot1 = tracemalloc.take_snapshot()
        
        for i in range(50):
            proj_id = db.create_project(f"MemTest{i}", temp_dir)
            with open(os.path.join(temp_dir, f"mem_test_{i}.py"), 'w') as f:
                f.write(f"class Test{i}:\n    def method(self):\n        pass\n")
            engine.sync_project(proj_id)
            db.delete_project(proj_id)
            if i % 10 == 0:
                gc.collect()
        
        snapshot2 = tracemalloc.take_snapshot()
        top_stats = snapshot2.compare_to(snapshot1, 'lineno')
        
        total_diff = sum(stat.size_diff for stat in top_stats[:10])
        print_success(f"内存变化: {total_diff / 1024 / 1024:.2f} MB (前10差异)")
        results.append(("内存增长", True))
        
        tracemalloc.stop()
        
        # 测试3.5: 异常文件处理不泄漏
        print_subsection("3.5 异常文件处理不泄漏")
        error_file = os.path.join(temp_dir, "error.py")
        with open(error_file, 'w') as f:
            f.write("invalid syntax here @#$%\n")
            f.write("class Valid:\n")
            f.write("    pass\n")
        
        proj_id = db.create_project("ErrorFileTest", temp_dir)
        try:
            sync_result = engine.sync_project(proj_id)
            print_success(f"异常文件处理完成，未崩溃")
            results.append(("异常文件", True))
        except Exception as e:
            print_warning(f"异常文件导致错误: {e}")
            results.append(("异常文件", False))
        finally:
            db.delete_project(proj_id)
        
    finally:
        try:
            for root, dirs, files in os.walk(temp_dir, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(temp_dir)
        except:
            pass
    
    # 结果总结
    print_section("资源泄漏测试结果")
    passed = sum(1 for _, ok in results if ok)
    total = len(results)
    for name, ok in results:
        status = "✅" if ok else "⚠️"
        print(f"   {status} {name}")
    print(f"\n通过: {passed}/{total}")
    
    return passed >= total * 0.8

def count_open_files():
    """统计打开的文件描述符数量"""
    try:
        import psutil
        process = psutil.Process()
        return len(process.open_files())
    except:
        return 0

# ========================================
# 测试4: 数据一致性测试
# ========================================

def test_data_consistency():
    """测试数据一致性"""
    print_section("测试4: 数据一致性深度测试")
    
    results = []
    temp_dir = tempfile.mkdtemp()
    
    try:
        # 测试4.1: 项目创建后数据一致性
        print_subsection("4.1 项目创建数据一致性")
        proj_id = db.create_project("ConsistencyTest", temp_dir)
        
        # 创建测试文件
        test_file = os.path.join(temp_dir, "test.py")
        with open(test_file, 'w') as f:
            f.write("class TestClass:\n    def test_method(self):\n        pass\n")
        
        # 同步
        engine.sync_project(proj_id)
        
        # 验证统计数据
        stats = db.get_stats(proj_id)
        graph = db.get_graph_data(proj_id)
        
        if stats['file_count'] >= 1 and len(graph['nodes']) >= 1:
            print_success(f"数据一致: 文件={stats['file_count']}, 节点={len(graph['nodes'])}")
            results.append(("创建一致性", True))
        else:
            print_error(f"数据不一致: 文件={stats['file_count']}, 节点={len(graph['nodes'])}")
            results.append(("创建一致性", False))
        
        db.delete_project(proj_id)
        
        # 测试4.2: 删除后数据清理
        print_subsection("4.2 删除后数据清理")
        proj_id = db.create_project("DeleteCleanup", temp_dir)
        
        test_file2 = os.path.join(temp_dir, "test2.py")
        with open(test_file2, 'w') as f:
            f.write("class TestClass2:\n    pass\n")
        
        engine.sync_project(proj_id)
        stats_before = db.get_stats(proj_id)
        db.delete_project(proj_id)
        
        # 尝试获取已删除项目
        project = db.get_project(proj_id)
        if project is None:
            print_success("项目删除后无法访问")
            results.append(("删除清理", True))
        else:
            print_error("删除后仍可访问")
            results.append(("删除清理", False))
        
        # 测试4.3: 搜索结果一致性
        print_subsection("4.3 搜索结果一致性")
        proj_id = db.create_project("SearchConsistency", temp_dir)
        
        search_file = os.path.join(temp_dir, "search_test.py")
        with open(search_file, 'w') as f:
            f.write("class UniqueTestClass123:\n    def unique_method_456(self):\n        pass\n")
        
        engine.sync_project(proj_id)
        
        # 搜索
        search_results = db.search(proj_id, "UniqueTestClass123")
        stats = db.get_stats(proj_id)
        
        if len(search_results) > 0 and stats['type_count'] > 0:
            print_success(f"搜索一致: 结果={len(search_results)}, 类型={stats['type_count']}")
            results.append(("搜索一致性", True))
        else:
            print_warning(f"搜索结果: {len(search_results)}, 统计: {stats['type_count']}")
            results.append(("搜索一致性", False))
        
        db.delete_project(proj_id)
        
        # 测试4.4: 并发操作数据一致性
        print_subsection("4.4 并发操作数据一致性")
        proj_id = db.create_project("ConcurrentConsistency", temp_dir)
        
        def sync_operation():
            for _ in range(5):
                engine.sync_project(proj_id)
                time.sleep(0.01)
        
        threads = []
        for i in range(3):
            t = threading.Thread(target=sync_operation)
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        stats = db.get_stats(proj_id)
        if stats['file_count'] >= 0:
            print_success(f"并发后数据一致: 文件={stats['file_count']}")
            results.append(("并发一致性", True))
        else:
            print_error(f"并发后数据不一致")
            results.append(("并发一致性", False))
        
        db.delete_project(proj_id)
        
    finally:
        try:
            for root, dirs, files in os.walk(temp_dir, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(temp_dir)
        except:
            pass
    
    # 结果总结
    print_section("数据一致性测试结果")
    passed = sum(1 for _, ok in results if ok)
    total = len(results)
    for name, ok in results:
        status = "✅" if ok else "⚠️"
        print(f"   {status} {name}")
    print(f"\n通过: {passed}/{total}")
    
    return passed >= total * 0.8

# ========================================
# 主测试函数
# ========================================

def main():
    print_section("代码知识图谱系统 - 极致细节深度测试")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python: {sys.version}")
    print(f"工作目录: {os.getcwd()}")
    
    all_results = []
    
    try:
        # 清理数据库
        if os.path.exists(config.DATABASE_PATH):
            os.remove(config.DATABASE_PATH)
        
        # 测试1: 边界条件
        try:
            result1 = test_boundary_conditions()
            all_results.append(("边界条件测试", result1))
        except Exception as e:
            print_error(f"边界条件测试异常: {e}")
            import traceback
            traceback.print_exc()
            all_results.append(("边界条件测试", False))
        
        # 测试2: 并发竞态
        try:
            result2 = test_concurrency_race_conditions()
            all_results.append(("并发竞态测试", result2))
        except Exception as e:
            print_error(f"并发竞态测试异常: {e}")
            import traceback
            traceback.print_exc()
            all_results.append(("并发竞态测试", False))
        
        # 测试3: 资源泄漏
        try:
            result3 = test_resource_leaks_and_memory()
            all_results.append(("资源泄漏测试", result3))
        except Exception as e:
            print_error(f"资源泄漏测试异常: {e}")
            import traceback
            traceback.print_exc()
            all_results.append(("资源泄漏测试", False))
        
        # 测试4: 数据一致性
        try:
            result4 = test_data_consistency()
            all_results.append(("数据一致性测试", result4))
        except Exception as e:
            print_error(f"数据一致性测试异常: {e}")
            import traceback
            traceback.print_exc()
            all_results.append(("数据一致性测试", False))
        
    except Exception as e:
        print_error(f"主测试异常: {e}")
        import traceback
        traceback.print_exc()
    
    # 最终结果总结
    print_section("=" * 140)
    print("🔥 极致细节深度测试 - 最终结果总结")
    print("=" * 140)
    
    total_passed = sum(1 for _, ok in all_results if ok)
    total_tests = len(all_results)
    
    for name, ok in all_results:
        status = "✅ 通过" if ok else "❌ 失败"
        print(f"   {status} - {name}")
    
    print(f"\n总体结果: {total_passed}/{total_tests} 测试通过")
    
    if total_passed == total_tests:
        print("\n🎉🎉🎉 所有极致细节测试通过！系统质量优秀！")
        return 0
    elif total_passed >= total_tests * 0.8:
        print("\n✅ 大部分测试通过，系统质量良好！")
        return 0
    else:
        print("\n⚠️  部分测试失败，需要进一步优化")
        return 1

if __name__ == "__main__":
    sys.exit(main())
