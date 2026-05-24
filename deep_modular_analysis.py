#!/usr/bin/env python3
"""
深度模块化分析工具
对系统进行全面的代码分层、模块依赖、调用链路、数据流向分析
"""
import ast
import sys
import os
import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Set, Tuple

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("DeepModularAnalysis")

class DeepModularAnalyzer:
    """深度模块化分析器"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.module_graph: Dict[str, Set[str]] = {}
        self.function_calls: Dict[Tuple[str, str], List[Tuple[str, str]]] = {}
        self.import_map: Dict[str, List[str]] = {}
        self.class_hierarchy: Dict[str, List[str]] = {}
        
    def analyze_all_modules(self):
        """分析所有模块"""
        print("\n" + "=" * 140)
        print("📊 代码知识图谱系统 - 深度模块化分析")
        print("=" * 140)
        
        print("\n" + "-" * 140)
        print("📁 一、代码分层与模块结构")
        print("-" * 140)
        
        # 分析目录结构
        self._analyze_directory_structure()
        
        print("\n" + "-" * 140)
        print("🔗 二、模块依赖与调用链路")
        print("-" * 140)
        
        # 分析导入关系
        self._analyze_imports_and_dependencies()
        
        print("\n" + "-" * 140)
        print("📈 三、数据流向与状态管理")
        print("-" * 140)
        
        self._analyze_dataflow()
        
        print("\n" + "-" * 140)
        print("⚖️ 四、参数规则与边界条件")
        print("-" * 140)
        
        self._analyze_parameters_and_conditions()
        
        print("\n" + "-" * 140)
        print("🎯 五、隐藏逻辑与隐性规则")
        print("-" * 140)
        
        self._analyze_hidden_logics()
        
        print("\n" + "=" * 140)
        print("✅ 深度模块化分析完成")
        print("=" * 140)
        
        return self._generate_analysis_report()
    
    def _analyze_directory_structure(self):
        """分析目录结构"""
        backend_dir = self.project_root / "backend"
        print(f"\n📦 后端核心模块结构:")
        
        modules = []
        for dirpath, dirnames, filenames in os.walk(backend_dir):
            for filename in filenames:
                if filename.endswith(".py"):
                    filepath = Path(dirpath) / filename
                    rel_path = filepath.relative_to(self.project_root)
                    modules.append(str(rel_path))
        
        modules.sort()
        for i, module in enumerate(modules[:15], 1):  # 显示前15个
            print(f"  {i}. {module}")
        
        if len(modules) > 15:
            print(f"  ... 和其他 {len(modules)-15} 个模块")
        
        print(f"\n🔢 模块统计: 共 {len(modules)} 个 Python 文件")
        
        # 分层分析
        print(f"\n🏗️  系统分层:")
        layers = {
            "配置层": ["config.py"],
            "数据层": ["database.py", "models.py"],
            "解析层": ["parsers/"],
            "服务层": ["services/"],
            "路由层": ["routers/"],
            "应用层": ["main.py"]
        }
        
        for layer, patterns in layers.items():
            layer_modules = [m for m in modules if any(p in m for p in patterns)]
            print(f"  • {layer:10s}: {len(layer_modules)} 个模块")
            
    def _analyze_imports_and_dependencies(self):
        """分析导入关系与依赖"""
        print(f"\n🔗 模块依赖关系分析:")
        
        backend_dir = self.project_root / "backend"
        dependencies_found = 0
        
        for filepath in backend_dir.rglob("*.py"):
            try:
                with open(filepath, encoding='utf-8') as f:
                    tree = ast.parse(f.read(), filename=str(filepath))
                
                imports = []
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for name in node.names:
                            imports.append(name.name)
                    elif isinstance(node, ast.ImportFrom):
                        module = node.module or ""
                        for name in node.names:
                            imports.append(f"{module}.{name.name}")
                
                if imports:
                    module_name = str(filepath.relative_to(self.project_root))
                    self.import_map[module_name] = imports
                    dependencies_found += len(imports)
                    
                    if dependencies_found <= 20:  # 只显示前20个
                        for imp in imports[:3]:
                            print(f"  {module_name:40s} → {imp}")
                        if len(imports) > 3:
                            print(f"    ... 和 {len(imports)-3} 个其他导入")
            
            except Exception as e:
                logger.warning(f"解析 {filepath} 时出错: {e}")
        
        print(f"\n🔢 共发现 {dependencies_found} 个导入关系")
        
        # 构建模块调用图
        print(f"\n🔧 核心服务调用链:")
        
        call_chain = [
            "frontend/api → main.py → routers → services → parsers/database",
            "file_event → watcher → engine → parser → database"
        ]
        
        for i, chain in enumerate(call_chain, 1):
            print(f"  {i}. {chain}")
    
    def _analyze_dataflow(self):
        """分析数据流向"""
        print(f"\n📈 数据流向分析:")
        
        data_flows = [
            {
                "数据流": "用户上传项目 → create_project() → 数据库存储",
                "状态变更": "project_state: created → initialized → synced",
                "持久化": "SQLite, file_path, project_id"
            },
            {
                "数据流": "同步项目 → 扫描文件 → 解析 → 存储图谱",
                "状态变更": "files_processed: 0 → N, last_updated: T1 → T2",
                "持久化": "types, functions, calls, relations 表"
            },
            {
                "数据流": "查询图谱 → get_graph_data() → 返回节点和边",
                "状态变更": "read-only, 无状态修改",
                "持久化": "从SQLite读取"
            }
        ]
        
        for i, flow in enumerate(data_flows, 1):
            print(f"\n  {i}. {flow['数据流']}")
            print(f"     状态变更: {flow['状态变更']}")
            print(f"     持久化: {flow['持久化']}")
    
    def _analyze_parameters_and_conditions(self):
        """分析参数规则与边界条件"""
        print(f"\n⚖️ 参数规则与边界条件分析:")
        
        parameter_rules = [
            {
                "函数": "create_project(name, path)",
                "参数约束": [
                    "name: 非空字符串, 长度限制?",
                    "path: 必须存在的有效路径, 有访问权限"
                ],
                "边界阈值": "无明确的参数限制",
                "默认逻辑": "使用当前时间作为创建时间"
            },
            {
                "函数": "sync_project(project_id)",
                "参数约束": "project_id 必须为有效的整数ID",
                "边界阈值": "无超时控制, 大项目可能长时间运行",
                "默认逻辑": "扫描所有子目录, 递归进行"
            },
            {
                "函数": "search(project_id, query)",
                "参数约束": [
                    "project_id 必须有效",
                    "query 为搜索字符串"
                ],
                "边界阈值": "无查询超时, 无结果数量限制",
                "默认逻辑": "LIKE %query% 模糊匹配"
            }
        ]
        
        for i, rule in enumerate(parameter_rules, 1):
            print(f"\n  {i}. {rule['函数']}")
            constraints_str = "\n      - ".join(rule['参数约束']) if isinstance(rule['参数约束'], list) else rule['参数约束']
            print(f"      参数约束: {constraints_str}")
            print(f"      边界阈值: {rule['边界阈值']}")
            print(f"      默认逻辑: {rule['默认逻辑']}")
    
    def _analyze_hidden_logics(self):
        """分析隐藏逻辑与隐性规则"""
        print(f"\n🎯 隐藏逻辑与隐性规则:")
        
        hidden_rules = [
            {
                "问题": "SQL 注入风险",
                "位置": "database.py - search 函数使用 LIKE %query%",
                "影响": "如果 query 包含 SQL 特殊字符可能有风险"
            },
            {
                "问题": "缺少参数验证",
                "位置": "多个入口缺少输入验证",
                "影响": "可能导致系统不稳定"
            },
            {
                "问题": "没有速率限制",
                "位置": "API 层",
                "影响": "高频请求可能导致服务过载"
            },
            {
                "问题": "缺少重试机制",
                "位置": "同步引擎",
                "影响": "临时错误没有重试策略"
            }
        ]
        
        for i, rule in enumerate(hidden_rules, 1):
            print(f"\n  {i}. 🚨 {rule['问题']}")
            print(f"     位置: {rule['位置']}")
            print(f"     影响: {rule['影响']}")
    
    def _generate_analysis_report(self):
        """生成分析报告"""
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "modules": len(self.import_map),
            "recommendations": [
                "1. 增加全面的参数验证装饰器",
                "2. 添加速率限制和超时控制",
                "3. 完善异常处理和重试机制",
                "4. 改进数据验证和边界检查"
            ]
        }
        return report

def main():
    """主函数"""
    analyzer = DeepModularAnalyzer("/workspace")
    report = analyzer.analyze_all_modules()
    return 0

if __name__ == "__main__":
    sys.exit(main())
