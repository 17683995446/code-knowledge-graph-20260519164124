import os
import hashlib
import logging
from typing import List, Dict, Any
from ..config import config
from ..database import db
from ..parsers import get_parser_for_language

logger = logging.getLogger("SyncEngine")

class SyncEngine:
    def __init__(self):
        self.db = db

    def get_language_by_extension(self, file_path: str) -> str:
        ext = os.path.splitext(file_path)[1].lower()
        return config.SUPPORTED_LANGUAGES.get(ext, None)

    def calculate_hash(self, file_path: str) -> str:
        """分块计算文件哈希，避免大文件内存问题"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logger.error(f"calculate_hash: 计算文件哈希失败 {file_path}, error: {e}")
            return ""

    def sync_project(self, project_id: int) -> Dict[str, Any]:
        logger.info(f"sync_project: 开始同步项目 project_id={project_id}")
        project = self.db.get_project(project_id)
        if not project:
            logger.error(f"sync_project: 项目不存在 project_id={project_id}")
            return {"success": False, "message": "项目不存在", "files_processed": 0}

        project_path = project['path']
        logger.info(f"sync_project: 项目路径 project_path={project_path}")
        if not os.path.exists(project_path):
            logger.error(f"sync_project: 项目路径不存在 project_path={project_path}")
            return {"success": False, "message": "项目路径不存在", "files_processed": 0}

        files_to_process = []
        logger.info("sync_project: 开始扫描项目目录")
        for root, dirs, files in os.walk(project_path):
            if '__pycache__' in root or 'node_modules' in root or '.git' in root:
                continue

            for file in files:
                file_path = os.path.join(root, file)
                language = self.get_language_by_extension(file_path)

                if language:
                    relative_path = os.path.relpath(file_path, project_path)
                    file_hash = self.calculate_hash(file_path)
                    files_to_process.append({
                        'path': file_path,
                        'relative_path': relative_path,
                        'language': language,
                        'hash': file_hash
                    })

        logger.info(f"sync_project: 扫描完成，发现 {len(files_to_process)} 个待处理文件")
        files_processed = 0
        for idx, file_info in enumerate(files_to_process):
            logger.debug(f"sync_project: 处理文件 {idx+1}/{len(files_to_process)} {file_info['relative_path']} ({file_info['language']})")
            self._process_file(project_id, file_info['path'], file_info['language'], file_info['hash'])
            files_processed += 1
            if files_processed % 50 == 0:
                logger.info(f"sync_project: 已处理 {files_processed}/{len(files_to_process)} 个文件")

        self.db.update_project_time(project_id)
        logger.info(f"sync_project: 项目同步完成，共处理 {files_processed} 个文件")

        return {
            "success": True,
            "message": f"同步完成",
            "files_processed": files_processed
        }

    def _process_file(self, project_id: int, file_path: str, language: str, file_hash: str):
        logger.debug(f"_process_file: 开始处理 file_path={file_path}, language={language}")
        try:
            parser = get_parser_for_language(language)
            if not parser:
                logger.warning(f"_process_file: 不支持的语言 language={language}")
                return

            logger.debug(f"_process_file: 开始解析文件")
            parse_result = parser.parse(file_path)
            logger.debug(f"_process_file: 解析完成，发现 {len(parse_result.types)} 个类型，{len(parse_result.functions)} 个函数")

            file_id = self.db.get_or_create_file(project_id, file_path, language, file_hash)
            logger.debug(f"_process_file: 文件已保存 file_id={file_id}")

            type_map = {}
            for type_info in parse_result.types:
                type_id = self.db.insert_type(
                    file_id,
                    type_info['name'],
                    type_info['kind'],
                    type_info.get('line_start'),
                    type_info.get('line_end')
                )
                type_map[type_info['name']] = type_id
            logger.debug(f"_process_file: 保存了 {len(type_map)} 个类型")

            for func_info in parse_result.functions:
                type_id = type_map.get(func_info['type_name']) if func_info['type_name'] else None
                func_id = self.db.insert_function(
                    file_id,
                    type_id,
                    func_info['name'],
                    func_info.get('line_start'),
                    func_info.get('line_end')
                )
            logger.debug(f"_process_file: 保存了 {len(parse_result.functions)} 个函数")

        except Exception as e:
            logger.error(f"_process_file: 处理文件时出错 file_path={file_path}, error: {str(e)}", exc_info=True)

    def process_file_event(self, project_id: int, file_path: str, event_type: str):
        language = self.get_language_by_extension(file_path)

        if event_type == 'deleted' or event_type == 'modified':
            self.db.delete_file_by_path(project_id, file_path)

        if event_type in ('created', 'modified') and language:
            file_hash = self.calculate_hash(file_path)
            self._process_file(project_id, file_path, language, file_hash)
            self.db.update_project_time(project_id)

engine = SyncEngine()
