#!/usr/bin/env python3
"""
全编程语言代码知识图谱系统 - API集成测试
测试所有FastAPI接口
"""
import sys
import os
import time
import tempfile
import requests
import subprocess
sys.path.insert(0, '/workspace')

print("=" * 80)
print("API集成测试")
print("=" * 80)

# 启动API服务
print("\n🚀 启动API服务中...")
api_process = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8000"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

# 等待服务启动
time.sleep(3)

BASE_URL = "http://127.0.0.1:8000"

try:
    # ==================== 测试1：健康检查 ====================
    print("\n✅ 测试1：健康检查")
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200, f"健康检查失败: {response}"
    print(f"   ✅ 健康检查通过: {response.json()}")
    
    # ==================== 测试2：根路径 ====================
    print("\n✅ 测试2：根路径")
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200
    print(f"   ✅ 根路径通过: {response.json()}")
    
    # ==================== 测试3：创建项目 ====================
    print("\n✅ 测试3：创建项目")
    
    # 创建临时测试目录
    test_dir = tempfile.mkdtemp()
    with open(os.path.join(test_dir, "test.py"), "w") as f:
        f.write("class TestClass:\n    def test_method(self):\n        pass\n")
    
    create_data = {
        "name": "API测试项目",
        "path": test_dir
    }
    response = requests.post(f"{BASE_URL}/api/projects", json=create_data)
    assert response.status_code == 200, f"创建项目失败: {response.text}"
    project = response.json()
    project_id = project["id"]
    print(f"   ✅ 项目创建成功: ID={project_id}, 名称={project['name']}")
    
    # ==================== 测试4：获取项目列表 ====================
    print("\n✅ 测试4：获取项目列表")
    response = requests.get(f"{BASE_URL}/api/projects")
    assert response.status_code == 200
    projects = response.json()
    print(f"   ✅ 项目列表获取成功: 共 {len(projects)} 个项目")
    
    # ==================== 测试5：同步项目 ====================
    print("\n✅ 测试5：同步项目")
    response = requests.post(f"{BASE_URL}/api/projects/{project_id}/sync")
    assert response.status_code == 200
    sync_result = response.json()
    print(f"   ✅ 同步成功: {sync_result}")
    
    # ==================== 测试6：获取项目统计 ====================
    print("\n✅ 测试6：获取项目统计")
    response = requests.get(f"{BASE_URL}/api/projects/{project_id}/stats")
    assert response.status_code == 200
    stats = response.json()
    print(f"   ✅ 统计获取成功: 文件={stats['file_count']}, 类型={stats['type_count']}, 函数={stats['function_count']}")
    
    # ==================== 测试7：获取图谱数据 ====================
    print("\n✅ 测试7：获取图谱数据")
    response = requests.get(f"{BASE_URL}/api/graph/{project_id}")
    assert response.status_code == 200
    graph = response.json()
    print(f"   ✅ 图谱获取成功: 节点={len(graph['nodes'])}, 边={len(graph['links'])}")
    
    # ==================== 测试8：搜索功能 ====================
    print("\n✅ 测试8：搜索功能")
    response = requests.get(f"{BASE_URL}/api/search?project_id={project_id}&query=Test")
    assert response.status_code == 200
    results = response.json()
    print(f"   ✅ 搜索成功: 找到 {len(results)} 个结果")
    
    # ==================== 测试9：删除项目 ====================
    print("\n✅ 测试9：删除项目")
    response = requests.delete(f"{BASE_URL}/api/projects/{project_id}")
    assert response.status_code == 200
    print(f"   ✅ 项目删除成功")
    
    # 清理
    import shutil
    shutil.rmtree(test_dir)
    
    print("\n" + "=" * 80)
    print("🎯 API集成测试 - 全部通过！")
    print("=" * 80)
    sys.exit(0)
    
except Exception as e:
    print(f"\n❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("📋 API集成测试结果")
    print("=" * 80)
    sys.exit(1)
    
finally:
    # 停止API服务
    print("\n🛑 停止API服务...")
    api_process.terminate()
    try:
        api_process.wait(timeout=2)
    except subprocess.TimeoutExpired:
        api_process.kill()
        api_process.wait()
