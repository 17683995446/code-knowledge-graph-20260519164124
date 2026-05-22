#!/usr/bin/env python3
"""
静态代码核验工具
包含：代码质量检查、常见错误检测、代码规范验证
"""
import sys
import os
import ast
import re
from pathlib import Path

def print_section(title):
    print("\n" + "=" * 100)
    print(f"🔍 {title}")
    print("=" * 100)

def check_python_file(file_path):
    """检查单个Python文件"""
    issues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 1. 语法检查
        try:
            ast.parse(content)
        except SyntaxError as e:
            issues.append({
                'type': '语法错误',
                'severity': '严重',
                'line': e.lineno,
                'message': str(e)
            })
        
        # 2. 代码规范检查
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # 检查过长的行
            if len(line) > 120:
                issues.append({
                    'type': '代码规范',
                    'severity': '建议',
                    'line': i,
                    'message': f'行过长 ({len(line)} 字符)'
                })
            
            # 检查多余的空格
            if line.endswith(' '):
                issues.append({
                    'type': '代码规范',
                    'severity': '轻微',
                    'line': i,
                    'message': '行尾有多余空格'
                })
        
        # 3. 常见错误模式检查
        # 检查 print 语句（应该使用 logging）
        print_matches = re.finditer(r'\bprint\s*\(', content)
        for match in print_matches:
            line_num = content.count('\n', 0, match.start()) + 1
            issues.append({
                'type': '最佳实践',
                'severity': '建议',
                'line': line_num,
                'message': '使用 print 而不是 logging'
            })
        
        # 检查裸露的 except
        bare_except_matches = re.finditer(r'except\s*:', content)
        for match in bare_except_matches:
            line_num = content.count('\n', 0, match.start()) + 1
            issues.append({
                'type': '代码质量',
                'severity': '中等',
                'line': line_num,
                'message': '裸露的 except，应该指定异常类型'
            })
    
    except Exception as e:
        issues.append({
            'type': '文件读取错误',
            'severity': '严重',
            'line': 0,
            'message': str(e)
        })
    
    return issues

def analyze_directory(directory):
    """分析目录中的所有Python文件"""
    all_issues = {}
    python_files = list(Path(directory).rglob("*.py"))
    
    print(f"📁 扫描目录: {directory}")
    print(f"📄 发现 {len(python_files)} 个 Python 文件\n")
    
    for file_path in python_files:
        # 跳过一些目录
        if any(skip in str(file_path) for skip in ['__pycache__', '.git', 'node_modules', 'test_projects']):
            continue
            
        issues = check_python_file(str(file_path))
        if issues:
            all_issues[str(file_path)] = issues
    
    return all_issues

def main():
    print_section("静态代码核验")
    
    backend_dir = "/workspace/backend"
    issues = analyze_directory(backend_dir)
    
    if not issues:
        print("✅ 未发现任何问题！代码质量良好！")
        return 0
    
    total_issues = sum(len(iss) for iss in issues.values())
    print(f"\n⚠️  发现 {total_issues} 个问题，涉及 {len(issues)} 个文件\n")
    
    # 按文件展示问题
    for file_path, file_issues in issues.items():
        print(f"\n📄 文件: {file_path}")
        print("-" * 80)
        
        # 按严重程度排序
        severity_order = {'严重': 0, '中等': 1, '建议': 2, '轻微': 3}
        file_issues.sort(key=lambda x: severity_order.get(x['severity'], 999))
        
        for issue in file_issues:
            severity_icon = {
                '严重': '🔴',
                '中等': '🟡',
                '建议': '🔵',
                '轻微': '⚪'
            }.get(issue['severity'], '⚪')
            
            print(f"   {severity_icon} [{issue['type']}] 第{issue['line']}行: {issue['message']}")
    
    print_section("核验总结")
    
    # 统计各类问题
    severity_counts = {}
    type_counts = {}
    
    for file_issues in issues.values():
        for issue in file_issues:
            severity_counts[issue['severity']] = severity_counts.get(issue['severity'], 0) + 1
            type_counts[issue['type']] = type_counts.get(issue['type'], 0) + 1
    
    print("\n📊 问题统计:")
    for severity, count in sorted(severity_counts.items()):
        print(f"   {severity}: {count} 个")
    
    critical_count = severity_counts.get('严重', 0)
    if critical_count > 0:
        print(f"\n❌ 发现 {critical_count} 个严重问题，需要修复！")
        return 1
    else:
        print("\n✅ 无严重问题，代码质量基本良好")
        return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
