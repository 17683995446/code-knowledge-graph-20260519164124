#!/usr/bin/env python3
import sys
import os

sys.path.insert(0, '/workspace/backend')

from parsers.python_parser import PythonParser
from parsers.js_parser import JSParser
from parsers.go_parser import GoParser

def test_python_parser():
    print("\n" + "="*60)
    print("测试Python解析器 - 复杂场景")
    print("="*60)
    
    parser = PythonParser()
    
    # 测试复杂Python文件
    test_file = '/workspace/test_projects/complex_python/main.py'
    
    if not os.path.exists(test_file):
        print(f"❌ 测试文件不存在: {test_file}")
        return False
    
    print(f"📄 解析文件: {test_file}")
    
    try:
        result = parser.parse(test_file)
        
        print(f"\n✅ 解析成功!")
        print(f"   - 类型/类数量: {len(result.types)}")
        print(f"   - 函数数量: {len(result.functions)}")
        
        print("\n📊 检测到的类型/类:")
        for t in result.types:
            print(f"   - {t['name']} ({t['kind']}) @ 行 {t.get('line_start', 'N/A')}")
        
        print("\n📊 检测到的函数/方法:")
        for f in result.functions[:20]:  # 只显示前20个
            prefix = f"   - {f['name']}"
            if f['type_name']:
                prefix += f" (在 {f['type_name']} 中)"
            prefix += f" @ 行 {f.get('line_start', 'N/A')}"
            print(prefix)
        
        if len(result.functions) > 20:
            print(f"   ... 还有 {len(result.functions) - 20} 个函数")
        
        # 验证特定类型是否被正确解析
        expected_types = ['BaseProcessor', 'Config', 'UserService', 'Order', 'AdvancedCache', 'DataPipeline']
        found_types = [t['name'] for t in result.types]
        
        print("\n🔍 验证关键类型:")
        for expected in expected_types:
            if expected in found_types:
                print(f"   ✅ {expected}")
            else:
                print(f"   ❌ {expected} (未找到)")
        
        # 验证特定函数
        expected_functions = ['create_user', 'get_user', 'process', 'add_transformer', 'validate_email']
        found_functions = [f['name'] for f in result.functions]
        
        print("\n🔍 验证关键函数:")
        for expected in expected_functions:
            if expected in found_functions:
                print(f"   ✅ {expected}")
            else:
                print(f"   ❌ {expected} (未找到)")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 解析失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_js_parser():
    print("\n" + "="*60)
    print("测试JavaScript/TypeScript解析器 - 复杂场景")
    print("="*60)
    
    parser = JSParser()
    
    # 测试复杂JS文件
    test_file = '/workspace/test_projects/complex_js/services/user.ts'
    
    if not os.path.exists(test_file):
        print(f"❌ 测试文件不存在: {test_file}")
        return False
    
    print(f"📄 解析文件: {test_file}")
    
    try:
        result = parser.parse(test_file)
        
        print(f"\n✅ 解析成功!")
        print(f"   - 类型/类数量: {len(result.types)}")
        print(f"   - 函数数量: {len(result.functions)}")
        
        print("\n📊 检测到的类型/类:")
        for t in result.types:
            print(f"   - {t['name']} ({t['kind']}) @ 行 {t.get('line_start', 'N/A')}")
        
        print("\n📊 检测到的函数/方法:")
        for f in result.functions[:20]:
            prefix = f"   - {f['name']}"
            if f['type_name']:
                prefix += f" (在 {f['type_name']} 中)"
            prefix += f" @ 行 {f.get('line_start', 'N/A')}"
            print(prefix)
        
        return True
        
    except Exception as e:
        print(f"\n❌ 解析失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_go_parser():
    print("\n" + "="*60)
    print("测试Go解析器 - 复杂场景")
    print("="*60)
    
    parser = GoParser()
    
    # 测试复杂Go文件
    test_file = '/workspace/test_projects/complex_go/main.go'
    
    if not os.path.exists(test_file):
        print(f"❌ 测试文件不存在: {test_file}")
        return False
    
    print(f"📄 解析文件: {test_file}")
    
    try:
        result = parser.parse(test_file)
        
        print(f"\n✅ 解析成功!")
        print(f"   - 类型/类数量: {len(result.types)}")
        print(f"   - 函数数量: {len(result.functions)}")
        
        print("\n📊 检测到的类型/类:")
        for t in result.types:
            print(f"   - {t['name']} ({t['kind']}) @ 行 {t.get('line_start', 'N/A')}")
        
        print("\n📊 检测到的函数/方法:")
        for f in result.functions[:20]:
            prefix = f"   - {f['name']}"
            if f['type_name']:
                prefix += f" (接收者: {f['type_name']})"
            prefix += f" @ 行 {f.get('line_start', 'N/A')}"
            print(prefix)
        
        return True
        
    except Exception as e:
        print(f"\n❌ 解析失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_integration():
    print("\n" + "="*60)
    print("集成测试 - 通过API创建项目并同步")
    print("="*60)
    
    import requests
    import time
    
    base_url = "http://localhost:8000"
    
    # 测试健康检查
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ 后端服务运行正常")
        else:
            print(f"❌ 后端服务异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法连接后端服务: {e}")
        print("请确保后端服务正在运行: uvicorn backend.main:app --host 0.0.0.0 --port 8000")
        return False
    
    # 创建测试项目
    project_data = {
        "name": "复杂代码库测试",
        "path": "/workspace/test_projects/complex_python"
    }
    
    try:
        response = requests.post(f"{base_url}/api/projects", json=project_data, timeout=10)
        if response.status_code == 200:
            project = response.json()
            project_id = project['id']
            print(f"✅ 项目创建成功: {project['name']} (ID: {project_id})")
        else:
            print(f"❌ 项目创建失败: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ 创建项目失败: {e}")
        return False
    
    # 触发同步
    print("⏳ 正在同步项目...")
    try:
        response = requests.post(f"{base_url}/api/projects/{project_id}/sync", timeout=30)
        if response.status_code == 200:
            sync_result = response.json()
            print(f"✅ 同步完成: {sync_result['files_processed']} 个文件已处理")
        else:
            print(f"❌ 同步失败: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ 同步失败: {e}")
        return False
    
    # 获取统计信息
    try:
        response = requests.get(f"{base_url}/api/projects/{project_id}/stats", timeout=10)
        if response.status_code == 200:
            stats = response.json()
            print(f"\n📊 项目统计:")
            print(f"   - 文件数: {stats['file_count']}")
            print(f"   - 类型数: {stats['type_count']}")
            print(f"   - 函数数: {stats['function_count']}")
            print(f"   - 语言分布: {stats['languages']}")
        else:
            print(f"❌ 获取统计失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 获取统计失败: {e}")
    
    # 获取图谱数据
    try:
        response = requests.get(f"{base_url}/api/graph/{project_id}", timeout=10)
        if response.status_code == 200:
            graph_data = response.json()
            print(f"\n📊 图谱数据:")
            print(f"   - 节点数: {len(graph_data['nodes'])}")
            print(f"   - 关系数: {len(graph_data['links'])}")
            
            # 显示前5个节点
            print("\n   前5个节点:")
            for node in graph_data['nodes'][:5]:
                print(f"   - {node['name']} ({node['type']}, {node['kind']})")
        else:
            print(f"❌ 获取图谱失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 获取图谱失败: {e}")
    
    # 测试搜索
    try:
        response = requests.get(
            f"{base_url}/api/search",
            params={"project_id": project_id, "query": "User"},
            timeout=10
        )
        if response.status_code == 200:
            results = response.json()
            print(f"\n🔍 搜索 'User' 的结果: {len(results)} 个")
            for r in results[:3]:
                print(f"   - {r['name']} ({r['entity_type']}) in {r['file_path']}")
        else:
            print(f"❌ 搜索失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 搜索失败: {e}")
    
    # 清理测试项目
    try:
        response = requests.delete(f"{base_url}/api/projects/{project_id}", timeout=10)
        if response.status_code == 200:
            print(f"\n✅ 测试项目已清理")
        else:
            print(f"\n⚠️ 清理项目失败: {response.status_code}")
    except Exception as e:
        print(f"⚠️ 清理项目失败: {e}")
    
    return True

if __name__ == "__main__":
    print("\n🚀 开始代码知识图谱系统深度测试")
    print("="*60)
    
    results = {
        'Python解析器': test_python_parser(),
        'JS解析器': test_js_parser(),
        'Go解析器': test_go_parser(),
        '集成测试': test_integration(),
    }
    
    print("\n" + "="*60)
    print("📋 测试结果汇总")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{test_name:20s}: {status}")
    
    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)
    
    print(f"\n总计: {passed_tests}/{total_tests} 测试通过")
    
    if passed_tests == total_tests:
        print("\n🎉 所有测试通过!")
        sys.exit(0)
    else:
        print(f"\n⚠️  {total_tests - passed_tests} 个测试失败，需要修复")
        sys.exit(1)
