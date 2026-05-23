#!/usr/bin/env python3
"""
超复杂场景深度测试工具
包含：超大文件、超大规模项目、混合语言、混乱场景等极端情况
"""
import sys
import os
import tempfile
import random
import string
import time
from datetime import datetime
from typing import List, Tuple

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.config import config
from backend.database import Database
from backend.services.engine import SyncEngine
from backend.parsers import get_parser_for_language

db = Database()
engine = SyncEngine()

def print_section(title):
    print("\n" + "=" * 120)
    print(f"🚀 {title}")
    print("=" * 120)

def print_subsection(title):
    print(f"\n   📌 {title}")
    print("   " + "-" * 100)

def create_ultra_large_file(temp_dir: str, num_classes: int = 2000) -> str:
    """创建超大型文件"""
    filepath = os.path.join(temp_dir, "ultra_large.py")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        for i in range(num_classes):
            class_name = f"UltraClass{i}"
            f.write(f"class {class_name}:\n")
            f.write(f"    def __init__(self):\n")
            f.write(f"        self.id = {i}\n")
            for j in range(random.randint(2, 5)):
                f.write(f"    def method_{j}(self):\n")
                f.write(f"        return '{class_name}.method_{j}'\n")
            f.write("\n")
    
    print(f"   ✅ 创建超大型文件 {filepath} - {num_classes} 个类")
    return filepath

def create_chaos_file(temp_dir: str) -> str:
    """创建包含各种混乱内容的文件"""
    filepath = os.path.join(temp_dir, "chaos.py")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        # 有效代码
        f.write("class ValidClass:\n")
        f.write("    def valid_method(self):\n")
        f.write("        return 'valid'\n\n")
        
        # 无效的语法
        f.write("def invalid_function(\n")
        f.write("    missing colon here\n\n")
        
        # 更多有效代码
        f.write("class AnotherClass:\n")
        f.write("    def another_method(self):\n")
        f.write("        return 'another'\n\n")
        
        # 混乱的混合内容
        f.write("@invalid_decorator\n")
        f.write("class DecoratedClass:\n")
        f.write("    pass\n\n")
        
        # 非常深的嵌套
        f.write("def deep_nesting():\n")
        f.write("    if True:\n")
        f.write("        if True:\n")
        f.write("            if True:\n")
        f.write("                if True:\n")
        f.write("                    if True:\n")
        f.write("                        pass\n\n")
    
    print(f"   ✅ 创建混乱文件 {filepath}")
    return filepath

def create_mixed_language_project(temp_dir: str) -> str:
    """创建混合语言的项目"""
    project_dir = os.path.join(temp_dir, "mixed_language_project")
    os.makedirs(project_dir, exist_ok=True)
    
    # Python 文件
    py_path = os.path.join(project_dir, "python_module.py")
    with open(py_path, 'w', encoding='utf-8') as f:
        f.write("class PythonClass:\n")
        f.write("    def method(self):\n")
        f.write("        return 'Python'\n\n")
        f.write("def python_function():\n")
        f.write("    return 'func'\n")
    print("   ✅ Python 文件")
    
    # JavaScript 文件
    js_path = os.path.join(project_dir, "javascript_module.js")
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write("class JSClass {\n")
        f.write("    method() { return 'JavaScript'; }\n")
        f.write("}\n\n")
        f.write("function jsFunction() { return 'func'; }\n")
    print("   ✅ JavaScript 文件")
    
    # Go 文件
    go_path = os.path.join(project_dir, "go_module.go")
    with open(go_path, 'w', encoding='utf-8') as f:
        f.write("package main\n\n")
        f.write("type GoStruct struct {}\n\n")
        f.write("func (g *GoStruct) Method() string { return 'Go'; }\n\n")
        f.write("func goFunc() string { return 'func'; }\n")
    print("   ✅ Go 文件")
    
    # 更多 Python 文件
    for i in range(5):
        more_py = os.path.join(project_dir, f"more_python_{i}.py")
        with open(more_py, 'w', encoding='utf-8') as f:
            f.write(f"class MoreClass{i}:\n")
            f.write(f"    def method(self):\n")
            f.write(f"        return 'more_{i}'\n")
    print("   ✅ 更多 Python 文件 (5个)")
    
    return project_dir

