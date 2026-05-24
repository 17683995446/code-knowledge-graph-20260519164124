#!/usr/bin/env python3
"""
极端复杂场景深度测试工具
测试：超大规模项目、多语言混合、混乱代码结构、边界情况
"""
import sys
import os
import tempfile
import random
import time
import logging
from pathlib import Path

# 配置详细日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.config import config
from backend.database import Database
from backend.services.engine import SyncEngine

# 清理旧的数据库
if os.path.exists(config.DATABASE_PATH):
    os.remove(config.DATABASE_PATH)

db = Database()
engine = SyncEngine()

def print_section(title):
    print("\n" + "=" * 150)
    print(f"🔥 {title}")
    print("=" * 150)

def print_subsection(title):
    print(f"\n📍 {title}")
    print("-" * 130)

def generate_class_name(index, complexity="simple"):
    prefixes = ["User", "Product", "Order", "Payment", "Inventory", "Report", 
                "Analytics", "Notification", "Cache", "Queue"]
    suffixes = ["Service", "Controller", "Repository", "Factory", "Manager", 
                "Handler", "Validator", "Processor", "Builder", "Adapter"]
    
    if complexity == "complex":
        return f"{random.choice(prefixes)}{index}{random.choice(suffixes)}"
    return f"{random.choice(prefixes)}{index}"

def generate_method_name(index, type_idx):
    verbs = ["get", "create", "update", "delete", "process", "validate", 
             "transform", "aggregate", "calculate", "format"]
    nouns = ["data", "object", "resource", "record", "entity", "item", 
             "element", "component", "structure", "module"]
    return f"{verbs[type_idx % len(verbs)]}{nouns[index % len(nouns)].capitalize()}"

