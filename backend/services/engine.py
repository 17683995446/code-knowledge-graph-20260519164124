import os
import hashlib
from typing import List, Dict, Any
from ..config import config
from ..database import db
from ..parsers import get_parser_for_language

class SyncEngine:
    def __init__(self):
        self.db = db

    def get_language_by_extension(self, file_path: str) -> str:
        ext = os.path.splitext(file_path)[1].lower()
        return config.SUPPORTED_LANGUAGES.get(ext, None)

    def calculate_hash(self, file_path: str) -> str:
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return ""

    def sync_project(self, project_id: int) -> Dict[str, Any]:
        project = self.db.get_project(project_id)
        if not project:
            return {"success": False, "message": "项目不存在", "files_processed": 0}

        project_path = project['path']
        if not os.path.exists(project_path):
            return {"success": False, "message": "项目路径不存在", "files_processed": 0}

        files_to_process = []
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

        files_processed = 0
        for file_info in files_to_process:
            self._process_file(project_id, file_info['path'], file_info['language'], file_info['hash'])
            files_processed += 1

        self.db.update_project_time(project_id)

        return {
            "success": True,
            "message": f"同步完成",
            "files_processed": files_processed
        }

    def _process_file(self, project_id: int, file_path: str, language: str, file_hash: str):
        try:
            parser = get_parser_for_language(language)
            if not parser:
                return

            parse_result = parser.parse(file_path)

            file_id = self.db.get_or_create_file(project_id, file_path, language, file_hash)

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

            for func_info in parse_result.functions:
                type_id = type_map.get(func_info['type_name']) if func_info['type_name'] else None
                func_id = self.db.insert_function(
                    file_id,
                    type_id,
                    func_info['name'],
                    func_info.get('line_start'),
                    func_info.get('line_end')
                )

        except Exception as e:
            print(f"Error processing file {file_path}: {e}")

    def process_file_event(self, project_id: int, file_path: str, event_type: str):
        language = self.get_language_by_extension(file_path)

        if event_type == 'deleted' or event_type == 'modified':
            self.db.delete_file_by_path(project_id, file_path)

        if event_type in ('created', 'modified') and language:
            file_hash = self.calculate_hash(file_path)
            self._process_file(project_id, file_path, language, file_hash)
            self.db.update_project_time(project_id)

engine = SyncEngine()
