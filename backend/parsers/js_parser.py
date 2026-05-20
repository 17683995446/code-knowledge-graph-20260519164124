import os
import re
from typing import List, Dict, Any, Optional
from .base import BaseParser, ParseResult

class JSParser(BaseParser):
    def get_language(self) -> str:
        return "javascript"

    def parse(self, file_path: str) -> ParseResult:
        result = ParseResult()

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            result = self._parse_content(content)
        except Exception as e:
            print(f"Error parsing JavaScript file {file_path}: {e}")

        return result

    def _parse_content(self, content: str) -> ParseResult:
        result = ParseResult()
        lines = content.split('\n')

        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()

            # 跳过空行和注释
            if not stripped or stripped.startswith('//'):
                i += 1
                continue

            # 检测是否是类定义
            class_match = re.match(r'^(export\s+)?(abstract\s+)?class\s+(\w+)(.*?)\s*\{?', stripped)
            if class_match:
                class_name = class_match.group(3)
                is_interface = False
                kind = 'class'

                # 检查是否是接口
                if 'extends' in class_match.group(4) or class_match.group(2):
                    kind = 'class'
                elif not stripped.endswith('{') and i + 1 < len(lines):
                    # 检查下一行是否是 { 或 interface关键字
                    next_line = lines[i + 1].strip()
                    if 'implements' in next_line or 'extends' in next_line:
                        kind = 'class'
                    elif 'interface' in stripped.lower():
                        is_interface = True
                        kind = 'interface'

                # 查找类体的结束
                end_line = self._find_brace_block_end(lines, i)

                result.types.append({
                    'name': class_name,
                    'kind': kind,
                    'line_start': i + 1,
                    'line_end': end_line
                })

                # 解析类内的方法
                j = i + 1
                brace_count = 0
                in_class_body = False

                while j < end_line and j < len(lines):
                    method_line = lines[j].strip()

                    # 统计大括号
                    brace_count += method_line.count('{') - method_line.count('}')

                    # 当进入类体时开始解析方法
                    if brace_count > 0 and not in_class_body:
                        in_class_body = True

                    if in_class_body:
                        # 解析方法定义
                        method_info = self._parse_method_def(method_line, j)
                        if method_info:
                            method_info['type_name'] = class_name
                            result.functions.append(method_info)

                    j += 1

                i = end_line
                continue

            # 检测interface声明
            interface_match = re.match(r'^(export\s+)?interface\s+(\w+)', stripped)
            if interface_match:
                interface_name = interface_match.group(2)
                end_line = self._find_brace_block_end(lines, i)

                result.types.append({
                    'name': interface_name,
                    'kind': 'interface',
                    'line_start': i + 1,
                    'line_end': end_line
                })

                i = end_line
                continue

            # 检测函数声明 (function关键字)
            func_match = re.match(r'^(export\s+)?function\s+(\w+)', stripped)
            if func_match:
                func_name = func_match.group(2)

                result.functions.append({
                    'name': func_name,
                    'type_name': None,
                    'line_start': i + 1,
                    'line_end': i + 1
                })

                i += 1
                continue

            # 检测箭头函数变量声明
            arrow_match = re.match(r'^(export\s+)?(const|let|var)\s+(\w+)\s*=.*=>', stripped)
            if arrow_match:
                func_name = arrow_match.group(3)

                result.functions.append({
                    'name': func_name,
                    'type_name': None,
                    'line_start': i + 1,
                    'line_end': i + 1
                })

                i += 1
                continue

            # 检测async函数
            async_match = re.match(r'^(export\s+)?async\s+(function\s+)?(\w+)', stripped)
            if async_match:
                func_name = async_match.group(3)

                # 确保不是类定义
                if not stripped.startswith('class'):
                    result.functions.append({
                        'name': func_name,
                        'type_name': None,
                        'line_start': i + 1,
                        'line_end': i + 1
                    })

                i += 1
                continue

            i += 1

        return result

    def _parse_method_def(self, line: str, line_num: int) -> Optional[Dict[str, Any]]:
        """解析方法定义"""
        stripped = line.strip()

        # 跳过空行和注释
        if not stripped or stripped.startswith('//') or stripped.startswith('/*'):
            return None

        # 匹配方法定义
        patterns = [
            r'^(static\s+)?(async\s+)?(\w+)\s*\([^)]*\)\s*[:{]',
            r'^(async\s+)?(\w+)\s*<[^>]+>\s*\([^)]*\)\s*[:{]',
            r'^(constructor)\s*\(',
        ]

        for pattern in patterns:
            match = re.match(pattern, stripped)
            if match:
                # 提取方法名
                if match.group(1) == 'constructor':
                    method_name = 'constructor'
                else:
                    groups = [g for g in match.groups() if g]
                    # 跳过关键字
                    for g in groups:
                        if g in ['static', 'async']:
                            continue
                        method_name = g
                        break
                    else:
                        continue

                # 过滤掉非方法名
                if method_name and not self._is_keyword(method_name):
                    return {
                        'name': method_name,
                        'type_name': None,
                        'line_start': line_num + 1,
                        'line_end': line_num + 1
                    }

        return None

    def _is_keyword(self, word: str) -> bool:
        """检查是否是JavaScript关键字"""
        keywords = {
            'if', 'else', 'for', 'while', 'do', 'switch', 'case', 'break',
            'continue', 'return', 'throw', 'try', 'catch', 'finally',
            'new', 'delete', 'typeof', 'instanceof', 'void',
            'this', 'super', 'class', 'extends', 'import', 'export',
            'from', 'default', 'as', 'const', 'let', 'var',
            'function', 'async', 'await', 'yield', 'static',
            'get', 'set', 'of', 'in'
        }
        return word in keywords

    def _find_brace_block_end(self, lines: List[str], start_line: int) -> int:
        """查找大括号块的结束位置"""
        i = start_line
        brace_count = 0
        started = False

        while i < len(lines):
            line = lines[i]

            for char in line:
                if char == '{':
                    brace_count += 1
                    started = True
                elif char == '}':
                    brace_count -= 1

            if started and brace_count == 0:
                return i + 1

            i += 1

        return len(lines)
