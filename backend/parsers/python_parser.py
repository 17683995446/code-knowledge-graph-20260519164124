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
        except Exception as e:
            logger.error(f"[parse] 解析 Python 文件 {file_path} 时出错: {e}", exc_info=True)
            print(f"Error parsing Python file {file_path}: {e}")

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
        logger.debug(f"[_parse_function_def] 解析函数定义 (第 {line_num} 行)")
        stripped = line.strip()

        if not (stripped.startswith('def ') or stripped.startswith('async def ')):
            logger.debug(f"[_parse_function_def] 不是有效的函数定义")
            return None

        logger.debug(f"[_parse_function_def] 有效的函数定义")
        # 移除async关键字
        def_part = stripped.replace('async def ', 'def ')
        logger.debug(f"[_parse_function_def] 清理后的定义: {def_part[:50]}...")

        # 提取函数名
        match = re.match(r'def\s+(\w+)\s*\(', def_part)
        if not match:
            logger.debug(f"[_parse_function_def] 无法匹配函数名")
            return None

        func_name = match.group(1)
        logger.debug(f"[_parse_function_def] 提取函数名: {func_name}")

        # 查找函数体结束位置
        indent_match = re.match(r'^(\s*)', line)
        base_indent = len(indent_match.group(1)) if indent_match else 0
        logger.debug(f"[_parse_function_def] 基础缩进: {base_indent}")

        result = {
            'name': func_name,
            'type_name': None,
            'line_start': line_num + 1,
            'line_end': line_num + 1
        }
        logger.debug(f"[_parse_function_def] 返回函数信息")
        return result

    def _find_indent_block_end(self, lines: List[str], start_line: int) -> int:
        """查找缩进块的结束行"""
        logger.debug(f"[_find_indent_block_end] 从第 {start_line} 行查找缩进块结束位置")
        if start_line >= len(lines):
            logger.debug(f"[_find_indent_block_end] 超出范围，返回 {start_line}")
            return start_line

        # 获取类定义的缩进级别
        first_line = lines[start_line]
        indent_match = re.match(r'^(\s*)', first_line)
        base_indent = len(indent_match.group(1)) if indent_match else 0
        logger.debug(f"[_find_indent_block_end] 基础缩进: {base_indent}")

        i = start_line + 1
        while i < len(lines):
            logger.debug(f"[_find_indent_block_end] 检查第 {i} 行")
            line = lines[i]

            # 空行或纯注释行不计入
            if not line.strip() or line.strip().startswith('#'):
                logger.debug(f"[_find_indent_block_end] 空行或注释，跳过")
                i += 1
                continue

            # 获取当前行的缩进
            indent_match = re.match(r'^(\s*)', line)
            current_indent = len(indent_match.group(1)) if indent_match else 0
            logger.debug(f"[_find_indent_block_end] 当前缩进: {current_indent}")

            # 如果缩进回到base_indent或更少，类结束
            if current_indent <= base_indent:
                logger.debug(f"[_find_indent_block_end] 缩进减小，块结束于第 {i} 行")
                return i

            i += 1

        logger.debug(f"[_find_indent_block_end] 到达文件末尾，返回 {len(lines)}")
        return len(lines)