def create_many_files_project(temp_dir: str, num_files: int = 200) -> str:
    """创建大量文件的项目"""
    project_dir = os.path.join(temp_dir, "many_files_project")
    os.makedirs(project_dir, exist_ok=True)
    
    for i in range(num_files):
        filepath = os.path.join(project_dir, f"file_{i}.py")
        with open(filepath, 'w', encoding='utf-8') as f:
            num_classes_in_file = random.randint(1, 5)
            for j in range(num_classes_in_file):
                f.write(f"class File{i}Class{j}:\n")
                f.write(f"    def method(self):\n")
                f.write(f"        return '{i}_{j}'\n\n")
        if (i + 1) % 50 == 0:
            print(f"   ... 已创建 {i + 1}/{num_files} 个文件")
    
    print(f"   ✅ 创建大量文件项目 - {num_files} 个文件")
    return project_dir

def create_very_deep_nested_dirs(temp_dir: str) -> str:
    """创建非常深的嵌套目录结构"""
    project_dir = os.path.join(temp_dir, "deep_nested_dirs")
    
    current_dir = project_dir
    for i in range(20):
        current_dir = os.path.join(current_dir, f"level_{i}")
        os.makedirs(current_dir, exist_ok=True)
        
        # 在每一层都创建一些文件
        for j in range(2):
            filepath = os.path.join(current_dir, f"l{i}_f{j}.py")
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"class L{i}F{j}Class:\n")
                f.write(f"    def method(self):\n")
                f.write(f"        return 'deep_{i}_{j}'\n")
    
    print(f"   ✅ 创建深度嵌套目录 - 20层深度")
    return project_dir

