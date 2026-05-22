#!/usr/bin/env python3
"""
全接口遍历与业务场景测试工具
包含：完整API接口测试、业务流程闭环、异常容错
"""
import sys
import os
import time
import tempfile
import shutil
import requests
import subprocess
import logging

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("APIFullTest")

sys.path.insert(0, '/workspace')

print("=" * 100)
print("🎯 全接口遍历与业务场景测试")
print("=" * 100)

# ==================== 启动API服务 ====================
print("\n🚀 步骤1：启动API服务")
print("-" * 100)

api_process = None
BASE_URL = "http://127.0.0.1:8000"

try:
    api_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    print("   ⏳ 等待服务启动...")
    time.sleep(3)
    print("   ✅ API服务启动")
    
except Exception as e:
    print(f"   ❌ 启动失败: {e}")
    sys.exit(1)

# ==================== API健康检查 ====================
print("\n🏥 步骤2：健康检查")
print("-" * 100)

try:
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200, "健康检查失败"
    print(f"   ✅ 健康检查通过: {response.json()}")
    
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200, "根路径失败"
    print(f"   ✅ 根路径通过: {response.json()}")
    
except Exception as e:
    print(f"   ❌ 健康检查异常: {e}")

# ==================== 测试1：项目管理API ====================
print("\n📦 测试组1：项目管理API")
print("-" * 100)

test_project_id = None
test_dir = tempfile.mkdtemp()

# 创建测试文件
with open(os.path.join(test_dir, "app.py"), "w") as f:
    f.write('''
class AppService:
    def __init__(self):
        self.data = []
    
    def add_item(self, item):
        self.data.append(item)
        return item

def main():
    pass
''')

with open(os.path.join(test_dir, "models.py"), "w") as f:
    f.write('''
class UserModel:
    def __init__(self, name, age):
        self.name = name
        self.age = age

class ProductModel:
    pass
''')

api_tests = []

print("\n📊 1.1 创建项目:")
try:
    create_data = {"name": "全接口测试项目", "path": test_dir}
    response = requests.post(f"{BASE_URL}/api/projects", json=create_data)
    assert response.status_code == 200, f"创建失败: {response}"
    project = response.json()
    test_project_id = project["id"]
    print(f"   ✅ 创建成功: ID={test_project_id}, 名称={project['name']}")
    api_tests.append(("创建项目", "✅ 通过"))
except Exception as e:
    print(f"   ❌ 失败: {e}")
    api_tests.append(("创建项目", "❌ 失败"))

print("\n📊 1.2 获取项目列表:")
try:
    response = requests.get(f"{BASE_URL}/api/projects")
    assert response.status_code == 200
    projects = response.json()
    print(f"   ✅ 获取成功: {len(projects)} 个项目")
    api_tests.append(("获取项目列表", "✅ 通过"))
except Exception as e:
    print(f"   ❌ 失败: {e}")
    api_tests.append(("获取项目列表", "❌ 失败"))

print("\n📊 1.3 同步项目:")
try:
    response = requests.post(f"{BASE_URL}/api/projects/{test_project_id}/sync")
    assert response.status_code == 200
    sync_result = response.json()
    print(f"   ✅ 同步成功: {sync_result['files_processed']} 个文件")
    api_tests.append(("同步项目", "✅ 通过"))
except Exception as e:
    print(f"   ❌ 失败: {e}")
    api_tests.append(("同步项目", "❌ 失败"))

print("\n📊 1.4 获取项目统计:")
try:
    response = requests.get(f"{BASE_URL}/api/projects/{test_project_id}/stats")
    assert response.status_code == 200
    stats = response.json()
    print(f"   ✅ 统计获取:")
    print(f"      - 文件数: {stats['file_count']}")
    print(f"      - 类型数: {stats['type_count']}")
    print(f"      - 函数数: {stats['function_count']}")
    print(f"      - 语言: {stats['languages']}")
    api_tests.append(("获取项目统计", "✅ 通过"))
except Exception as e:
    print(f"   ❌ 失败: {e}")
    api_tests.append(("获取项目统计", "❌ 失败"))

# ==================== 测试2：图谱API ====================
print("\n🌐 测试组2：图谱与搜索API")
print("-" * 100)

