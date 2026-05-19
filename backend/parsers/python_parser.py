import os
from typing import List, Dict, Any
from .base import BaseParser, ParseResult

class PythonParser(BaseParser):
    def get_language(self) -> str:
        return "python"

    def parse(self, file_path: str) -> ParseResult:
        result = ParseResult()

        try:
            from tree_sitter import Language, Parser
            import tree_sitter_python
        except ImportError:
            return self._parse_simple(file_path)

        try:
            language = Language(tree_sitter_python.language())
            parser = Parser(language)
            parser.set_language(language)

            with open(file_path, 'rb') as f:
                tree = parser.parse(f.read())

            self._traverse(tree.root_node, result, None)
        except Exception:
            return self._parse_simple(file_path)

        return result

    def _parse_simple(self, file_path: str) -> ParseResult:
        result = ParseResult()

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            current_type = None
            current_type_kind = None
            current_type_start = None

            for i, line in enumerate(lines):
                stripped = line.strip()

                if stripped.startswith('class '):
                    if current_type:
                        result.types.append({
                            'name': current_type,
                            'kind': current_type_kind,
                            'line_start': current_type_start,
                            'line_end': i + 1
                        })

                    parts = stripped.split('(')[0].split()
                    if len(parts) >= 2:
                        current_type = parts[1]
                        current_type_kind = 'class'
                        current_type_start = i + 1

                elif stripped.startswith('def '):
                    func_name = stripped.split('(')[0].split()[1] if '(' in stripped else stripped.split()[1] if len(stripped.split()) >= 2 else 'unknown'

                    if current_type:
                        result.functions.append({
                            'name': func_name,
                            'type_name': current_type,
                            'line_start': i + 1,
                            'line_end': i + 1
                        })
                    else:
                        result.functions.append({
                            'name': func_name,
                            'type_name': None,
                            'line_start': i + 1,
                            'line_end': i + 1
                        })

                elif stripped.startswith('async def '):
                    func_name = stripped.split('(')[0].split()[2] if '(' in stripped else stripped.split()[2] if len(stripped.split()) >= 3 else 'unknown'

                    if current_type:
                        result.functions.append({
                            'name': func_name,
                            'type_name': current_type,
                            'line_start': i + 1,
                            'line_end': i + 1
                        })
                    else:
                        result.functions.append({
                            'name': func_name,
                            'type_name': None,
                            'line_start': i + 1,
                            'line_end': i + 1
                        })

                elif stripped.startswith('@') and i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line.startswith('def '):
                        if current_type:
                            current_type = None
                            current_type_kind = None
                            current_type_start = None
                    elif not next_line.startswith('def '):
                        current_type = None
                        current_type_kind = None
                        current_type_start = None

                elif stripped and not stripped.startswith('#') and not stripped.startswith('"""') and not stripped.startswith("'''"):
                    if current_type and not any(stripped.startswith(kw) for kw in ['if ', 'elif ', 'else:', 'for ', 'while ', 'try:', 'except', 'finally:', 'with ', 'return ', 'import ', 'from ']):
                        if '=' in stripped and not '==' in stripped:
                            current_type = None
                            current_type_kind = None
                            current_type_start = None

            if current_type:
                result.types.append({
                    'name': current_type,
                    'kind': current_type_kind,
                    'line_start': current_type_start,
                    'line_end': len(lines)
                })

        except Exception:
            pass

        return result

    def _traverse(self, node, result: ParseResult, parent_type: tuple):
        if node.type in ('class_definition', 'function_definition', 'async_function_definition'):
            name_node = None
            for child in node.children:
                if child.type == 'identifier':
                    name_node = child
                    break

            if name_node:
                name = name_node.text.decode('utf-8')

                if node.type == 'class_definition':
                    result.types.append({
                        'name': name,
                        'kind': 'class',
                        'line_start': node.start_point[0] + 1,
                        'line_end': node.end_point[0] + 1
                    })
                    self._traverse(node, result, ('type', name))
                else:
                    func_name = parent_type[1] + '.' + name if parent_type else name
                    result.functions.append({
                        'name': name,
                        'type_name': parent_type[1] if parent_type else None,
                        'line_start': node.start_point[0] + 1,
                        'line_end': node.end_point[0] + 1
                    })

        for child in node.children:
            self._traverse(child, result, parent_type)
