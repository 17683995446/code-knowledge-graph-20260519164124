"""
输入验证和安全模块
提供全面的参数验证、边界检查和安全防护
"""
import os
import re
import logging
from typing import Optional, Callable, Any
from functools import wraps

logger = logging.getLogger("Validators")

class ValidationError(Exception):
    """验证失败时抛出的异常"""
    pass

def validate_project_name(name: str) -> str:
    """
    验证项目名称
    :param name: 项目名称
    :return: 清理后的名称
    :raises: ValidationError
    """
    if not name or not isinstance(name, str):
        raise ValidationError("项目名称必须为非空字符串")
    
    name = name.strip()
    
    if len(name) == 0:
        raise ValidationError("项目名称不能为空")
    
    if len(name) > 500:
        raise ValidationError("项目名称过长（最大500字符）")
    
    # 防止路径遍历攻击
    if any(c in name for c in ['..', '/', '\\', '\0']):
        raise ValidationError("项目名称包含非法字符")
    
    return name

def validate_project_path(path: str, check_exists: bool = True) -> str:
    """
    验证项目路径
    :param path: 项目路径
    :param check_exists: 是否检查路径存在
    :return: 规范化后的路径
    :raises: ValidationError
    """
    if not path or not isinstance(path, str):
        raise ValidationError("项目路径必须为非空字符串")
    
    path = path.strip()
    
    if len(path) == 0:
        raise ValidationError("项目路径不能为空")
    
    # 规范化路径
    normalized_path = os.path.abspath(os.path.normpath(path))
    
    if check_exists:
        if not os.path.exists(normalized_path):
            raise ValidationError(f"项目路径不存在: {path}")
        
        if not os.path.isdir(normalized_path):
            raise ValidationError(f"不是有效的目录: {path}")
        
        # 检查读取权限
        if not os.access(normalized_path, os.R_OK):
            raise ValidationError(f"没有访问权限: {path}")
    
    return normalized_path

def validate_project_id(project_id: Any) -> int:
    """
    验证项目ID
    :param project_id: 项目ID
    :return: 整数项目ID
    :raises: ValidationError
    """
    try:
        project_id_int = int(project_id)
        if project_id_int <= 0:
            raise ValidationError("项目ID必须为正整数")
        return project_id_int
    except (ValueError, TypeError):
        raise ValidationError("无效的项目ID格式")

def validate_search_query(query: str, max_length: int = 1000) -> str:
    """
    验证搜索查询
    :param query: 搜索查询
    :param max_length: 最大长度
    :return: 清理后的查询
    :raises: ValidationError
    """
    if query is None:
        return ""
    
    query_str = str(query).strip()
    
    if len(query_str) > max_length:
        raise ValidationError(f"搜索查询过长（最大{max_length}字符）")
    
    # 移除潜在危险字符，但保留基本搜索功能
    query_str = re.sub(r'[\0\b\t\n\r]', '', query_str)
    
    return query_str

def validate_integer(value: Any, min_val: Optional[int] = None, max_val: Optional[int] = None, field_name: str = "值") -> int:
    """
    验证整数参数
    :param value: 要验证的值
    :param min_val: 最小值（可选）
    :param max_val: 最大值（可选）
    :param field_name: 字段名称（用于错误消息）
    :return: 验证后的整数
    :raises: ValidationError
    """
    try:
        val = int(value)
        if min_val is not None and val < min_val:
            raise ValidationError(f"{field_name}不能小于{min_val}")
        if max_val is not None and val > max_val:
            raise ValidationError(f"{field_name}不能大于{max_val}")
        return val
    except (ValueError, TypeError):
        raise ValidationError(f"{field_name}必须为有效的整数")

def validate_file_path(file_path: str, base_dir: Optional[str] = None) -> str:
    """
    验证文件路径
    :param file_path: 文件路径
    :param base_dir: 基础目录（防止路径遍历）
    :return: 规范化的路径
    :raises: ValidationError
    """
    if not file_path or not isinstance(file_path, str):
        raise ValidationError("文件路径必须为非空字符串")
    
    file_path = file_path.strip()
    normalized_path = os.path.normpath(file_path)
    
    # 防止路径遍历
    if normalized_path.startswith("..") or normalized_path.startswith("/") or "\\.." in normalized_path:
        raise ValidationError("文件路径包含非法字符")
    
    if base_dir:
        base_dir_normalized = os.path.abspath(base_dir)
        full_path = os.path.abspath(os.path.join(base_dir, normalized_path))
        if not full_path.startswith(base_dir_normalized):
            raise ValidationError("文件路径超出允许范围")
    
    return normalized_path

def safe_like_pattern(pattern: str) -> str:
    """
    安全的LIKE模式处理（防止部分注入风险）
    :param pattern: 原始模式
    :return: 安全的模式
    """
    # 转义SQL LIKE特殊字符
    pattern = pattern.replace('%', '\\%').replace('_', '\\_')
    return pattern
