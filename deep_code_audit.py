#!/usr/bin/env python3
"""
深度代码审计与修复工具 - 第一阶段迭代2
基于代码审计结果进行修复
"""
import sys
import os

def print_section(title):
    print("\n" + "=" * 120)
    print(f"🔍 {title}")
    print("=" * 120)

def print_subsection(title):
    print(f"\n   📌 {title}")
    print("   " + "-" * 100)

def audit_database_module():
    """审计数据库模块"""
    print_section("数据库模块代码审计")
    
    issues = []
    
    print_subsection("审计点1: 异常处理完整性")
    
    print("   ❌ 问题1: create_project 没有处理 UNIQUE constraint 冲突")
    issues.append({
        'file': 'backend/database.py',
        'function': 'create_project',
        'severity': '高',
        'issue': '路径重复时抛出原始异常，用户体验差',
        'fix': '捕获 sqlite3.IntegrityError，提供友好的错误提示'
    })
    
    print("   ❌ 问题2: insert_type 和 insert_function 使用 INSERT OR REPLACE")
    print("           这会意外删除旧数据，可能导致引用失效")
    issues.append({
        'file': 'backend/database.py',
        'functions': ['insert_type', 'insert_function'],
        'severity': '高',
        'issue': '使用 REPLACE 策略会删除旧记录，可能破坏数据完整性',
        'fix': '使用 INSERT OR IGNORE 策略，避免意外删除'
    })
    
    print_subsection("审计点2: 参数验证")
    
    print("   ❌ 问题3: 缺乏参数验证")
    issues.append({
        'file': 'backend/database.py',
        'severity': '中',
        'issue': '没有验证 name, path 等参数是否为空或无效',
        'fix': '添加参数验证逻辑'
    })
    
    print_subsection("审计点3: 资源管理与并发")
    
    print("   ❌ 问题4: SQLite 默认配置不适合高并发")
    issues.append({
        'file': 'backend/database.py',
        'severity': '中',
        'issue': '没有启用 WAL 模式，没有设置 busy_timeout',
        'fix': '添加连接配置优化'
    })
    
    print_subsection("审计点4: 日志完整性")
    
    print("   ⚠️ 问题5: 部分函数缺少日志记录")
    issues.append({
        'file': 'backend/database.py',
        'functions': ['insert_type', 'insert_function', 'search', 'get_stats'],
        'severity': '低',
        'issue': '关键函数缺少详细日志',
        'fix': '添加日志记录'
    })
    
    return issues

def audit_parser_modules():
    """审计解析器模块"""
    print_section("解析器模块代码审计")
    
    issues = []
    
    print_subsection("审计点1: Python解析器")
    
    print("   ⚠️ 问题1: _find_indent_block_end 对嵌套类处理有缺陷")
    issues.append({
        'file': 'backend/parsers/python_parser.py',
        'function': '_find_indent_block_end',
        'severity': '中',
        'issue': '深度嵌套类时缩进判断可能不准确',
        'fix': '优化缩进块的结束判断逻辑'
    })
    
    print_subsection("审计点2: 异常处理")
    
    print("   ❌ 问题2: 解析器在遇到语法错误时可能崩溃")
    issues.append({
        'file': 'backend/parsers/*.py',
        'severity': '中',
        'issue': '某些无效语法可能导致解析器异常',
        'fix': '增强异常捕获，确保单个文件失败不影响整体'
    })
    
    return issues

def audit_engine_module():
    """审计引擎模块"""
    print_section("引擎服务模块代码审计")
    
    issues = []
    
    print_subsection("审计点1: 文件同步逻辑")
    
    print("   ⚠️ 问题1: 同步引擎没有实现真正的增量更新")
    issues.append({
        'file': 'backend/services/engine.py',
        'function': 'sync_project',
        'severity': '中',
        'issue': '每次都重新扫描所有文件，没有利用 hash 做增量判断',
        'fix': '添加文件 hash 对比，实现真正的增量同步'
    })
    
    print_subsection("审计点2: 错误处理")
    
    print("   ❌ 问题2: _process_file 的错误处理太简单")
    issues.append({
        'file': 'backend/services/engine.py',
        'function': '_process_file',
        'severity': '中',
        'issue': '只打印错误，没有记录失败文件列表',
        'fix': '添加失败文件记录机制'
    })
    
    return issues

def audit_router_modules():
    """审计路由模块"""
    print_section("API路由模块代码审计")
    
    issues = []
    
    print_subsection("审计点1: 输入验证")
    
    print("   ❌ 问题1: 路由层缺乏输入验证")
    issues.append({
        'file': 'backend/routers/*.py',
        'severity': '高',
        'issue': '没有验证请求参数的合法性',
        'fix': '使用 Pydantic 模型进行参数验证'
    })
    
    print_subsection("审计点2: 错误响应")
    
    print("   ⚠️ 问题2: 错误响应格式不统一")
    issues.append({
        'file': 'backend/routers/*.py',
        'severity': '低',
        'issue': '不同的路由使用不同的错误响应格式',
        'fix': '统一错误响应格式'
    })
    
    return issues

def show_audit_summary(all_issues):
    """显示审计总结"""
    print_section("代码审计总结")
    
    severity_counts = {'高': 0, '中': 0, '低': 0}
    
    for issue in all_issues:
        severity = issue.get('severity', '低')
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
    
    print(f"\n   📊 问题统计:")
    for severity, count in severity_counts.items():
        emoji = {'高': '🔴', '中': '🟡', '低': '🟢'}[severity]
        print(f"      {emoji} {severity}优先级: {count} 个")
    
    print(f"\n   📝 问题详情:")
    for i, issue in enumerate(all_issues, 1):
        severity = issue.get('severity', '低')
        emoji = {'高': '🔴', '中': '🟡', '低': '🟢'}[severity]
        print(f"\n      {i}. {emoji} [{severity}] {issue.get('file', 'N/A')}")
        if 'function' in issue:
            print(f"         函数: {issue['function']}")
        if 'functions' in issue:
            print(f"         函数: {', '.join(issue['functions'])}")
        print(f"         问题: {issue['issue']}")
        print(f"         建议: {issue['fix']}")
    
    return all_issues

def main():
    print_section("代码知识图谱系统 - 深度代码审计 (第一阶段迭代2)")
    
    all_issues = []
    
    # 审计各个模块
    all_issues.extend(audit_database_module())
    all_issues.extend(audit_parser_modules())
    all_issues.extend(audit_engine_module())
    all_issues.extend(audit_router_modules())
    
    # 显示总结
    show_audit_summary(all_issues)
    
    print_section("审计完成")
    print(f"""
   📋 共发现 {len(all_issues)} 个问题:
      🔴 高优先级: {sum(1 for i in all_issues if i.get('severity') == '高')} 个
      🟡 中优先级: {sum(1 for i in all_issues if i.get('severity') == '中')} 个
      🟢 低优先级: {sum(1 for i in all_issues if i.get('severity') == '低')} 个
   
   🎯 建议行动:
      1. 优先修复高优先级问题（异常处理、输入验证）
      2. 中优先级问题纳入迭代计划
      3. 低优先级问题可在后续优化中处理
""")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
