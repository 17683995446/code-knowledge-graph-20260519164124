import os
from typing import List, Dict, Any
from .base import BaseParser, ParseResult

class JSParser(BaseParser):
    def get_language(self) -> str:
        return "javascript"

    def parse(self, file_path: str) -> ParseResult:
        result = ParseResult()

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            lines = content.split('\n')
            i = 0
            while i < len(lines):
                line = lines[i].strip()

                if line.startswith('class ') or line.startswith('export class '):
                    class_name = self._extract_class_name(line)
                    if class_name:
                        result.types.append({
                            'name': class_name,
                            'kind': 'class',
                            'line_start': i + 1,
                            'line_end': i + 1
                        })

                        class_end = self._find_class_end(lines, i)
                        for j in range(i + 1, class_end):
                            method_line = lines[j].strip()
                            if method_line.startswith('static ') or method_line.startswith('async '):
                                method_line = lines[j + 1].strip() if j + 1 < len(lines) else ''

                            if method_line.startswith(method_line.split('(')[0].split()[0] if '(' in method_line else ''):
                                if '(' in method_line:
                                    method_name = method_line.split('(')[0].split()[-1]
                                    if method_name and method_name != class_name:
                                        result.functions.append({
                                            'name': method_name,
                                            'type_name': class_name,
                                            'line_start': j + 1,
                                            'line_end': j + 1
                                        })

                        i = class_end
                        continue

                elif line.startswith('function ') or line.startswith('export function '):
                    func_name = self._extract_function_name(line)
                    if func_name:
                        result.functions.append({
                            'name': func_name,
                            'type_name': None,
                            'line_start': i + 1,
                            'line_end': i + 1
                        })

                elif line.startswith('const ') or line.startswith('let ') or line.startswith('var '):
                    if '=>' in line or line.endswith('='):
                        parts = line.split('=')[0].strip().split()
                        if len(parts) >= 2:
                            func_name = parts[-1]
                            result.functions.append({
                                'name': func_name,
                                'type_name': None,
                                'line_start': i + 1,
                                'line_end': i + 1
                            })

                elif line.startswith('interface ') or line.startswith('export interface '):
                    interface_name = self._extract_interface_name(line)
                    if interface_name:
                        result.types.append({
                            'name': interface_name,
                            'kind': 'interface',
                            'line_start': i + 1,
                            'line_end': i + 1
                        })

                elif line.startswith('type ') or line.startswith('export type '):
                    type_name = self._extract_type_name(line)
                    if type_name:
                        result.types.append({
                            'name': type_name,
                            'kind': 'type_alias',
                            'line_start': i + 1,
                            'line_end': i + 1
                        })

                i += 1

        except Exception:
            pass

        return result

    def _extract_class_name(self, line: str) -> str:
        parts = line.replace('export', '').replace('class', '').strip().split()
        return parts[0] if parts else None

    def _extract_function_name(self, line: str) -> str:
        parts = line.replace('export', '').replace('function', '').strip().split('(')
        return parts[0].strip() if parts else None

    def _extract_interface_name(self, line: str) -> str:
        parts = line.replace('export', '').replace('interface', '').strip().split()
        return parts[0] if parts else None

    def _extract_type_name(self, line: str) -> str:
        parts = line.replace('export', '').replace('type', '').strip().split('=')
        return parts[0].strip() if parts else None

    def _find_class_end(self, lines: List[str], start: int) -> int:
        brace_count = 0
        for i in range(start, len(lines)):
            brace_count += lines[i].count('{')
            brace_count -= lines[i].count('}')
            if brace_count == 0 and i > start:
                return i + 1
        return len(lines)
