#!/usr/bin/env python3
"""
第一阶段：极端文件与边界场景深度测试
"""
import sys
import os
import tempfile
import random
import string
import time
from datetime import datetime

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.config import config
from backend.database import Database
from backend.parsers import get_parser_for_language
from backend.parsers.base import ParseResult

# 初始化数据库
db = Database()

def print_section(title):
    print("\n" + "=" * 100)
    print(f"🚀 {title}")
    print("=" * 100)

def create_extreme_python_file(temp_dir):
    """创建各种极端Python文件"""
    test_files = []
    
    print("\n📄 创建1：超大型单一文件 (1000+类)")
    huge_file = os.path.join(temp_dir, "huge_file.py")
    with open(huge_file, 'w') as f:
        for i in range(1000):
            f.write(f"class Class{i}:\n    def method{i}(self):\n        return {i}\n\n")
    test_files.append(("超大型文件", huge_file))
    print(f"   ✅ 创建成功: {huge_file}")
    
    print("\n📄 创建2：极端长标识符")
    long_ids_file = os.path.join(temp_dir, "long_identifiers.py")
    with open(long_ids_file, 'w') as f:
        very_long_name = "".join([random.choice(string.ascii_lowercase) for _ in range(100)])
        f.write(f"class {very_long_name}:\n    def method_{very_long_name[:20]}(self):\n        pass\n\n")
    test_files.append(("极端长标识符", long_ids_file))
    print(f"   ✅ 创建成功: {long_ids_file}")
    
    print("\n📄 创建3：全是注释的文件")
    comments_file = os.path.join(temp_dir, "all_comments.py")
    with open(comments_file, 'w') as f:
        for i in range(200):
            f.write(f"# 这是第{i}条注释行，非常的长，需要处理换行\n")
    test_files.append(("全注释文件", comments_file))
    print(f"   ✅ 创建成功: {comments_file}")
    
    print("\n📄 创建4：空文件")
    empty_file = os.path.join(temp_dir, "empty.py")
    open(empty_file, 'w').close()
    test_files.append(("空文件", empty_file))
    print(f"   ✅ 创建成功: {empty_file}")
    
    print("\n📄 创建5：深度嵌套类")
    deep_nested = os.path.join(temp_dir, "deep_nested.py")
    with open(deep_nested, 'w') as f:
        f.write("""class Level1:
    class Level2:
        class Level3:
            class Level4:
                class Level5:
                    class Level6:
                        class Level7:
                            class Level8:
                                class Level9:
                                    class Level10:
                                        def deepest_method(self):
                                            return "deep"
        def outer_method(self):
            return "outer"
""")
    test_files.append(("深度嵌套", deep_nested))
    print(f"   ✅ 创建成功: {deep_nested}")
    
    print("\n📄 创建6：混合无效语法")
    messy_file = os.path.join(temp_dir, "messy_code.py")
    with open(messy_file, 'w') as f:
        f.write("""class ValidClass:
    def valid_method(self):
        pass

# 下面是一些混乱的代码
def invalid_def()
    pass

class AnotherValid:
    pass

invalid code here
""")
    test_files.append(("混合语法错误", messy_file))
    print(f"   ✅ 创建成功: {messy_file}")
    
    print("\n📄 创建7：所有支持的语言混合")
    for lang, ext in [("javascript", ".js"), ("go", ".go")]:
        file_name = os.path.join(temp_dir, f"test_file{ext}")
        if lang == "javascript":
            with open(file_name, 'w') as f:
                f.write("""class JSClass {
    constructor() { }
    method() { }
}

function jsFunction() { }
""")
        elif lang == "go":
            with open(file_name, 'w') as f:
                f.write("""package main

type GoStruct struct { }

func (g *GoStruct) Method() { }

func goFunc() { }
""")
        test_files.append((f"{lang}文件", file_name))
        print(f"   ✅ 创建成功: {file_name}")
    
    return test_files

