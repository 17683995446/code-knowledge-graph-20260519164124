from typing import List, Dict, Any
from .base import BaseParser, ParseResult

class GoParser(BaseParser):
    def get_language(self) -> str:
        return "go"

    def parse(self, file_path: str) -> ParseResult:
        result = ParseResult()

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            current_type = None
            current_type_kind = None
            current_type_start = None

            for i, line in enumerate(lines):
                stripped = line.strip()

                if stripped.startswith('type '):
                    parts = stripped.split()
                    if len(parts) >= 2:
                        type_name = parts[1]

                        if len(parts) >= 3 and parts[2] == 'struct':
                            current_type = type_name
                            current_type_kind = 'struct'
                            current_type_start = i + 1
                            result.types.append({
                                'name': type_name,
                                'kind': 'struct',
                                'line_start': i + 1,
                                'line_end': i + 1
                            })

                        elif len(parts) >= 3 and parts[2] == 'interface':
                            current_type = type_name
                            current_type_kind = 'interface'
                            current_type_start = i + 1
                            result.types.append({
                                'name': type_name,
                                'kind': 'interface',
                                'line_start': i + 1,
                                'line_end': i + 1
                            })

                        else:
                            current_type = type_name
                            current_type_kind = 'type'
                            current_type_start = i + 1
                            result.types.append({
                                'name': type_name,
                                'kind': 'type',
                                'line_start': i + 1,
                                'line_end': i + 1
                            })

                elif stripped.startswith('func '):
                    func_def = stripped.replace('func', '').strip()

                    if func_def.startswith('('):
                        parts = func_def.split(')')
                        if len(parts) >= 2:
                            receiver = parts[0][1:]
                            func_part = parts[1].strip()
                            func_name = func_part.split('(')[0].strip()

                            if current_type and receiver == current_type:
                                result.functions.append({
                                    'name': func_name,
                                    'type_name': current_type,
                                    'line_start': i + 1,
                                    'line_end': i + 1
                                })
                            else:
                                result.functions.append({
                                    'name': func_name,
                                    'type_name': receiver,
                                    'line_start': i + 1,
                                    'line_end': i + 1
                                })
                    else:
                        func_name = func_def.split('(')[0].strip()
                        result.functions.append({
                            'name': func_name,
                            'type_name': None,
                            'line_start': i + 1,
                            'line_end': i + 1
                        })

            if current_type:
                pass

        except Exception:
            pass

        return result
