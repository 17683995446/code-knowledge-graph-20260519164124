#!/usr/bin/env python3
"""
业务场景闭环测试工具
包含：完整业务流程测试、数据一致性校验、性能验证等
"""
import sys
import os
import time
import requests
import subprocess
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("BusinessScenarioTest")

BASE_URL = "http://127.0.0.1:8000"

def print_section(title):
    """打印分段标题"""
    print("\n" + "=" * 100)
    print(f"📋 {title}")
    print("=" * 100)

def print_test_result(test_name, success):
    """打印测试结果"""
    status = "✅ 通过" if success else "❌ 失败"
    print(f"   {test_name:50s} - {status}")
    return success

def main():
    print_section("代码知识图谱系统 - 业务场景闭环测试")
    
    test_results = []
    
    # 步骤1：启动API服务
    print_section("步骤1：启动API服务")
    api_process = None
    try:
        api_process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print("   ⏳ 等待服务启动...")
        time.sleep(3)
        test_results.append(print_test_result("启动API服务", True))
    except Exception as e:
        print(f"   ❌ 启动失败: {e}")
        test_results.append(print_test_result("启动API服务", False))
        return 1
    
    # 步骤2：健康检查
    print_section("步骤2：健康检查")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print(f"   ✅ 健康检查通过: {response.json()}")
            test_results.append(print_test_result("健康检查", True))
        else:
            test_results.append(print_test_result("健康检查", False))
    except Exception as e:
        print(f"   ❌ 健康检查异常: {e}")
        test_results.append(print_test_result("健康检查", False))
    
    # 步骤3：创建测试项目
    print_section("步骤3：创建测试项目")
    project_id = None
    project_path = "/workspace/test_projects/complex_python"
    try:
        create_data = {
            "name": f"业务测试项目_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "path": project_path
        }
        response = requests.post(f"{BASE_URL}/api/projects", json=create_data)
        if response.status_code == 200:
            project = response.json()
            project_id = project["id"]
            print(f"   ✅ 项目创建成功: ID={project_id}, 名称={project['name']}")
            test_results.append(print_test_result("创建巨型项目", True))
        else:
            test_results.append(print_test_result("创建巨型项目", False))
    except Exception as e:
        print(f"   ❌ 创建失败: {e}")
        test_results.append(print_test_result("创建巨型项目", False))
    
    if not project_id:
        if api_process:
            api_process.terminate()
        return 1
    
    # 步骤4：同步巨型项目（这是核心测试）
    print_section("步骤4：同步巨型项目")
    sync_start_time = time.time()
    try:
        print("   ⏳ 正在同步大规模代码库，这可能需要一些时间...")
        response = requests.post(f"{BASE_URL}/api/projects/{project_id}/sync", timeout=300)
        sync_duration = time.time() - sync_start_time
        
        if response.status_code == 200:
            sync_result = response.json()
            print(f"   ✅ 同步完成:")
            print(f"      - 处理文件数: {sync_result['files_processed']}")
            print(f"      - 耗时: {sync_duration:.2f} 秒")
            if sync_duration > 0:
                print(f"      - 平均处理速度: {sync_result['files_processed'] / sync_duration:.2f} 文件/秒")
            test_results.append(print_test_result("同步巨型项目", True))
        else:
            test_results.append(print_test_result("同步巨型项目", False))
    except Exception as e:
        sync_duration = time.time() - sync_start_time
        print(f"   ❌ 同步异常: {e}")
        test_results.append(print_test_result("同步巨型项目", False))
    
    # 步骤5：获取项目统计
    print_section("步骤5：获取项目统计")
    stats = None
    try:
        response = requests.get(f"{BASE_URL}/api/projects/{project_id}/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"   ✅ 项目统计:")
            print(f"      - 文件数: {stats['file_count']}")
            print(f"      - 类型数: {stats['type_count']}")
            print(f"      - 函数数: {stats['function_count']}")
            print(f"      - 语言分布: {stats['languages']}")
            test_results.append(print_test_result("获取项目统计", True))
        else:
            test_results.append(print_test_result("获取项目统计", False))
    except Exception as e:
        print(f"   ❌ 获取统计异常: {e}")
        test_results.append(print_test_result("获取项目统计", False))
    
    # 步骤6：获取知识图谱数据
    print_section("步骤6：获取知识图谱数据")
    graph_data = None
    try:
        response = requests.get(f"{BASE_URL}/api/graph/{project_id}")
        if response.status_code == 200:
            graph_data = response.json()
            print(f"   ✅ 图谱数据:")
            print(f"      - 节点数: {len(graph_data['nodes'])}")
            print(f"      - 边数: {len(graph_data['links'])}")
            test_results.append(print_test_result("获取知识图谱", True))
        else:
            test_results.append(print_test_result("获取知识图谱", False))
    except Exception as e:
        print(f"   ❌ 获取图谱异常: {e}")
        test_results.append(print_test_result("获取知识图谱", False))
    
    # 步骤7：搜索功能测试
    print_section("步骤7：搜索功能测试")
    search_queries = [
        ("user", None, "用户相关"),
        ("product", None, "产品相关"),
        ("auth", "type", "认证类型"),
        ("process", "function", "处理函数"),
    ]
    all_search_ok = True
    for query, type_filter, desc in search_queries:
        try:
            params = {"project_id": project_id, "query": query}
            if type_filter:
                params["type_filter"] = type_filter
            
            response = requests.get(f"{BASE_URL}/api/search", params=params)
            if response.status_code == 200:
                results = response.json()
                print(f"   ✅ 搜索 '{query}' ({desc}): 找到 {len(results)} 个结果")
            else:
                print(f"   ❌ 搜索 '{query}' 失败")
                all_search_ok = False
        except Exception as e:
            print(f"   ❌ 搜索 '{query}' 异常: {e}")
            all_search_ok = False
    test_results.append(print_test_result("搜索功能测试", all_search_ok))
    
    # 步骤8：数据一致性校验
    print_section("步骤8：数据一致性校验")
    consistency_ok = True
    try:
        if stats and graph_data:
            type_nodes = [n for n in graph_data['nodes'] if n['type'] == 'type']
            func_nodes = [n for n in graph_data['nodes'] if n['type'] == 'function']
            
            print(f"   📊 数据一致性检查:")
            print(f"      - 统计中的类型数: {stats['type_count']}")
            print(f"      - 图谱中的类型节点: {len(type_nodes)}")
            print(f"      - 统计中的函数数: {stats['function_count']}")
            print(f"      - 图谱中的函数节点: {len(func_nodes)}")
            
            # 验证一致性
            type_ok = stats['type_count'] == len(type_nodes)
            func_ok = stats['function_count'] == len(func_nodes)
            
            if type_ok and func_ok:
                print(f"   ✅ 数据一致性验证通过")
                test_results.append(print_test_result("数据一致性校验", True))
            else:
                print(f"   ⚠️ 数据可能不一致")
                test_results.append(print_test_result("数据一致性校验", False))
        else:
            test_results.append(print_test_result("数据一致性校验", False))
    except Exception as e:
        print(f"   ❌ 一致性校验异常: {e}")
        test_results.append(print_test_result("数据一致性校验", False))
    
    # 步骤9：重复同步测试（增量更新）
    print_section("步骤9：重复同步测试（增量更新）")
    try:
        print("   🔄 执行第二次同步（验证增量更新）...")
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/api/projects/{project_id}/sync", timeout=300)
        second_sync_duration = time.time() - start_time
        
        if response.status_code == 200:
            sync_result = response.json()
            print(f"   ✅ 第二次同步完成:")
            print(f"      - 处理文件数: {sync_result['files_processed']}")
            print(f"      - 耗时: {second_sync_duration:.2f} 秒")
            
            if second_sync_duration < sync_duration * 0.5:
                print(f"      - 增量更新优化验证通过 (更快)")
            
            test_results.append(print_test_result("重复同步测试", True))
        else:
            test_results.append(print_test_result("重复同步测试", False))
    except Exception as e:
        print(f"   ❌ 重复同步异常: {e}")
        test_results.append(print_test_result("重复同步测试", False))
    
    # 步骤10：删除项目
    print_section("步骤10：删除测试项目")
    try:
        response = requests.delete(f"{BASE_URL}/api/projects/{project_id}")
        if response.status_code == 200:
            print(f"   ✅ 项目删除成功")
            test_results.append(print_test_result("删除项目", True))
        else:
            test_results.append(print_test_result("删除项目", False))
    except Exception as e:
        print(f"   ❌ 删除异常: {e}")
        test_results.append(print_test_result("删除项目", False))
    
    # 步骤11：停止服务
    print_section("步骤11：停止API服务")
    if api_process:
        api_process.terminate()
        try:
            api_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            api_process.kill()
            api_process.wait()
        print("   ✅ API服务已停止")
    
    # 最终结果汇总
    print_section("业务场景测试最终结果")
    total_tests = len(test_results)
    passed_tests = len([r for r in test_results if r])
    failed_tests = total_tests - passed_tests
    
    print(f"\n📊 总体统计: {passed_tests}/{total_tests} 通过")
    if failed_tests == 0:
        print("🎉 所有业务场景测试通过！系统运行稳定！")
        return 0
    else:
        print(f"⚠️ 有 {failed_tests} 个测试失败")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