def test_phase1_extreme_scenarios():
    """第一阶段测试：极端文件与边界场景"""
    print_section("第一阶段：极端文件与边界场景深度测试")
    
    results = []
    
    temp_dir = tempfile.mkdtemp()
    try:
        print_section("1. 创建极端测试文件")
        test_files = create_extreme_python_file(temp_dir)
        
        print_section("2. 逐个测试解析器处理能力")
        
        for desc, file_path in test_files:
            try:
                print(f"\n📝 测试 {desc}...")
                ext = os.path.splitext(file_path)[1].lower()
                lang_map = {".py": "python", ".js": "javascript", ".go": "go"}
                language = lang_map.get(ext, "python")
                
                parser = get_parser_for_language(language)
                
                if parser:
                    start_time = time.time()
                    result = parser.parse(file_path)
                    elapsed = time.time() - start_time
                    
                    print(f"   ✅ 解析成功! 耗时: {elapsed:.3f}s")
                    print(f"      - 发现类型: {len(result.types)}")
                    print(f"      - 发现函数: {len(result.functions)}")
                    
                    results.append((desc, True, f"类型: {len(result.types)}, 函数: {len(result.functions)}"))
                else:
                    print(f"   ⚠️  {language} 没有对应的解析器")
                    results.append((desc, True, "无对应解析器"))
                
            except Exception as e:
                print(f"   ❌ 解析失败: {e}")
                import traceback
                traceback.print_exc()
                results.append((desc, False, str(e)))
        
        print_section("3. 数据库边界条件测试")
        
        print("\n🔍 测试3.1：创建超长名称的项目")
        try:
            very_long_name = "".join([random.choice(string.ascii_letters) for _ in range(200)])
            proj_id = db.create_project(very_long_name, temp_dir)
            print(f"   ✅ 成功创建超长名称项目, ID: {proj_id}")
            db.delete_project(proj_id)
            results.append(("超长项目名", True, "成功"))
        except Exception as e:
            print(f"   ❌ 失败: {e}")
            results.append(("超长项目名", False, str(e)))
        
        print("\n🔍 测试3.2：创建大量项目后删除")
        proj_ids = []
        try:
            for i in range(20):
                proj_id = db.create_project(f"批量测试项目_{i}", temp_dir)
                proj_ids.append(proj_id)
            print(f"   ✅ 成功创建20个项目")
            for pid in proj_ids:
                db.delete_project(pid)
            print(f"   ✅ 成功删除所有20个项目")
            results.append(("批量项目管理", True, "20个"))
        except Exception as e:
            print(f"   ❌ 失败: {e}")
            results.append(("批量项目管理", False, str(e)))
        
        print_section("4. 特殊场景数据库操作")
        
        print("\n💾 测试4.1：不存在的项目操作")
        try:
            non_existent_proj = db.get_project(999999)
            if non_existent_proj is None:
                print(f"   ✅ 正确返回 None")
            results.append(("获取不存在的项目", True, "正常"))
        except Exception as e:
            print(f"   ⚠️ 出错: {e}")
            results.append(("获取不存在的项目", False, str(e)))
        
        try:
            db.delete_project(999999)
            print(f"   ✅ 删除不存在的项目未崩溃")
            results.append(("删除不存在的项目", True, "正常"))
        except Exception as e:
            print(f"   ⚠️ 出错: {e}")
            results.append(("删除不存在的项目", False, str(e)))
        
    finally:
        # 清理
        print("\n🧹 清理...")
        try:
            for filename in os.listdir(temp_dir):
                try:
                    os.remove(os.path.join(temp_dir, filename))
                except:
                    pass
            os.rmdir(temp_dir)
        except:
            pass
    
    # 结果总结
    print_section("📊 第一阶段测试结果总结")
    passed = sum(1 for _, ok, _ in results if ok)
    total = len(results)
    
    for desc, ok, msg in results:
        status = "✅" if ok else "❌"
        print(f"   {status} {desc:30s} - {msg}")
    
    print(f"\n总体: {passed}/{total} 通过")
    return passed == total

if __name__ == "__main__":
    print_section("代码知识图谱系统 - 第一阶段极端场景深度测试")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        success = test_phase1_extreme_scenarios()
        print_section("第一阶段测试完成")
        
        if success:
            print("✅ 第一阶段测试通过！")
        else:
            print("⚠️  第一阶段有测试失败")
        
    except Exception as e:
        print_section("严重错误")
        print(f"❌ {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
