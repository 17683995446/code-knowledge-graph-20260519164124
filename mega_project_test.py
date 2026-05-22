#!/usr/bin/env python3
"""
专门针对 mega_chaos 项目的深度测试
"""
import sys
import os
import time
import subprocess
import requests
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"
api_process = None


def print_section(title):
    print("\n" + "=" * 100)
    print(f"  📊 {title}")
    print("=" * 100)


def start_server():
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
    global api_process
    if api_process:
        print("停止API服务器...")
        api_process.terminate()
        try:
            api_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            api_process.kill()
            api_process.wait()


def test_mega_chaos():
    print_section("Mega Chaos 项目深度测试")
    
    project_id = None
    try:
        # 第1步: 创建项目
        print_section("步骤1: 创建项目")
        create_data = {
            "name": f"MegaTest_{datetime.now().strftime('%H%M%S')}",
            "path": "/workspace/test_projects/mega_chaos"
        }
        resp = requests.post(f"{BASE_URL}/api/projects", json=create_data)
        print(f"创建项目 - 状态码: {resp.status_code}")
        assert resp.status_code == 200
        project = resp.json()
        project_id = project["id"]
        print(f"✅ 项目创建成功，ID: {project_id}")
        
        # 第2步: 同步项目 - 关键测试！
        print_section("步骤2: 同步 Mega Chaos 项目 (800+ 文件)")
        start_time = time.time()
        
        print("⏳ 开始同步...")
        sync_resp = requests.post(
            f"{BASE_URL}/api/projects/{project_id}/sync",
            timeout=600
        )
        sync_duration = time.time() - start_time
        
        print(f"同步响应: {sync_resp.status_code}")
        if sync_resp.status_code == 200:
            sync_data = sync_resp.json()
            print("✅ 同步完成!")
            print(f"   处理文件数: {sync_data['files_processed']}")
            print(f"   总耗时: {sync_duration:.2f} 秒")
            if sync_data['files_processed'] > 0:
                print(f"   平均速度: {sync_data['files_processed'] / sync_duration:.2f} 文件/秒")
        else:
            print(f"❌ 同步失败")
            print(f"响应内容: {sync_resp.text}")
            return False
        
        # 第3步: 获取统计信息
        print_section("步骤3: 获取项目统计信息")
        stats_resp = requests.get(f"{BASE_URL}/api/projects/{project_id}/stats")
        print(f"统计状态: {stats_resp.status_code}")
        if stats_resp.status_code == 200:
            stats = stats_resp.json()
            print(f"   📈 项目统计:")
            print(f"      - 文件数: {stats['file_count']}")
            print(f"      - 类型数: {stats['type_count']}")
            print(f"      - 函数数: {stats['function_count']}")
            print(f"      - 语言: {stats['languages']}")
        
        # 第4步: 获取图谱数据
        print_section("步骤4: 获取知识图谱数据")
        graph_resp = requests.get(f"{BASE_URL}/api/graph/{project_id}")
        print(f"图谱响应: {graph_resp.status_code}")
        if graph_resp.status_code == 200:
            graph = graph_resp.json()
            print(f"   📊 图谱数据:")
            print(f"      - 节点数: {len(graph['nodes'])}")
            print(f"      - 边数: {len(graph['links'])}")
            
            # 简单验证
            type_count = sum(1 for n in graph['nodes'] if n['type'] == 'type')
            func_count = sum(1 for n in graph['nodes'] if n['type'] == 'function')
            print(f"      - 类型节点: {type_count}")
            print(f"      - 函数节点: {func_count}")
        
        # 第5步: 搜索测试
        print_section("步骤5: 搜索功能测试")
        test_queries = [
            "Auth", "User", "Product", "Database", "Order", "Payment"
        ]
        for query in test_queries:
            search_resp = requests.get(
                f"{BASE_URL}/api/search",
                params={"project_id": project_id, "query": query}
            )
            if search_resp.status_code == 200:
                results = search_resp.json()
                print(f"   '{query}' -> {len(results)} 结果")
        
        # 第6步: 第二次同步 (增量)
        print_section("步骤6: 第二次同步 (验证稳定性)")
        start_time2 = time.time()
        sync2_resp = requests.post(
            f"{BASE_URL}/api/projects/{project_id}/sync",
            timeout=600
        )
        sync2_duration = time.time() - start_time2
        
        if sync2_resp.status_code == 200:
            sync2_data = sync2_resp.json()
            print(f"✅ 第二次同步完成!")
            print(f"   处理文件数: {sync2_data['files_processed']}")
            print(f"   耗时: {sync2_duration:.2f} 秒")
            print(f"   对比第一次: {sync2_duration / sync_duration:.1%}")
        
        # 清理
        print_section("清理: 删除项目")
        del_resp = requests.delete(f"{BASE_URL}/api/projects/{project_id}")
        print(f"删除响应: {del_resp.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if project_id:
            try:
                requests.delete(f"{BASE_URL}/api/projects/{project_id}")
            except:
                pass


def main():
    print_section("Mega Chaos 超大项目深度测试")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 启动服务器
        if not start_server():
            print("❌ 服务器启动失败")
            return 1
        
        # 健康检查
        print_section("健康检查")
        health_resp = requests.get(f"{BASE_URL}/health")
        if health_resp.status_code != 200:
            print("❌ 健康检查失败")
            return 1
        print("✅ 健康检查通过")
        
        # 执行测试
        test_ok = test_mega_chaos()
        
        # 结果
        print_section("测试最终结果")
        if test_ok:
            print("🎉🎉🎉 Mega Chaos 测试通过! 系统稳定!")
            return 0
        else:
            print("❌ 测试失败")
            return 1
            
    except Exception as e:
        print(f"❌ 总体异常: {e}")
        return 1
    finally:
        stop_server()


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
