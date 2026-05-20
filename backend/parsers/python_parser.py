import os
import re
from typing import List, Dict, Any, Optional, Tuple
from .base import BaseParser, ParseResult

class PythonParser(BaseParser):
    def get_language(self) -> str:
        return "python"

    def parse(self, file_path: str) -> ParseResult:
        result = ParseResult()

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            result = self._parse_content(content)
        except Exception as e:
            print(f"Error parsing Python file {file_path}: {e}")

        return result

    def _parse_content(self, content: str) -> ParseResult:
        result = ParseResult()
        lines = content.split('\n')

        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()

            # 跳过空行和注释
            if not stripped or stripped.startswith('#'):
                i += 1
                continue

            # 检查装饰器
            is_dataclass = False
            is_abstract = False
            while stripped.startswith('@'):
                if '@dataclass' in stripped:
                    is_dataclass = True
                elif '@abstractmethod' in stripped or 'ABC' in stripped:
                    is_abstract = True
                i += 1
                if i < len(lines):
                    line = lines[i]
                    stripped = line.strip()
                else:
                    break

            if not stripped:
                continue

            # 解析类定义
            class_match = re.match(r'^class\s+(\w+)(.*?):', stripped)
            if class_match:
                class_name = class_match.group(1)
                kind = 'class'

                if is_dataclass:
                    kind = 'dataclass'
                elif is_abstract:
                    kind = 'abstract_class'

                # 查找类的结束位置
                end_line = self._find_indent_block_end(lines, i)

                result.types.append({
                    'name': class_name,
                    'kind': kind,
                    'line_start': i + 1,
                    'line_end': end_line
                })

                # 解析类内的方法
                j = i + 1
                while j < end_line and j < len(lines):
                    method_line = lines[j].strip()

                    if method_line.startswith('def ') or method_line.startswith('async def '):
                        method_info = self._parse_function_def(method_line, j)
                        if method_info:
                            method_info['type_name'] = class_name
                            result.functions.append(method_info)

                    j += 1

                i = end_line
                continue

            # 解析顶层函数
            if stripped.startswith('def ') or stripped.startswith('async def '):
                func_info = self._parse_function_def(stripped, i)
                if func_info:
                    result.functions.append(func_info)

            i += 1

        return result

    def _parse_function_def(self, line: str, line_num: int) -> Optional[Dict[str, Any]]:
        stripped = line.strip()

        if not (stripped.startswith('def ') or stripped.startswith('async def ')):
            return None

        # 移除async关键字
        def_part = stripped.replace('async def ', 'def ')

        # 提取函数名
        match = re.match(r'def\s+(\w+)\s*\(', def_part)
        if not match:
            return None

        func_name = match.group(1)

        # 查找函数体结束位置
        indent_match = re.match(r'^(\s*)', line)
        base_indent = len(indent_match.group(1)) if indent_match else 0

        return {
            'name': func_name,
            'type_name': None,
            'line_start': line_num + 1,
            'line_end': line_num + 1
        }

    def _find_indent_block_end(self, lines: List[str], start_line: int) -> int:
        """查找缩进块的结束行"""
        if start_line >= len(lines):
            return start_line

        # 获取类定义的缩进级别
        first_line = lines[start_line]
        indent_match = re.match(r'^(\s*)', first_line)
        base_indent = len(indent_match.group(1)) if indent_match else 0

        i = start_line + 1
        while i < len(lines):
            line = lines[i]

            # 空行或纯注释行不计入
            if not line.strip() or line.strip().startswith('#'):
                i += 1
                continue

            # 获取当前行的缩进
            indent_match = re.match(r'^(\s*)', line)
            current_indent = len(indent_match.group(1)) if indent_match else 0

            # 如果缩进回到base_indent或更少，类结束
            if current_indent <= base_indent:
                return i

            i += 1

        return len(lines)
