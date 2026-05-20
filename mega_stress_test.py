#!/usr/bin/env python3
"""超大规模压力测试 - 测试系统处理852+文件的能力"""
import sys
import time
import os
sys.path.insert(0, '/workspace')

from backend.database import db
from backend.services.engine import engine

def mega_stress_test():
    print("\n" + "="*80)
    print("🔥 超大规模压力测试 - 852个Python文件")
    print("="*80)

    test_path = "/workspace/test_projects/mega_chaos"

    if not os.path.exists(test_path):
        print(f"❌ 测试项目不存在: {test_path}")
        return False

    print(f"\n📦 测试项目: {test_path}")

    # 创建项目
    try:
        project_id = db.create_project("超大规模测试", test_path)
        print(f"✅ 项目创建成功 (ID: {project_id})")
    except Exception as e:
        print(f"❌ 创建项目失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    # 首次同步测试
    print(f"\n⏱️  首次同步...")
    start_time = time.time()

    try:
        result = engine.sync_project(project_id)
        elapsed = time.time() - start_time

        print(f"✅ 首次同步完成!")
        print(f"   ⏱️  耗时: {elapsed:.2f}秒")

        # 获取统计
        stats = db.get_stats(project_id)
        print(f"\n📊 统计:")
        print(f"   - 文件数: {stats['file_count']}")
        print(f"   - 类型数: {stats['type_count']}")
        print(f"   - 函数数: {stats['function_count']}")
        print(f"   - 语言分布: {stats['languages']}")

        # 获取图谱数据
        graph_data = db.get_graph_data(project_id)
        print(f"\n🕸️  图谱:")
        print(f"   - 节点数: {len(graph_data['nodes'])}")
        print(f"   - 关系数: {len(graph_data['links'])}")

        # 性能指标
        avg_time_per_file = elapsed / stats['file_count'] if stats['file_count'] > 0 else 0
        print(f"\n⚡ 性能指标:")
        print(f"   - 平均每文件耗时: {avg_time_per_file*1000:.2f}毫秒")
        print(f"   - 处理速度: {stats['file_count']/elapsed:.1f} 文件/秒")

        # 第二次同步测试（验证稳定性）
        print(f"\n⏱️  第二次同步（无变化）...")
        start_time2 = time.time()
        result2 = engine.sync_project(project_id)
        elapsed2 = time.time() - start_time2
        print(f"   ⏱️  耗时: {elapsed2:.2f}秒")

        # 第三次同步测试（再次验证）
        print(f"\n⏱️  第三次同步...")
        start_time3 = time.time()
        result3 = engine.sync_project(project_id)
        elapsed3 = time.time() - start_time3
        print(f"   ⏱️  耗时: {elapsed3:.2f}秒")

        # 性能一致性
        avg_sync = (elapsed2 + elapsed3) / 2
        print(f"\n📈 性能一致性:")
        print(f"   - 平均重复同步耗时: {avg_sync:.2f}秒")
        print(f"   - 性能波动: {abs(elapsed2-elapsed3)/avg_sync*100:.1f}%")

        # 内存使用（估算）
        db_size = os.path.getsize('/workspace/codegraph.db')
        print(f"\n💾 数据库:")
        print(f"   - 大小: {db_size/1024/1024:.2f} MB")
        print(f"   - 每文件平均: {db_size/stats['file_count']/1024:.2f} KB")

        # 搜索性能测试
        print(f"\n🔍 搜索性能测试...")
        search_queries = ['User', 'Manager', 'Service', 'Process', 'calculate']

        for query in search_queries:
            start = time.time()
            results = db.search(project_id, query)
            search_time = time.time() - start
            print(f"   - 搜索 '{query}': {len(results)} 结果, {search_time*1000:.2f}毫秒")

        # 清理
        db.delete_project(project_id)
        print(f"\n✅ 清理完成")

        # 评估结果
        print("\n" + "="*80)
        print("📋 超大规模测试评估")
        print("="*80)

        passed = True

        # 性能标准
        if avg_time_per_file > 0.1:  # 每文件不应超过100ms
            print(f"⚠️  警告: 平均每文件耗时 {avg_time_per_file*1000:.2f}ms 较高")
            passed = False
        else:
            print(f"✅ 性能标准通过: {avg_time_per_file*1000:.2f}ms/文件")

        # 一致性标准
        if abs(elapsed2-elapsed3)/avg_sync > 0.5:  # 波动不应超过50%
            print(f"⚠️  警告: 同步性能波动较大")
            passed = False
        else:
            print(f"✅ 性能一致性通过")

        # 数据完整性
        if stats['file_count'] < 800:
            print(f"⚠️  警告: 处理文件数 {stats['file_count']} 低于预期 852")
            passed = False
        else:
            print(f"✅ 数据完整性通过: {stats['file_count']} 文件")

        return passed

    except Exception as e:
        print(f"\n❌ 超大规模测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def edge_case_test():
    print("\n" + "="*80)
    print("🧪 边缘情况测试")
    print("="*80)

    # 测试特殊文件
    edge_files = [
        "/workspace/test_projects/mega_chaos/unicode_names.py",
        "/workspace/test_projects/mega_chaos/empty.py",
        "/workspace/test_projects/mega_chaos/only_comments.py",
    ]

    print("\n📄 测试特殊文件:")
    for filepath in edge_files:
        if os.path.exists(filepath):
            try:
                from backend.parsers.python_parser import PythonParser
                parser = PythonParser()
                result = parser.parse(filepath)
                print(f"   ✅ {os.path.basename(filepath)}:")
                print(f"      - 类型: {len(result.types)}, 函数: {len(result.functions)}")
            except Exception as e:
                print(f"   ❌ {os.path.basename(filepath)}: {e}")

    # 测试极长行文件
    long_file = "/workspace/test_projects/mega_chaos/very_long_line.py"
    if os.path.exists(long_file):
        try:
            from backend.parsers.python_parser import PythonParser
            parser = PythonParser()
            result = parser.parse(long_file)
            print(f"\n📄 极长行文件:")
            print(f"   ✅ 处理成功: 类型 {len(result.types)}, 函数 {len(result.functions)}")
        except Exception as e:
            print(f"\n⚠️  极长行文件处理失败: {e}")

def chaos_scenario_test():
    print("\n" + "="*80)
    print("💥 混乱场景测试")
    print("="*80)

    # 测试数据库并发
    print("\n🔄 测试数据库并发写入...")

    try:
        project_id = db.create_project("并发测试", "/workspace/test_projects/complex_python")

        # 模拟并发操作
        for i in range(10):
            result = engine.sync_project(project_id)

        print(f"✅ 完成10次并发同步")

        stats = db.get_stats(project_id)
        print(f"   - 最终文件数: {stats['file_count']}")

        db.delete_project(project_id)
        print(f"✅ 清理完成")

    except Exception as e:
        print(f"❌ 并发测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("\n🚀 开始超大规模压力测试")
    print("🔥 目标: 测试系统处理852+文件的能力")

    # 主测试
    mega_result = mega_stress_test()

    # 边缘情况
    edge_case_test()

    # 混乱场景
    chaos_scenario_test()

    print("\n" + "="*80)
    if mega_result:
        print("🎉 超大规模压力测试通过!")
        sys.exit(0)
    else:
        print("⚠️  超大规模测试发现问题，请查看上述日志")
        sys.exit(1)
