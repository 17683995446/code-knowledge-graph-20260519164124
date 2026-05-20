import os
import re
from typing import List, Dict, Any, Optional
from .base import BaseParser, ParseResult

class GoParser(BaseParser):
    def get_language(self) -> str:
        return "go"

    def parse(self, file_path: str) -> ParseResult:
        result = ParseResult()

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            result = self._parse_content(content)
        except Exception as e:
            print(f"Error parsing Go file {file_path}: {e}")

        return result

    def _parse_content(self, content: str) -> ParseResult:
        result = ParseResult()
        lines = content.split('\n')

        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()

            # 跳过空行和注释
            if not stripped or stripped.startswith('//') or stripped.startswith('/*') or stripped.startswith('*'):
                i += 1
                continue

            # 检测type定义 (struct, interface, type别名)
            type_match = re.match(r'^type\s+(\w+)(.*?)\s*(struct|interface|type)\s*\{?', stripped)
            if type_match:
                type_name = type_match.group(1)
                type_suffix = type_match.group(2).strip()
                type_kind = type_match.group(3)

                # 处理泛型
                if type_suffix:
                    type_name = type_name + type_suffix

                # 确定类型
                kind = 'type'
                if type_kind == 'struct':
                    kind = 'struct'
                elif type_kind == 'interface':
                    kind = 'interface'

                # 查找类型定义的结束
                if '{' in stripped:
                    end_line = self._find_brace_block_end(lines, i)
                else:
                    end_line = i + 1

                result.types.append({
                    'name': type_name,
                    'kind': kind,
                    'line_start': i + 1,
                    'line_end': end_line
                })

                # 如果是struct，解析字段
                if kind == 'struct':
                    j = i + 1
                    while j < end_line and j < len(lines):
                        field_line = lines[j].strip()
                        field_match = re.match(r'^(\w+)\s+(\*?\w+.*)$', field_line)
                        if field_match:
                            pass  # 字段信息可以进一步处理
                        j += 1

                i = end_line
                continue

            # 检测func定义 (接收者或普通函数)
            func_match = re.match(r'^func\s+(?:\((\w+)\s+(\*?\w+)\)\s+)?(\w+)(.*?)\(', stripped)
            if func_match:
                receiver = func_match.group(1)
                receiver_type = func_match.group(2)
                func_name = func_match.group(3)
                generic_part = func_match.group(4) or ''

                # 如果有泛型参数
                if generic_part:
                    func_name = func_name + generic_part

                result.functions.append({
                    'name': func_name,
                    'type_name': receiver if receiver else None,
                    'receiver_type': receiver_type if receiver else None,
                    'line_start': i + 1,
                    'line_end': i + 1
                })

                i += 1
                continue

            i += 1

        return result

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