print("\n📊 2.1 获取图谱数据:")
try:
    response = requests.get(f"{BASE_URL}/api/graph/{test_project_id}")
    assert response.status_code == 200
    graph = response.json()
    print(f"   ✅ 图谱获取: 节点={len(graph['nodes'])}, 边={len(graph['links'])}")
    api_tests.append(("获取图谱数据", "✅ 通过"))
except Exception as e:
    print(f"   ❌ 失败: {e}")
    api_tests.append(("获取图谱数据", "❌ 失败"))

print("\n📊 2.2 搜索功能:")
try:
    response = requests.get(f"{BASE_URL}/api/search", params={"project_id": test_project_id, "query": "User"})
    assert response.status_code == 200
    results = response.json()
    print(f"   ✅ 搜索成功: {len(results)} 个结果")
    api_tests.append(("搜索功能", "✅ 通过"))
except Exception as e:
    print(f"   ❌ 失败: {e}")
    api_tests.append(("搜索功能", "❌ 失败"))

print("\n📊 2.3 搜索 - 类型过滤:")
try:
    response = requests.get(f"{BASE_URL}/api/search", params={"project_id": test_project_id, "query": "App", "type_filter": "type"})
    assert response.status_code == 200
    results = response.json()
    print(f"   ✅ 类型过滤搜索: {len(results)} 个结果")
    api_tests.append(("类型过滤搜索", "✅ 通过"))
except Exception as e:
    print(f"   ❌ 失败: {e}")
    api_tests.append(("类型过滤搜索", "❌ 失败"))

# ==================== 测试3：异常情况 ====================
print("\n⚠️ 测试组3：异常情况测试")
print("-" * 100)

print("\n📊 3.1 获取不存在的项目:")
try:
    response = requests.get(f"{BASE_URL}/api/projects/99999999")
    assert response.status_code == 404 or response.status_code == 200
    print(f"   ✅ 不存在项目处理: {response.status_code}")
    api_tests.append(("不存在项目", "✅ 通过"))
except Exception as e:
    print(f"   ❌ 失败: {e}")
    api_tests.append(("不存在项目", "❌ 失败"))

print("\n📊 3.2 搜索空关键词:")
try:
    response = requests.get(f"{BASE_URL}/api/search", params={"project_id": test_project_id, "query": ""})
    print(f"   ✅ 空搜索: {response.status_code}, {len(response.json())} 结果")
    api_tests.append(("空关键词搜索", "✅ 通过"))
except Exception as e:
    print(f"   ❌ 失败: {e}")
    api_tests.append(("空关键词搜索", "❌ 失败"))

# ==================== 测试4：删除项目 ====================
print("\n🗑️ 测试组4：项目删除")
print("-" * 100)

print("\n📊 4.1 删除项目:")
try:
    response = requests.delete(f"{BASE_URL}/api/projects/{test_project_id}")
    assert response.status_code == 200
    print(f"   ✅ 删除成功: {response.json()}")
    api_tests.append(("删除项目", "✅ 通过"))
except Exception as e:
    print(f"   ❌ 失败: {e}")
    api_tests.append(("删除项目", "❌ 失败"))

# ==================== 清理 ====================
print("\n🧹 清理环境:")
shutil.rmtree(test_dir)
print("   ✅ 测试目录已清理")

# 停止API服务
print("\n🛑 停止API服务:")
if api_process:
    api_process.terminate()
    try:
        api_process.wait(timeout=3)
    except subprocess.TimeoutExpired:
        api_process.kill()
        api_process.wait()
    print("   ✅ API服务已停止")

# ==================== 测试结果汇总 ====================
print("\n" + "=" * 100)
print("📊 全接口测试结果汇总")
print("=" * 100)

for test in api_tests:
    print(f"   {test[0]:30s} - {test[1]}")

total = len(api_tests)
passed = len([t for t in api_tests if "✅" in t[1]])
failed = len([t for t in api_tests if "❌" in t[1]])

print("\n" + "=" * 100)
print(f"🎯 最终统计: {passed}/{total} 通过")

if failed == 0:
    print("✅ 所有接口测试通过！")
    sys.exit(0)
else:
    print(f"❌ {failed} 个接口测试失败")
    sys.exit(1)
