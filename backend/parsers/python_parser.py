import os
import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from .base import BaseParser, ParseResult

logger = logging.getLogger("PythonParser")

class PythonParser(BaseParser):
    def get_language(self) -> str:
        return "python"

    def parse(self, file_path: str) -> ParseResult:
        logger.debug(f"[parse] 开始解析文件: {file_path}")
        result = ParseResult()

        try:
            logger.debug(f"[parse] 打开文件: {file_path}")
            with open(file_path, 'r', encoding='utf-8') as f:
                logger.debug(f"[parse] 读取文件内容")
                content = f.read()

            logger.debug(f"[parse] 文件读取完成，开始解析内容")
            result = self._parse_content(content)
            logger.debug(f"[parse] 解析完成，发现 {len(result.types)} 个类型和 {len(result.functions)} 个函数")
        except UnicodeDecodeError as e:
            logger.warning(f"[parse] 编码错误，尝试使用其他编码: {file_path}, {e}")
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read()
                result = self._parse_content(content)
            except Exception as e2:
                logger.error(f"[parse] 最终解析失败: {file_path}, {e2}")
        except Exception as e:
            logger.error(f"[parse] 解析 Python 文件 {file_path} 时出错: {e}", exc_info=True)

        return result

    def _parse_content(self, content: str) -> ParseResult:
        logger.debug(f"[_parse_content] 开始解析内容，共 {len(content.splitlines())} 行")
        result = ParseResult()
        lines = content.split('\n')

        i = 0
        while i < len(lines):
            logger.debug(f"[_parse_content] 处理第 {i} 行")
            line = lines[i]
            stripped = line.strip()

            # 跳过空行和注释
            if not stripped or stripped.startswith('#'):
                logger.debug(f"[_parse_content] 跳过空行或注释 (第 {i} 行)")
                i += 1
                continue

            # 检查装饰器
            is_dataclass = False
            is_abstract = False
            logger.debug(f"[_parse_content] 检查装饰器")
            while stripped.startswith('@'):
                logger.debug(f"[_parse_content] 发现装饰器: {stripped[:50]}...")
                if '@dataclass' in stripped:
                    is_dataclass = True
                    logger.debug(f"[_parse_content] 识别为 dataclass")
                elif '@abstractmethod' in stripped or 'ABC' in stripped:
                    is_abstract = True
                    logger.debug(f"[_parse_content] 识别为 abstract")
                i += 1
                if i < len(lines):
                    line = lines[i]
                    stripped = line.strip()
                else:
                    break

            if not stripped:
                logger.debug(f"[_parse_content] 空内容，跳过")
                continue

            # 解析类定义
            class_match = re.match(r'^class\s+(\w+)(.*?):', stripped)
            if class_match:
                class_name = class_match.group(1)
                logger.debug(f"[_parse_content] 发现类定义: {class_name}")
                kind = 'class'

                if is_dataclass:
                    kind = 'dataclass'
                elif is_abstract:
                    kind = 'abstract_class'

                logger.debug(f"[_parse_content] 类类型: {kind}")
                # 查找类的结束位置
                end_line = self._find_indent_block_end(lines, i)
                logger.debug(f"[_parse_content] 类结束于第 {end_line} 行")

                result.types.append({
                    'name': class_name,
                    'kind': kind,
                    'line_start': i + 1,
                    'line_end': end_line
                })
                logger.debug(f"[_parse_content] 添加类型到结果: {class_name}")

                # 解析类内的方法
                logger.debug(f"[_parse_content] 解析类内方法，从第 {i + 1} 行到第 {end_line} 行")
                j = i + 1
                while j < end_line and j < len(lines):
                    method_line = lines[j].strip()

                    if method_line.startswith('def ') or method_line.startswith('async def '):
                        logger.debug(f"[_parse_content] 发现方法定义 (第 {j} 行)")
                        method_info = self._parse_function_def(method_line, j)
                        if method_info:
                            method_info['type_name'] = class_name
                            result.functions.append(method_info)
                            logger.debug(f"[_parse_content] 添加方法: {method_info['name']}")

                    j += 1

                i = end_line
                continue

            # 解析顶层函数
            if stripped.startswith('def ') or stripped.startswith('async def '):
                logger.debug(f"[_parse_content] 发现顶层函数 (第 {i} 行)")
                func_info = self._parse_function_def(stripped, i)
                if func_info:
                    result.functions.append(func_info)
                    logger.debug(f"[_parse_content] 添加顶层函数: {func_info['name']}")

            i += 1

        logger.debug(f"[_parse_content] 内容解析完成，返回结果")
        return result

    def _parse_function_def(self, line: str, line_num: int) -> Optional[Dict[str, Any]]:
        logger.debug(f"[_parse_function_def] 解析函数定义 (第 {line_num} 行): {line[:80]}...")
        
        async_prefix = ''
        if line.startswith('async def '):
            async_prefix = 'async '
            func_part = line[len('async def '):]
        else:
            func_part = line[len('def '):]
        
        func_name_match = re.match(r'(\w+)\s*\(', func_part)
        if func_name_match:
            func_name = func_name_match.group(1)
            logger.debug(f"[_parse_function_def] 解析到函数名: {func_name}")
            
            return {
                'name': func_name,
                'kind': 'function',
                'line_start': line_num + 1,
                'line_end': line_num + 1
            }
        
        logger.debug(f"[_parse_function_def] 函数名解析失败")
        return None

    def _find_indent_block_end(self, lines: List[str], start_idx: int) -> int:
        logger.debug(f"[_find_indent_block_end] 查找缩进块结束位置，起始行: {start_idx}")
        
        if start_idx >= len(lines):
            logger.debug(f"[_find_indent_block_end] 起始索引超出范围")
            return start_idx
        
        # 查找起始行的缩进
        start_line = lines[start_idx]
        base_indent = len(start_line) - len(start_line.lstrip())
        logger.debug(f"[_find_indent_block_end] 基础缩进: {base_indent} 个字符")
        
        i = start_idx + 1
        while i < len(lines):
            current_line = lines[i]
            
            # 跳过空行
            if not current_line.strip():
                i += 1
                continue
            
            current_indent = len(current_line) - len(current_line.lstrip())
            
            # 如果遇到缩进更小的非空行，说明块结束
            if current_indent <= base_indent:
                logger.debug(f"[_find_indent_block_end] 在第 {i} 行发现块结束")
                return i
            
            i += 1
        
        # 如果到文件末尾，返回最后一行
        logger.debug(f"[_find_indent_block_end] 块结束于文件末尾")
        return len(lines) - 1
