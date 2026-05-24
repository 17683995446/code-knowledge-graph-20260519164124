import os
import hashlib
import logging
from typing import List, Dict, Any, Optional, Callable
from ..config import config
from ..database import db
from ..parsers import get_parser_for_language

logger = logging.getLogger("SyncEngine")

class SyncEngine:
    def __init__(self):
        self.db = db
        self._progress_callback: Optional[Callable] = None

    def set_progress_callback(self, callback: Optional[Callable]):
        """设置进度回调函数"""
        self._progress_callback = callback

    def _report_progress(self, current: int, total: int, message: str = ""):
        """报告进度"""
        if self._progress_callback:
            self._progress_callback(current, total, message)

    def get_language_by_extension(self, file_path: str) -> str:
        ext = os.path.splitext(file_path)[1].lower()
        return config.SUPPORTED_LANGUAGES.get(ext, None)

    def calculate_hash(self, file_path: str) -> str:
        """分块计算文件哈希，避免大文件内存问题"""
        try:
            logger.debug(f"[calculate_hash] 开始计算哈希: {file_path}")
            hash_md5 = hashlib.md5()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b""):  # 8KB 块大小
                    hash_md5.update(chunk)
            file_hash = hash_md5.hexdigest()
            logger.debug(f"[calculate_hash] 哈希计算完成: {file_hash}")
            return file_hash
        except Exception as e:
            logger.error(f"[calculate_hash] 计算文件哈希失败 {file_path}, error: {e}")
            return ""

    def sync_project(self, project_id: int) -> Dict[str, Any]:
        logger.info(f"[sync_project] ========================================")
        logger.info(f"[sync_project] 开始同步项目 project_id={project_id}")
        
        project = self.db.get_project(project_id)
        if not project:
            error_msg = "项目不存在"
            logger.error(f"[sync_project] {error_msg}, project_id={project_id}")
            return {
                'success': False, 
                'message': error_msg, 
                'files_processed': 0,
                'errors': 0,
                'warnings': 0
            }

        project_path = project['path']
        logger.info(f"[sync_project] 项目路径: {project_path}")
        
        if not os.path.exists(project_path):
            error_msg = "项目路径不存在"
            logger.error(f"[sync_project] {error_msg}: {project_path}")
            return {
                'success': False, 
                'message': error_msg, 
                'files_processed': 0,
                'errors': 0,
                'warnings': 0
            }

        logger.info(f"[sync_project] 开始扫描项目目录")
        files_to_process = []
        scan_errors = 0
        
        try:
            for root, dirs, files in os.walk(project_path):
                # 跳过常见的忽略目录
                skip_dirs = ['__pycache__', 'node_modules', '.git', '.idea', '__pycache__', 
                           'node_modules', '.git', 'coverage', 'dist', 'build', 'out']
                dirs[:] = [d for d in dirs if d not in skip_dirs]
                
                for file in files:
                    file_path = os.path.join(root, file)
                    language = self.get_language_by_extension(file_path)
                    
                    if language:
                        files_to_process.append({
                            'path': file_path,
                            'relative_path': os.path.relpath(file_path, project_path),
                            'language': language
                        })
        
        except Exception as e:
            logger.error(f"[sync_project] 扫描目录出错: {e}")
            scan_errors += 1
        
        logger.info(f"[sync_project] 扫描完成，发现 {len(files_to_process)} 个待处理文件")
        logger.info(f"[sync_project] ========================================")
        
        self._report_progress(0, len(files_to_process), f"开始同步，发现 {len(files_to_process)} 个文件")
        
        files_processed = 0
        files_error = 0
        files_skipped = 0
        
        for idx, file_info in enumerate(files_to_process):
            progress_pct = (idx + 1) / len(files_to_process) * 100
            logger.info(f"[sync_project] 进度: {progress_pct:.1f}% ({idx + 1}/{len(files_to_process)})")
            
            try:
                self._report_progress(idx + 1, len(files_to_process), 
                                      f"处理: {file_info['relative_path']}")
                
                logger.debug(f"[sync_project] 处理文件 [{idx + 1}/{len(files_to_process)}]: {file_info['relative_path']}")
                self._process_file(project_id, file_info['path'], file_info['language'])
                files_processed += 1
                
            except Exception as e:
                logger.error(f"[sync_project] 处理文件出错 {file_info['path']}: {e}", exc_info=True)
                files_error += 1
        
        try:
            self.db.update_project_time(project_id)
        except Exception as e:
            logger.warning(f"[sync_project] 更新项目时间失败: {e}")
        
        logger.info(f"[sync_project] ========================================")
        logger.info(f"[sync_project] 项目同步完成!")
        logger.info(f"[sync_project]   - 处理成功: {files_processed}")
        logger.info(f"[sync_project]   - 处理出错: {files_error}")
        logger.info(f"[sync_project]   - 跳过文件: {files_skipped}")
        logger.info(f"[sync_project] ========================================")
        
        self._report_progress(len(files_to_process), len(files_to_process), 
                              f"同步完成，处理 {files_processed} 个文件")
        
        return {
            'success': True,
            'message': f"同步完成，处理 {files_processed} 个文件",
            'files_processed': files_processed,
            'errors': files_error,
            'warnings': scan_errors
        }

    def _process_file(self, project_id: int, file_path: str, language: str):
        logger.debug(f"[_process_file] 开始处理: {file_path}")
        
        try:
            # 计算文件哈希
            logger.debug(f"[_process_file] 计算文件哈希: {file_path}")
            file_hash = self.calculate_hash(file_path)
            
            # 获取解析器
            logger.debug(f"[_process_file] 获取解析器: {language}")
            parser = get_parser_for_language(language)
            if not parser:
                logger.warning(f"[_process_file] 不支持的语言: {language}")
                return
            
            # 解析文件
            logger.debug(f"[_process_file] 开始解析文件: {file_path}")
            parse_result = parser.parse(file_path)
            
            logger.debug(f"[_process_file] 解析完成: {len(parse_result.types)} 个类型, {len(parse_result.functions)} 个函数")
            
            # 保存文件和解析结果
            file_id = self.db.get_or_create_file(project_id, file_path, language, file_hash)
            logger.debug(f"[_process_file] 文件已保存: file_id={file_id}")
            
            # 保存类型
            type_map = {}
            for type_info in parse_result.types:
                try:
                    type_id = self.db.insert_type(
                        file_id,
                        type_info['name'],
                        type_info['kind'],
                        type_info.get('line_start'),
                        type_info.get('line_end')
                    )
                    type_map[type_info['name']] = type_id
                except Exception as e:
                    logger.warning(f"[_process_file] 保存类型失败 {type_info['name']}: {e}")
            
            logger.debug(f"[_process_file] 保存了 {len(type_map)} 个类型")
            
            # 保存函数
            for func_info in parse_result.functions:
                try:
                    type_id = type_map.get(func_info['type_name']) if func_info.get('type_name') else None
                    func_id = self.db.insert_function(
                        file_id,
                        type_id,
                        func_info['name'],
                        func_info.get('line_start'),
                        func_info.get('line_end')
                    )
                except Exception as e:
                    logger.warning(f"[_process_file] 保存函数失败 {func_info['name']}: {e}")
            
            logger.debug(f"[_process_file] 保存了 {len(parse_result.functions)} 个函数")
            
        except Exception as e:
            logger.error(f"[_process_file] 处理文件失败: {file_path}, {e}", exc_info=True)
            raise

    def process_file_event(self, project_id: int, file_path: str, event_type: str):
        language = self.get_language_by_extension(file_path)
        
        if event_type == 'deleted' or event_type == 'modified':
            try:
                self.db.delete_file_by_path(project_id, file_path)
                logger.info(f"[process_file_event] 文件已删除: {file_path}")
            except Exception as e:
                logger.warning(f"[process_file_event] 删除文件失败: {e}")
        
        if event_type in ('created', 'modified') and language:
            try:
                self._process_file(project_id, file_path, language)
                logger.info(f"[process_file_event] 文件已处理: {file_path}")
                
                self.db.update_project_time(project_id)
            except Exception as e:
                logger.error(f"[process_file_event] 处理文件失败: {e}")

engine = SyncEngine()