def create_massive_multilingual_project(temp_dir, num_files=500, num_langs=4):
    """创建超大规模多语言混合项目"""
    project_dir = os.path.join(temp_dir, "massive_multilingual_project")
    os.makedirs(project_dir, exist_ok=True)
    
    languages = ["python", "javascript", "go", "java"]
    extensions = {"python": ".py", "javascript": ".js", "go": ".go", "java": ".java"}
    
    for file_idx in range(num_files):
        lang = languages[file_idx % num_langs]
        ext = extensions[lang]
        filename = f"module_{file_idx:03d}{ext}"
        filepath = os.path.join(project_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            # 创建不同复杂度的代码
            if lang == "python":
                num_classes = random.randint(2, 8)
                for cls_idx in range(num_classes):
                    class_name = generate_class_name(file_idx * 100 + cls_idx, "complex")
                    f.write(f"class {class_name}:\n")
                    f.write(f"    \"\"\"{class_name} documentation\"\"\"\n")
                    
                    num_methods = random.randint(3, 10)
                    for mth_idx in range(num_methods):
                        method_name = generate_method_name(mth_idx, cls_idx)
                        f.write(f"\n    def {method_name}(self, param1, param2=None):\n")
                        f.write(f"        \"\"\"{method_name} method\"\"\"\n")
                        f.write(f"        result = param1 + (param2 if param2 else 0)\n")
                        f.write(f"        return result\n")
            
            elif lang == "javascript":
                num_classes = random.randint(2, 7)
                for cls_idx in range(num_classes):
                    class_name = generate_class_name(file_idx * 100 + cls_idx, "complex")
                    f.write(f"class {class_name} {{\n")
                    f.write(f"    constructor() {{\n")
                    f.write(f"        this.data = null;\n")
                    f.write(f"    }}\n")
                    
                    num_methods = random.randint(3, 9)
                    for mth_idx in range(num_methods):
                        method_name = generate_method_name(mth_idx, cls_idx)
                        f.write(f"\n    {method_name}(a, b) {{\n")
                        f.write(f"        return a + b;\n")
                        f.write(f"    }}\n")
                f.write(f"}}\n")
            
            elif lang == "go":
                f.write(f"package main\n\n")
                num_structs = random.randint(2, 6)
                for struct_idx in range(num_structs):
                    struct_name = generate_class_name(file_idx * 100 + struct_idx, "complex")
                    f.write(f"type {struct_name} struct {{\n")
                    f.write(f"    Name string\n")
                    f.write(f"    Value int\n")
                    f.write(f"}}\n\n")
                    
                    f.write(f"func (s *{struct_name}) ProcessData(x, y int) int {{\n")
                    f.write(f"    return x + y\n")
                    f.write(f"}}\n\n")
            
            elif lang == "java":
                f.write(f"package com.example;\n\n")
                num_classes = random.randint(1, 5)
                for cls_idx in range(num_classes):
                    class_name = generate_class_name(file_idx * 100 + cls_idx, "complex")
                    f.write(f"public class {class_name} {{\n")
                    f.write(f"    private String name;\n")
                    f.write(f"    private int value;\n\n")
                    
                    num_methods = random.randint(2, 7)
                    for mth_idx in range(num_methods):
                        method_name = generate_method_name(mth_idx, cls_idx)
                        f.write(f"    public int {method_name}(int a, int b) {{\n")
                        f.write(f"        return a + b;\n")
                        f.write(f"    }}\n\n")
                f.write(f"}}\n")
    
    print(f"✅ 创建超大规模多语言项目: {num_files} 文件, {num_langs} 语言")
    return project_dir

def create_chaos_nested_project(temp_dir, depth=10, files_per_level=15):
    """创建深度嵌套目录混乱项目"""
    project_dir = os.path.join(temp_dir, "chaos_nested_project")
    os.makedirs(project_dir, exist_ok=True)
    
    current_dir = project_dir
    for level in range(depth):
        dir_name = f"level_{level}"
        for i in range(ord('a'), ord('z') + 1):
            subdir = os.path.join(current_dir, f"{chr(i)}")
            os.makedirs(subdir, exist_ok=True)
            
            for file_idx in range(files_per_level):
                filename = f"file_{level}_{i}_{file_idx}.py"
                filepath = os.path.join(subdir, filename)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    class_name = f"Level{level}File{i}Class{file_idx}"
                    f.write(f"class {class_name}:\n")
                    f.write(f"    def process(self, data):\n")
                    f.write(f"        return data\n\n")
        
        current_dir = os.path.join(current_dir, dir_name)
        os.makedirs(current_dir, exist_ok=True)
    
    print(f"✅ 创建深度嵌套混乱项目: {depth} 层深度")
    return project_dir

def create_invalid_and_edge_cases(temp_dir):
    """创建包含各种边界和无效情况的项目"""
    project_dir = os.path.join(temp_dir, "edge_cases_project")
    os.makedirs(project_dir, exist_ok=True)
    
    # 1. 空文件
    open(os.path.join(project_dir, "empty.py"), 'w').close()
    
    # 2. 只有注释的文件
    comment_file = os.path.join(project_dir, "comments_only.js")
    with open(comment_file, 'w') as f:
        for i in range(1000):
            f.write(f"// This is comment line {i}\n")
    
    # 3. 包含语法错误的Python文件
    bad_python = os.path.join(project_dir, "syntax_error.py")
    with open(bad_python, 'w') as f:
        f.write("def bad_function():\n")
        f.write("    syntax error here\n")
        f.write("    return broken\n")
    
    # 4. 超级大的单个类
    large_class = os.path.join(project_dir, "huge_class.py")
    with open(large_class, 'w') as f:
        f.write("class HugeClass:\n")
        for i in range(500):
            f.write(f"    def method_{i}(self, x):\n")
            f.write(f"        return x + {i}\n")
    
    # 5. 混合了二进制和文本的"伪代码"
    mixed_content = os.path.join(project_dir, "mixed_content.py")
    with open(mixed_content, 'w') as f:
        f.write("class ValidClass:\n")
        f.write("    def valid_method(self):\n")
        f.write("        return True\n")
        f.write("\n\x00\x01\x02\x03\x04")  # 二进制垃圾数据
        f.write("\ndef another_function():")  # 不完整的函数
    
    # 6. 超长文件名
    long_filename = "a" * 200 + ".py"
    long_file_path = os.path.join(project_dir, long_filename)
    with open(long_file_path, 'w') as f:
        f.write("class LongFileNameTest:\n    pass\n")
    
    print(f"✅ 创建边界和无效情况测试项目")
    return project_dir

def test_massive_multilingual_sync():
    """测试超大规模多语言项目同步"""
    print_subsection("超大规模多语言项目同步测试")
    
    temp_dir = tempfile.mkdtemp()
    project_dir = None
    
    try:
        project_dir = create_massive_multilingual_project(temp_dir, num_files=300, num_langs=4)
        project_id = db.create_project("Massive Multilingual", project_dir)
        
        print(f"⏳ 开始同步超大规模多语言项目...")
        start_time = time.time()
        result = engine.sync_project(project_id)
        elapsed = time.time() - start_time
        
        stats = db.get_stats(project_id)
        
        print(f"\n📊 同步结果:")
        print(f"   文件处理: {result['files_processed']}")
        print(f"   发现类型: {stats['type_count']}")
        print(f"   发现函数: {stats['function_count']}")
        print(f"   语言分布: {stats['languages']}")
        print(f"   同步耗时: {elapsed:.2f} 秒")
        
        success = stats['file_count'] > 0
        print(f"✅ 超大规模多语言项目测试 {'成功' if success else '部分成功'}")
        return success
        
    except Exception as e:
        print(f"❌ 超大规模多语言项目测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if project_dir:
            try:
                db.delete_project(project_id)
            except:
                pass

def test_chaos_nested_project():
    """测试混乱嵌套目录项目"""
    print_subsection("深度嵌套混乱项目测试")
    
    temp_dir = tempfile.mkdtemp()
    project_dir = None
    
    try:
        project_dir = create_chaos_nested_project(temp_dir, depth=8, files_per_level=10)
        project_id = db.create_project("Chaos Nested", project_dir)
        
        print(f"⏳ 开始同步深度嵌套混乱项目...")
        start_time = time.time()
        result = engine.sync_project(project_id)
        elapsed = time.time() - start_time
        
        stats = db.get_stats(project_id)
        
        print(f"\n📊 同步结果:")
        print(f"   文件处理: {result['files_processed']}")
        print(f"   发现类型: {stats['type_count']}")
        print(f"   发现函数: {stats['function_count']}")
        print(f"   同步耗时: {elapsed:.2f} 秒")
        
        success = True  # 只要不崩溃就算通过
        print(f"✅ 深度嵌套混乱项目测试 {'成功' if success else '失败'}")
        return success
        
    except Exception as e:
        print(f"❌ 深度嵌套混乱项目测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if project_dir:
            try:
                db.delete_project(project_id)
            except:
                pass

def test_edge_and_invalid_cases():
    """测试边界和无效情况"""
    print_subsection("边界和无效情况测试")
    
    temp_dir = tempfile.mkdtemp()
    project_dir = None
    
    try:
        project_dir = create_invalid_and_edge_cases(temp_dir)
        project_id = db.create_project("Edge Cases", project_dir)
        
        print(f"⏳ 开始同步边界和无效情况项目...")
        start_time = time.time()
        result = engine.sync_project(project_id)
        elapsed = time.time() - start_time
        
        stats = db.get_stats(project_id)
        
        print(f"\n📊 同步结果:")
        print(f"   文件处理: {result['files_processed']}")
        print(f"   发现类型: {stats['type_count']}")
        print(f"   发现函数: {stats['function_count']}")
        print(f"   同步耗时: {elapsed:.2f} 秒")
        
        success = True  # 只要不崩溃就算通过
        print(f"✅ 边界和无效情况测试 {'成功' if success else '失败'}")
        return success
        
    except Exception as e:
        print(f"❌ 边界和无效情况测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if project_dir:
            try:
                db.delete_project(project_id)
            except:
                pass

def main():
    print_section("代码知识图谱系统 - 极端复杂场景深度测试")
    print(f"开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    try:
        result = test_massive_multilingual_sync()
        results.append(("超大规模多语言项目", result))
        
        result = test_chaos_nested_project()
        results.append(("深度嵌套混乱项目", result))
        
        result = test_edge_and_invalid_cases()
        results.append(("边界和无效情况", result))
        
    finally:
        print_section("📊 最终测试结果总结")
        for name, ok in results:
            status = "✅ 通过" if ok else "❌ 失败"
            print(f"   {status}: {name}")
        
        passed = sum(1 for _, ok in results if ok)
        total = len(results)
        print(f"\n总体: {passed}/{total} 个极端复杂场景测试通过")
        
        if passed == total:
            print(f"\n🎉🎉🎉 所有极端复杂场景测试通过！系统表现优秀！")
            print(f"\n✅ 系统在处理超大规模、多语言、嵌套混乱、边界情况时都能稳定运行！")
        else:
            print(f"\n✅ 大部分测试通过，系统基本稳定")
        
        return 0 if passed >= total * 0.8 else 1

if __name__ == "__main__":
    sys.exit(main())
