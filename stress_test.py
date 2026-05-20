#!/usr/bin/env python3
"""压力测试脚本 - 测试系统的性能和稳定性"""
import sys
import time
import os
sys.path.insert(0, '/workspace')

from backend.database import db
from backend.services.engine import engine

def stress_test():
    print("\n" + "="*60)
    print("大规模代码库压力测试")
    print("="*60)

    test_projects = [
        '/workspace/backend',  # 后端代码本身
        '/workspace/test_projects/complex_python',
        '/workspace/test_projects/complex_js',
        '/workspace/test_projects/complex_go',
    ]

    total_files = 0
    total_types = 0
    total_functions = 0
    total_time = 0

    for i, project_path in enumerate(test_projects, 1):
        if not os.path.exists(project_path):
            print(f"⚠️ 跳过不存在的项目: {project_path}")
            continue

        project_name = os.path.basename(project_path)
        print(f"\n📦 测试项目 {i}: {project_name}")
        print(f"   路径: {project_path}")

        # 创建项目
        try:
            project_id = db.create_project(project_name, project_path)
            print(f"   ✅ 项目创建成功 (ID: {project_id})")
        except Exception as e:
            print(f"   ❌ 创建项目失败: {e}")
            continue

        # 同步
        print(f"   ⏳ 开始同步...")
        start_time = time.time()

        try:
            result = engine.sync_project(project_id)
            elapsed = time.time() - start_time

            print(f"   ✅ 同步完成!")
            print(f"   ⏱️  耗时: {elapsed:.2f}秒")
            print(f"   📄 处理文件: {result['files_processed']}")

            # 获取统计
            stats = db.get_stats(project_id)
            print(f"   📊 统计:")
            print(f"      - 文件数: {stats['file_count']}")
            print(f"      - 类型数: {stats['type_count']}")
            print(f"      - 函数数: {stats['function_count']}")

            total_files += stats['file_count']
            total_types += stats['type_count']
            total_functions += stats['function_count']
            total_time += elapsed

            # 获取图谱数据
            graph_data = db.get_graph_data(project_id)
            print(f"   🕸️  图谱:")
            print(f"      - 节点数: {len(graph_data['nodes'])}")
            print(f"      - 关系数: {len(graph_data['links'])}")

            # 清理
            db.delete_project(project_id)
            print(f"   🧹 项目已清理")

        except Exception as e:
            print(f"   ❌ 同步失败: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "="*60)
    print("压力测试汇总")
    print("="*60)
    print(f"总处理文件数: {total_files}")
    print(f"总检测类型数: {total_types}")
    print(f"总检测函数数: {total_functions}")
    print(f"总耗时: {total_time:.2f}秒")
    print(f"平均每文件耗时: {(total_time/total_files if total_files > 0 else 0):.4f}秒")
    print("="*60)

def edge_case_test():
    print("\n" + "="*60)
    print("边界情况和异常测试")
    print("="*60)

    # 测试空项目
    print("\n📦 测试1: 空目录")
    try:
        project_id = db.create_project("空项目", "/tmp/empty_test_dir")
        os.makedirs("/tmp/empty_test_dir", exist_ok=True)
        result = engine.sync_project(project_id)
        print(f"   ✅ 处理完成: {result['files_processed']} 个文件")
        db.delete_project(project_id)
    except Exception as e:
        print(f"   ⚠️  预期行为: {e}")

    # 测试单个文件
    print("\n📦 测试2: 单个Python文件")
    try:
        test_file = "/workspace/test_projects/complex_python/main.py"
        project_id = db.create_project("单文件测试", "/workspace/test_projects")
        result = engine.sync_project(project_id)
        stats = db.get_stats(project_id)
        print(f"   ✅ 处理完成:")
        print(f"      - 文件数: {stats['file_count']}")
        print(f"      - 类型数: {stats['type_count']}")
        print(f"      - 函数数: {stats['function_count']}")
        db.delete_project(project_id)
    except Exception as e:
        print(f"   ❌ 失败: {e}")

    # 测试重复创建
    print("\n📦 测试3: 重复项目名称")
    try:
        project_id = db.create_project("重复测试", "/workspace/test_projects/complex_python")
        db.create_project("重复测试", "/workspace/test_projects/complex_js")
        print(f"   ❌ 应该抛出异常!")
    except Exception as e:
        print(f"   ✅ 正确拒绝重复名称: {type(e).__name__}")

    print("\n" + "="*60)

def performance_test():
    print("\n" + "="*60)
    print("性能基准测试")
    print("="*60)

    # 多次同步测试
    print("\n🔄 测试1: 重复同步性能")
    try:
        project_id = db.create_project("性能测试", "/workspace/backend")
        print(f"   首次同步:")
        start = time.time()
        result1 = engine.sync_project(project_id)
        time1 = time.time() - start
        stats1 = db.get_stats(project_id)
        print(f"      - 耗时: {time1:.2f}秒")
        print(f"      - 文件: {stats1['file_count']}")

        print(f"   二次同步（无变化）:")
        start = time.time()
        result2 = engine.sync_project(project_id)
        time2 = time.time() - start
        stats2 = db.get_stats(project_id)
        print(f"      - 耗时: {time2:.2f}秒")
        print(f"      - 文件: {stats2['file_count']}")

        print(f"   性能提升: {((time1-time2)/time1*100):.1f}%")

        db.delete_project(project_id)
    except Exception as e:
        print(f"   ❌ 失败: {e}")

    print("\n" + "="*60)

if __name__ == "__main__":
    stress_test()
    edge_case_test()
    performance_test()

    print("\n🎉 所有压力测试完成!")
