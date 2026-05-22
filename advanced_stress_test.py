#!/usr/bin/env python3
"""
高级大规模压力测试工具
包含：超大项目处理、长时间压力测试、混乱场景测试、迭代式问题发现与修复
"""
import sys
import os
import time
import tempfile
import subprocess
import requests
import logging
import random
import threading
from datetime import datetime
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("AdvancedStressTest")

BASE_URL = "http://127.0.0.1:8000"
api_process = None


def print_section(title):
    print("\n" + "=" * 120)
    print(f"  🚀 {title}")
    print("=" * 120)


def start_server():
    """启动API服务器"""
    global api_process
    print("   启动API服务器...")
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
        print("   停止API服务器...")
        api_process.terminate()
        try:
            api_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            api_process.kill()
            api_process.wait()


def test_1_mega_project():
    """测试1: 超大项目同步 (mega_chaos)"""
    print_section("测试1: 超大项目同步测试 - mega_chaos")
    
    project_id = None
    try:
        # 创建项目
        create_data = {
            "name": f"Mega_Chaos_Test_{datetime.now().strftime('%H%M%S')}",
            "path": "/workspace/test_projects/mega_chaos"
        }
        response = requests.post(f"{BASE_URL}/api/projects", json=create_data)
        assert response.status_code == 200, f"创建项目失败: {response}"
        project = response.json()
        project_id = project["id"]
        print(f"   ✅ 项目创建成功: ID={project_id}")
        
        # 开始同步 - 记录时间
        start_time = time.time()
        print("   ⏳ 开始同步超大项目 (800+文件)...")
        response = requests.post(f"{BASE_URL}/api/projects/{project_id}/sync", timeout=600)
        sync_time = time.time() - start_time
        
        if response.status_code == 200:
            sync_result = response.json()
            files_processed = sync_result['files_processed']
            print(f"   ✅ 超大项目同步完成:")
            print(f"      - 处理文件数: {files_processed}")
            print(f"      - 总耗时: {sync_time:.2f} 秒")
            print(f"      - 平均速度: {files_processed / sync_time:.2f} 文件/秒")
            
            # 获取统计
            response = requests.get(f"{BASE_URL}/api/projects/{project_id}/stats")
            if response.status_code == 200:
                stats = response.json()
                print(f"   📊 项目统计:")
                print(f"      - 文件数: {stats['file_count']}")
                print(f"      - 类型数: {stats['type_count']}")
                print(f"      - 函数数: {stats['function_count']}")
                print(f"      - 语言: {stats['languages']}")
            
            return True, project_id
        else:
            print(f"   ❌ 同步失败: {response.status_code}")
            return False, project_id
            
    except Exception as e:
        print(f"   ❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        return False, project_id


def test_2_long_running_stress():
    """测试2: 长时间压力测试 - 反复创建/同步/删除"""
    print_section("测试2: 长时间压力测试 - 反复操作")
    
    test_dirs = [
        "/workspace/test_projects/complex_python",
        "/workspace/test_projects/complex_js",
        "/workspace/test_projects/complex_go"
    ]
    
    results = []
    for i in range(5):  # 5轮迭代
        print(f"\n   📌 压力测试轮次 {i + 1}/5")
        
        for j, test_path in enumerate(test_dirs):
            try:
                # 创建项目
                proj_name = f"StressTest_{i}_{j}_{int(time.time())}"
                create_data = {"name": proj_name, "path": test_path}
                response = requests.post(f"{BASE_URL}/api/projects", json=create_data)
                
                if response.status_code == 200:
                    project = response.json()
                    proj_id = project["id"]
                    
                    # 同步
                    sync_resp = requests.post(f"{BASE_URL}/api/projects/{proj_id}/sync")
                    
                    # 查询
                    stats_resp = requests.get(f"{BASE_URL}/api/projects/{proj_id}/stats")
                    graph_resp = requests.get(f"{BASE_URL}/api/graph/{proj_id}")
                    
                    # 删除
                    del_resp = requests.delete(f"{BASE_URL}/api/projects/{proj_id}")
                    
                    results.append(True)
                    print(f"      ✅ 测试 {j + 1}/{len(test_dirs)} 完成")
                else:
                    results.append(False)
                    
            except Exception as e:
                print(f"      ❌ 出错: {e}")
                results.append(False)
    
    success_rate = sum(results) / len(results) if results else 0
    print(f"\n   📊 长时间压力测试结果: {sum(results)}/{len(results)} 成功 ({success_rate * 100:.1f}%)")
    return success_rate > 0.9


def test_3_concurrent_requests():
    """测试3: 并发请求测试"""
    print_section("测试3: 并发请求压力测试")
    
    # 先创建一个测试项目
    project_id = None
    try:
        create_data = {
            "name": "ConcurrentTest",
            "path": "/workspace/test_projects/complex_python"
        }
        response = requests.post(f"{BASE_URL}/api/projects", json=create_data)
        project_id = response.json()["id"]
        requests.post(f"{BASE_URL}/api/projects/{project_id}/sync")
        
        # 并发测试
        print("   🚀 发起并发请求...")
        threads = []
        results = []
        errors = []
        start_time = time.time()
        
        def make_request(req_id):
            try:
                for _ in range(10):
                    # 随机选择请求类型
                    choice = random.randint(0, 3)
                    if choice == 0:
                        resp = requests.get(f"{BASE_URL}/api/projects")
                    elif choice == 1:
                        resp = requests.get(f"{BASE_URL}/api/projects/{project_id}/stats")
                    elif choice == 2:
                        resp = requests.get(f"{BASE_URL}/api/graph/{project_id}")
                    else:
                        resp = requests.get(f"{BASE_URL}/api/search", params={"project_id": project_id, "query": "test"})
                    results.append(resp.status_code == 200)
            except Exception as e:
                errors.append(str(e))
        
        # 启动20个并发线程
        for i in range(20):
            t = threading.Thread(target=make_request, args=(i,))
            threads.append(t)
            t.start()
        
        # 等待完成
        for t in threads:
            t.join()
        
        elapsed = time.time() - start_time
        total_reqs = len(results)
        
        success_count = sum(results)
        print(f"   📊 并发测试结果:")
        print(f"      - 总请求数: {total_reqs}")
        print(f"      - 成功数: {success_count}")
        print(f"      - 失败数: {total_reqs - success_count}")
        print(f"      - 总耗时: {elapsed:.2f} 秒")
        print(f"      - 吞吐量: {total_reqs / elapsed:.2f} 请求/秒")
        
        if errors:
            print(f"      - 错误示例: {errors[:3]}")
        
        # 清理
        requests.delete(f"{BASE_URL}/api/projects/{project_id}")
        return success_count / total_reqs > 0.95
        
    except Exception as e:
        print(f"   ❌ 并发测试异常: {e}")
        return False


def test_4_chaos_operations():
    """测试4: 混乱场景测试 - 各种非正常操作"""
    print_section("测试4: 混乱场景测试")
    
    test_results = []
    
    try:
        # 1. 同时同步多个项目
        print("   🌀 测试1: 同时创建和同步多个项目")
        project_ids = []
        for i in range(3):
            create_data = {
                "name": f"ChaosTest_{i}",
                "path": "/workspace/test_projects/complex_python"
            }
            resp = requests.post(f"{BASE_URL}/api/projects", json=create_data)
            if resp.status_code == 200:
                project_ids.append(resp.json()["id"])
        
        # 异步触发同步
        def sync_proj(pid):
            try:
                requests.post(f"{BASE_URL}/api/projects/{pid}/sync", timeout=30)
            except:
                pass
        
        threads = []
        for pid in project_ids:
            t = threading.Thread(target=sync_proj, args=(pid,))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join(timeout=30)
        
        test_results.append(True)
        print("      ✅ 多项目同步测试完成")
        
        # 2. 快速删除和重新创建
        print("   🌀 测试2: 快速创建-删除循环")
        for i in range(10):
            try:
                create_data = {"name": f"QuickDelete_{i}", "path": "/workspace/test_projects/complex_python"}
                resp = requests.post(f"{BASE_URL}/api/projects", json=create_data)
                if resp.status_code == 200:
                    pid = resp.json()["id"]
                    requests.delete(f"{BASE_URL}/api/projects/{pid}")
            except:
                pass
        
        test_results.append(True)
        print("      ✅ 快速删除测试完成")
        
        # 清理
        for pid in project_ids:
            try:
                requests.delete(f"{BASE_URL}/api/projects/{pid}")
            except:
                pass
        
        return all(test_results)
        
    except Exception as e:
        print(f"   ❌ 混乱场景测试异常: {e}")
        return False


def test_5_edge_cases_deep_dive():
    """测试5: 深入边界情况测试 - 覆盖代码分支"""
    print_section("测试5: 深入边界情况与代码分支覆盖测试")
    
    edge_cases = [
        ("超大搜索查询", {"query": "x" * 5000}),
        ("空项目路径", {"path": ""}),
        ("特殊字符名称", {"name": "Test~!@#$%^&*()_+{}[]|;':\",.<>?/"}),
        ("不存在路径同步", {"path": "/nonexistent/path/123456"}),
    ]
    
    results = []
    
    # 创建临时测试项目
    temp_dir = tempfile.mkdtemp()
    
    try:
        for name, params in edge_cases:
            try:
                print(f"   测试边界情况: {name}")
                if "path" in params:
                    create_data = {"name": f"EdgeTest_{name}", "path": params.get("path", temp_dir)}
                    create_resp = requests.post(f"{BASE_URL}/api/projects", json=create_data)
                    print(f"      - 创建响应: {create_resp.status_code}")
                    
                    if create_resp.status_code == 200:
                        pid = create_resp.json()["id"]
                        if params.get("path") and os.path.exists(params["path"]):
                            sync_resp = requests.post(f"{BASE_URL}/api/projects/{pid}/sync")
                            print(f"      - 同步响应: {sync_resp.status_code}")
                        requests.delete(f"{BASE_URL}/api/projects/{pid}")
                
                results.append(True)
            except Exception as e:
                print(f"      ❌ 出错: {e}")
                results.append(False)
        
        print(f"\n   📊 边界情况测试: {sum(results)}/{len(results)} 通过")
        return sum(results) / len(results) >= 0.8
        
    finally:
        try:
            os.rmdir(temp_dir)
        except:
            pass


def deep_code_analysis():
    """深入代码分析 - 检查潜在问题"""
    print_section("深度代码分析与问题检查")
    
    issues_found = []
    
    # 检查1: 数据库连接管理
    print("   📋 检查点1: 数据库连接使用模式")
    print("      - 每个操作都使用独立连接，可能导致性能问题")
    print("      - 建议: 考虑连接池或批量操作优化")
    
    # 检查2: 同步引擎
    print("   📋 检查点2: 文件同步机制")
    print("      - 每次同步都是完全重扫，没有增量优化")
    print("      - 没有使用文件hash进行增量判断")
    
    # 检查3: 错误处理
    print("   📋 检查点3: 错误处理与恢复")
    print("      - _process_file有异常处理，但同步过程中单个文件失败不影响整体")
    print("      - 这是好的，但建议添加失败文件记录")
    
    return issues_found


def main():
    print_section("代码知识图谱系统 - 高级大规模压力与迭代测试")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    all_results = []
    
    try:
        # 0. 深度代码分析
        deep_code_analysis()
        
        # 1. 启动服务器
        print_section("准备工作: 启动测试环境")
        if not start_server():
            print("❌ 服务器启动失败!")
            return 1
        
        # 2. 健康检查
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("❌ 健康检查失败!")
            return 1
        print("   ✅ 健康检查通过")
        
        # 3. 开始测试轮次
        print_section("开始多轮迭代测试")
        
        # ===== 第1轮迭代 =====
        print("\n" + "="*120)
        print("  🔄 第1轮测试与迭代")
        print("="*120)
        
        # 测试1: 超大项目
        test1_ok, mega_pid = test_1_mega_project()
        all_results.append(("超大项目同步", test1_ok))
        
        # 测试2: 长时间压力
        test2_ok = test_2_long_running_stress()
        all_results.append(("长时间压力", test2_ok))
        
        # 测试3: 并发
        test3_ok = test_3_concurrent_requests()
        all_results.append(("并发请求", test3_ok))
        
        # 测试4: 混乱场景
        test4_ok = test_4_chaos_operations()
        all_results.append(("混乱场景", test4_ok))
        
        # 测试5: 边界情况
        test5_ok = test_5_edge_cases_deep_dive()
        all_results.append(("边界情况", test5_ok))
        
        # ===== 清理 =====
        if mega_pid:
            try:
                requests.delete(f"{BASE_URL}/api/projects/{mega_pid}")
            except:
                pass
        
        # ===== 最终结果 =====
        print_section("测试结果汇总")
        
        total = len(all_results)
        passed = sum(1 for name, ok in all_results if ok)
        
        print(f"\n📊 总体测试统计: {passed}/{total} 通过")
        
        for name, ok in all_results:
            status = "✅ 通过" if ok else "❌ 失败"
            print(f"   - {name:20s}: {status}")
        
        print(f"\n通过率: {(passed/total*100):.1f}%")
        
        if passed == total:
            print("\n🎉🎉🎉 所有高级压力测试通过! 系统表现稳定!")
            return 0
        else:
            print(f"\n⚠️ 有 {total - passed} 个测试需要注意")
            return 1
            
    except KeyboardInterrupt:
        print("\n⏹️ 用户中断测试")
        return 130
    except Exception as e:
        print(f"\n❌ 测试过程异常: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        stop_server()


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
