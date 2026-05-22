#!/usr/bin/env python3
"""
异常容错测试工具
包含：无效参数、不存在路径、边界情况、错误输入等测试
"""
import sys
import os
import time
import requests
import subprocess
import tempfile
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ExceptionToleranceTest")

BASE_URL = "http://127.0.0.1:8000"

def print_section(title):
    print("\n" + "=" * 100)
    print(f"⚠️  {title}")
    print("=" * 100)

def print_test_result(test_name, success):
    status = "✅ 通过" if success else "❌ 失败"
    print(f"   {test_name:50s} - {status}")
    return success

def test_exception_cases():
    test_results = []
    
    # 测试1: 创建项目 - 空参数
    print_section("测试1: 创建项目 - 无效/空参数")
    try:
        # 空名称
        response = requests.post(f"{BASE_URL}/api/projects", json={"name": "", "path": "/tmp"})
        print(f"   空名称 - 状态码: {response.status_code}")
        
        # 空路径
        response = requests.post(f"{BASE_URL}/api/projects", json={"name": "测试", "path": ""})
        print(f"   空路径 - 状态码: {response.status_code}")
        
        # 完全空
        response = requests.post(f"{BASE_URL}/api/projects", json={})
        print(f"   空请求 - 状态码: {response.status_code}")
        
        test_results.append(print_test_result("无效参数测试", True))
    except Exception as e:
        print(f"   异常: {e}")
        test_results.append(print_test_result("无效参数测试", False))
    
    # 测试2: 创建项目 - 不存在的路径
    print_section("测试2: 创建项目 - 不存在的路径")
    try:
        response = requests.post(f"{BASE_URL}/api/projects", json={
            "name": "无效路径测试",
            "path": "/path/that/does/not/exist/ever/12345"
        })
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {response.text}")
        test_results.append(print_test_result("不存在路径测试", True))
    except Exception as e:
        print(f"   异常: {e}")
        test_results.append(print_test_result("不存在路径测试", False))
    
    # 测试3: 获取项目 - 无效ID
    print_section("测试3: 获取/操作不存在的项目")
    try:
        invalid_ids = [99999, -1, 0, "abc"]
        for invalid_id in invalid_ids:
            response = requests.get(f"{BASE_URL}/api/projects/{invalid_id}")
            print(f"   ID {invalid_id} - 状态码: {response.status_code}")
            
            # 测试同步不存在的项目
            sync_response = requests.post(f"{BASE_URL}/api/projects/{invalid_id}/sync")
            print(f"   同步ID {invalid_id} - 状态码: {sync_response.status_code}")
            
            # 测试删除不存在的项目
            del_response = requests.delete(f"{BASE_URL}/api/projects/{invalid_id}")
            print(f"   删除ID {invalid_id} - 状态码: {del_response.status_code}")
        
        test_results.append(print_test_result("无效项目ID测试", True))
    except Exception as e:
        print(f"   异常: {e}")
        test_results.append(print_test_result("无效项目ID测试", False))
    
    # 测试4: 搜索功能 - 边界情况
    print_section("测试4: 搜索功能 - 边界情况")
    try:
        # 创建一个测试项目先
        temp_dir = tempfile.mkdtemp()
        with open(os.path.join(temp_dir, "test.py"), "w") as f:
            f.write("class TestClass:\n    def test_func(self):\n        pass\n")
        
        create_resp = requests.post(f"{BASE_URL}/api/projects", json={
            "name": "搜索测试项目",
            "path": temp_dir
        })
        project_id = create_resp.json()["id"]
        requests.post(f"{BASE_URL}/api/projects/{project_id}/sync")
        
        # 各种边界搜索
        test_cases = [
            ("空字符串", ""),
            ("非常长的查询", "a" * 1000),
            ("特殊字符", "!@#$%^&*()"),
            ("中文搜索", "测试"),
            ("Unicode", "测试😊"),
            ("SQL注入尝试", "' OR 1=1 --"),
        ]
        
        for desc, query in test_cases:
            response = requests.get(f"{BASE_URL}/api/search", params={
                "project_id": project_id,
                "query": query
            })
            print(f"   {desc} - 状态码: {response.status_code}")
        
        # 清理
        requests.delete(f"{BASE_URL}/api/projects/{project_id}")
        os.rmdir(temp_dir)
        
        test_results.append(print_test_result("搜索边界情况测试", True))
    except Exception as e:
        print(f"   异常: {e}")
        test_results.append(print_test_result("搜索边界情况测试", False))
    
    # 测试5: 同步项目 - 特殊文件
    print_section("测试5: 同步项目 - 特殊情况文件")
    try:
        temp_dir = tempfile.mkdtemp()
        
        # 创建各种特殊文件
        files = [
            ("empty.py", ""),
            ("only_comments.py", "# 这只是注释\n# 另一行注释"),
            ("syntax_error.py", "class InvalidClass\n    def bad_func():\n        pass"),
            ("encoding_test.py", "# -*- coding: gbk -*-\n# 测试编码"),
        ]
        
        for filename, content in files:
            with open(os.path.join(temp_dir, filename), "w", encoding='utf-8') as f:
                f.write(content)
        
        # 创建项目并同步
        create_resp = requests.post(f"{BASE_URL}/api/projects", json={
            "name": "特殊文件测试",
            "path": temp_dir
        })
        project_id = create_resp.json()["id"]
        
        sync_response = requests.post(f"{BASE_URL}/api/projects/{project_id}/sync")
        print(f"   同步完成 - 状态码: {sync_response.status_code}")
        
        stats_response = requests.get(f"{BASE_URL}/api/projects/{project_id}/stats")
        print(f"   统计: {stats_response.json()}")
        
        # 清理
        requests.delete(f"{BASE_URL}/api/projects/{project_id}")
        for filename, _ in files:
            os.remove(os.path.join(temp_dir, filename))
        os.rmdir(temp_dir)
        
        test_results.append(print_test_result("特殊文件同步测试", True))
    except Exception as e:
        print(f"   异常: {e}")
        test_results.append(print_test_result("特殊文件同步测试", False))
    
    # 测试6: 大量并发请求（基础性能）
    print_section("测试6: 高频率API调用")
    try:
        temp_dir = tempfile.mkdtemp()
        with open(os.path.join(temp_dir, "test.py"), "w") as f:
            f.write("class A:\n    pass\n")
        
        create_resp = requests.post(f"{BASE_URL}/api/projects", json={
            "name": "高频率测试",
            "path": temp_dir
        })
        project_id = create_resp.json()["id"]
        requests.post(f"{BASE_URL}/api/projects/{project_id}/sync")
        
        # 快速连续请求
        success_count = 0
        for i in range(20):
            response = requests.get(f"{BASE_URL}/api/projects/{project_id}/stats")
            if response.status_code == 200:
                success_count += 1
        
        print(f"   20次快速请求 - 成功: {success_count}/20")
        
        # 清理
        requests.delete(f"{BASE_URL}/api/projects/{project_id}")
        os.remove(os.path.join(temp_dir, "test.py"))
        os.rmdir(temp_dir)
        
        test_results.append(print_test_result("高频率API调用测试", True))
    except Exception as e:
        print(f"   异常: {e}")
        test_results.append(print_test_result("高频率API调用测试", False))
    
    return test_results

def main():
    print_section("异常容错测试")
    
    # 启动服务
    api_process = None
    try:
        api_process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        time.sleep(2)
        
        test_results = test_exception_cases()
        
        # 停止服务
        if api_process:
            api_process.terminate()
            try:
                api_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                api_process.kill()
                api_process.wait()
        
        # 结果汇总
        print_section("异常容错测试结果汇总")
        total_tests = len(test_results)
        passed_tests = len([r for r in test_results if r])
        failed_tests = total_tests - passed_tests
        
        print(f"\n📊 总体统计: {passed_tests}/{total_tests} 通过")
        if failed_tests == 0:
            print("🎉 所有异常容错测试通过！系统鲁棒性良好！")
            return 0
        else:
            print(f"⚠️  有 {failed_tests} 个测试失败")
            return 1
            
    except Exception as e:
        print(f"测试执行异常: {e}")
        if api_process:
            api_process.terminate()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