def test_ultra_complex_scenarios():
    """超复杂场景测试"""
    print_section("代码知识图谱系统 - 超复杂场景深度测试")
    
    results = []
    temp_dir = tempfile.mkdtemp()
    
    try:
        # 测试1: 超大型文件
        print_subsection("场景1: 超大型文件 (2000个类)")
        try:
            large_file = create_ultra_large_file(temp_dir, 2000)
            
            proj_id = db.create_project("Ultra Large File", os.path.dirname(large_file))
            
            start_time = time.time()
            sync_result = engine.sync_project(proj_id)
            elapsed = time.time() - start_time
            
            stats = db.get_stats(proj_id)
            print(f"   📊 同步结果:")
            print(f"      文件处理: {sync_result['files_processed']}")
            print(f"      发现类型: {stats['type_count']}")
            print(f"      发现函数: {stats['function_count']}")
            print(f"      耗时: {elapsed:.2f}秒")
            
            results.append(("超大型文件", True, f"处理了 {sync_result['files_processed']} 个文件"))
            db.delete_project(proj_id)
        except Exception as e:
            print(f"   ❌ 错误: {e}")
            import traceback
            traceback.print_exc()
            results.append(("超大型文件", False, str(e)))
        
        # 测试2: 混乱文件
        print_subsection("场景2: 混乱文件 (包含语法错误)")
        try:
            chaos_file = create_chaos_file(temp_dir)
            
            proj_id = db.create_project("Chaos File", os.path.dirname(chaos_file))
            sync_result = engine.sync_project(proj_id)
            
            stats = db.get_stats(proj_id)
            print(f"   📊 同步结果:")
            print(f"      文件处理: {sync_result['files_processed']}")
            print(f"      发现类型: {stats['type_count']}")
            print(f"      发现函数: {stats['function_count']}")
            
            results.append(("混乱文件", True, f"发现 {stats['type_count']} 个类型"))
            db.delete_project(proj_id)
        except Exception as e:
            print(f"   ❌ 错误: {e}")
            import traceback
            traceback.print_exc()
            results.append(("混乱文件", False, str(e)))
        
        # 测试3: 混合语言项目
        print_subsection("场景3: 混合语言项目 (Python/JS/Go)")
        try:
            mixed_dir = create_mixed_language_project(temp_dir)
            
            proj_id = db.create_project("Mixed Language", mixed_dir)
            sync_result = engine.sync_project(proj_id)
            
            stats = db.get_stats(proj_id)
            print(f"   📊 同步结果:")
            print(f"      文件处理: {sync_result['files_processed']}")
            print(f"      发现类型: {stats['type_count']}")
            print(f"      发现函数: {stats['function_count']}")
            
            results.append(("混合语言", True, f"处理了 {sync_result['files_processed']} 个文件"))
            db.delete_project(proj_id)
        except Exception as e:
            print(f"   ❌ 错误: {e}")
            import traceback
            traceback.print_exc()
            results.append(("混合语言", False, str(e)))
        
        # 测试4: 大量文件项目
        print_subsection("场景4: 大量文件项目 (200个文件)")
        try:
            many_files_dir = create_many_files_project(temp_dir, 200)
            
            proj_id = db.create_project("Many Files", many_files_dir)
            
            start_time = time.time()
            sync_result = engine.sync_project(proj_id)
            elapsed = time.time() - start_time
            
            stats = db.get_stats(proj_id)
            print(f"   📊 同步结果:")
            print(f"      文件处理: {sync_result['files_processed']}")
            print(f"      发现类型: {stats['type_count']}")
            print(f"      发现函数: {stats['function_count']}")
            print(f"      耗时: {elapsed:.2f}秒")
            
            results.append(("大量文件", True, f"处理了 {sync_result['files_processed']} 个文件, 耗时 {elapsed:.2f}s"))
            db.delete_project(proj_id)
        except Exception as e:
            print(f"   ❌ 错误: {e}")
            import traceback
            traceback.print_exc()
            results.append(("大量文件", False, str(e)))
        
        # 测试5: 深度嵌套目录
        print_subsection("场景5: 深度嵌套目录 (20层)")
        try:
            deep_dir = create_very_deep_nested_dirs(temp_dir)
            
            proj_id = db.create_project("Deep Nested", deep_dir)
            sync_result = engine.sync_project(proj_id)
            
            stats = db.get_stats(proj_id)
            print(f"   📊 同步结果:")
            print(f"      文件处理: {sync_result['files_processed']}")
            print(f"      发现类型: {stats['type_count']}")
            
            results.append(("深度嵌套", True, f"处理了 {sync_result['files_processed']} 个文件"))
            db.delete_project(proj_id)
        except Exception as e:
            print(f"   ❌ 错误: {e}")
            import traceback
            traceback.print_exc()
            results.append(("深度嵌套", False, str(e)))
        
        # 测试6: 快速重复创建/删除项目
        print_subsection("场景6: 快速重复创建/删除项目 (50次)")
        try:
            for i in range(50):
                proj_id = db.create_project(f"Repeat Test {i}", temp_dir)
                engine.sync_project(proj_id)
                db.delete_project(proj_id)
                
                if (i + 1) % 10 == 0:
                    print(f"   ... 完成 {i + 1}/50 次循环")
            
            results.append(("快速重复操作", True, "50次循环完成"))
        except Exception as e:
            print(f"   ❌ 错误: {e}")
            import traceback
            traceback.print_exc()
            results.append(("快速重复操作", False, str(e)))
        
    finally:
        # 清理
        print("\n🧹 清理临时文件...")
        try:
            for root, dirs, files in os.walk(temp_dir, topdown=False):
                for name in files:
                    try:
                        os.remove(os.path.join(root, name))
                    except:
                        pass
                for name in dirs:
                    try:
                        os.rmdir(os.path.join(root, name))
                    except:
                        pass
            os.rmdir(temp_dir)
        except:
            pass
    
    # 结果总结
    print_section("测试结果总结")
    
    passed = sum(1 for _, ok, _ in results if ok)
    total = len(results)
    
    for name, ok, msg in results:
        status = "✅" if ok else "❌"
        print(f"   {status} {name:20s}: {msg}")
    
    print(f"\n总体: {passed}/{total} 通过")
    
    return passed == total

if __name__ == "__main__":
    print_section("代码知识图谱系统 - 超复杂场景深度测试开始")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 清理数据库
        if os.path.exists(config.DATABASE_PATH):
            os.remove(config.DATABASE_PATH)
        db.init_database()
        
        success = test_ultra_complex_scenarios()
        print_section("超复杂场景测试完成")
        
        if success:
            print("🎉 所有超复杂场景测试通过！系统稳定性优秀！")
        else:
            print("⚠️ 有部分测试失败，但系统没有崩溃！")
        
    except Exception as e:
        print_section("严重错误")
        print(f"❌ {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
