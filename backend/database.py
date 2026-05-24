import sqlite3
import logging
import os
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
from .config import config
from .validators import (
    validate_project_name,
    validate_project_path,
    validate_project_id,
    validate_search_query,
    validate_integer,
    validate_file_path,
    safe_like_pattern,
    ValidationError
)

logger = logging.getLogger("Database")

class Database:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or config.DATABASE_PATH
        self.init_db()

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executescript("""
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    path TEXT UNIQUE NOT NULL,
                    created_at INTEGER NOT NULL,
                    updated_at INTEGER NOT NULL
                );

                CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER NOT NULL,
                    path TEXT NOT NULL,
                    language TEXT NOT NULL,
                    hash TEXT NOT NULL,
                    modified INTEGER NOT NULL,
                    FOREIGN KEY (project_id) REFERENCES projects(id),
                    UNIQUE(project_id, path)
                );

                CREATE TABLE IF NOT EXISTS types (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    line_start INTEGER,
                    line_end INTEGER,
                    FOREIGN KEY (file_id) REFERENCES files(id),
                    UNIQUE(file_id, name, kind)
                );

                CREATE TABLE IF NOT EXISTS functions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_id INTEGER NOT NULL,
                    type_id INTEGER,
                    name TEXT NOT NULL,
                    line_start INTEGER,
                    line_end INTEGER,
                    FOREIGN KEY (file_id) REFERENCES files(id),
                    FOREIGN KEY (type_id) REFERENCES types(id),
                    UNIQUE(file_id, type_id, name)
                );

                CREATE TABLE IF NOT EXISTS calls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    caller_id INTEGER NOT NULL,
                    caller_type TEXT NOT NULL,
                    callee_id INTEGER NOT NULL,
                    callee_type TEXT NOT NULL,
                    FOREIGN KEY (caller_id) REFERENCES types(id),
                    FOREIGN KEY (callee_id) REFERENCES types(id)
                );

                CREATE TABLE IF NOT EXISTS refs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    from_id INTEGER NOT NULL,
                    from_type TEXT NOT NULL,
                    to_id INTEGER NOT NULL,
                    to_type TEXT NOT NULL,
                    kind TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_files_project ON files(project_id);
                CREATE INDEX IF NOT EXISTS idx_types_file ON types(file_id);
                CREATE INDEX IF NOT EXISTS idx_functions_file ON functions(file_id);
                CREATE INDEX IF NOT EXISTS idx_functions_type ON functions(type_id);
                CREATE INDEX IF NOT EXISTS idx_calls_caller ON calls(caller_id);
                CREATE INDEX IF NOT EXISTS idx_calls_callee ON calls(callee_id);
            """)

    def create_project(self, name: str, path: str) -> int:
        logger.info(f"create_project: 开始创建项目 name={name}, path={path}")
        
        try:
            # 使用验证器进行参数验证
            clean_name = validate_project_name(name)
            clean_path = validate_project_path(path)
            
            import time
            with self.get_connection() as conn:
                cursor = conn.cursor()
                try:
                    cursor.execute(
                        "INSERT INTO projects (name, path, created_at, updated_at) VALUES (?, ?, ?, ?)",
                        (clean_name, clean_path, int(time.time()), int(time.time()))
                    )
                    project_id = cursor.lastrowid
                    logger.info(f"create_project: 项目创建成功 project_id={project_id}")
                    return project_id
                except sqlite3.IntegrityError as e:
                    error_msg = f"项目路径已存在: {path}"
                    logger.error(f"create_project: {error_msg}, error: {e}")
                    raise ValueError(error_msg)
                    
        except ValidationError as e:
            logger.error(f"create_project: 验证失败 - {e}")
            raise ValueError(str(e))

    def get_projects(self) -> List[Dict[str, Any]]:
        logger.debug("get_projects: 开始获取项目列表")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM projects ORDER BY updated_at DESC")
            projects = [dict(row) for row in cursor.fetchall()]
            logger.debug(f"get_projects: 获取到 {len(projects)} 个项目")
            return projects

    def get_project(self, project_id: int) -> Optional[Dict[str, Any]]:
        logger.debug(f"get_project: 开始获取项目 project_id={project_id}")
        try:
            valid_project_id = validate_project_id(project_id)
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM projects WHERE id = ?", (valid_project_id,))
                row = cursor.fetchone()
                project = dict(row) if row else None
                if project:
                    logger.debug(f"get_project: 获取到项目 {project['name']}")
                else:
                    logger.warning(f"get_project: 项目不存在 project_id={valid_project_id}")
                return project
        except ValidationError as e:
            logger.error(f"get_project: 验证失败 - {e}")
            raise ValueError(str(e))

    def delete_project(self, project_id: int):
        logger.info(f"delete_project: 开始删除项目 project_id={project_id}")
        try:
            valid_project_id = validate_project_id(project_id)
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM files WHERE project_id = ?", (valid_project_id,))
                file_ids = [row[0] for row in cursor.fetchall()]
                logger.info(f"delete_project: 将删除 {len(file_ids)} 个相关文件")

                for file_id in file_ids:
                    cursor.execute("DELETE FROM calls WHERE caller_id = ? OR callee_id = ?", (file_id, file_id))
                    cursor.execute("DELETE FROM refs WHERE from_id = ? OR to_id = ?", (file_id, file_id))
                    cursor.execute("DELETE FROM functions WHERE file_id = ?", (file_id,))
                    cursor.execute("DELETE FROM types WHERE file_id = ?", (file_id,))
                    cursor.execute("DELETE FROM files WHERE id = ?", (file_id,))

                cursor.execute("DELETE FROM projects WHERE id = ?", (valid_project_id,))
                logger.info(f"delete_project: 项目删除完成 project_id={valid_project_id}")
        except ValidationError as e:
            logger.error(f"delete_project: 验证失败 - {e}")
            raise ValueError(str(e))

    def update_project_time(self, project_id: int):
        logger.debug(f"update_project_time: 更新项目时间 project_id={project_id}")
        try:
            valid_project_id = validate_project_id(project_id)
            import time
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE projects SET updated_at = ? WHERE id = ?", (int(time.time()), valid_project_id))
        except ValidationError as e:
            logger.error(f"update_project_time: 验证失败 - {e}")
            raise ValueError(str(e))

    def get_or_create_file(self, project_id: int, path: str, language: str, hash: str) -> int:
        logger.debug(f"get_or_create_file: 处理文件 project_id={project_id}, path={path}, language={language}")
        import time
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # 检查是否已存在
            cursor.execute("SELECT id FROM files WHERE project_id = ? AND path = ?", (project_id, path))
            row = cursor.fetchone()
            if row:
                # 更新文件
                cursor.execute(
                    "UPDATE files SET hash = ?, modified = ?, language = ? WHERE project_id = ? AND path = ?",
                    (hash, int(time.time()), language, project_id, path)
                )
                file_id = row[0]
                logger.debug(f"get_or_create_file: 文件已存在，更新完成 file_id={file_id}")
            else:
                # 插入新文件
                cursor.execute(
                    "INSERT INTO files (project_id, path, language, hash, modified) VALUES (?, ?, ?, ?, ?)",
                    (project_id, path, language, hash, int(time.time()))
                )
                file_id = cursor.lastrowid
                logger.debug(f"get_or_create_file: 文件已保存 file_id={file_id}")
            return file_id

    def delete_file_by_path(self, project_id: int, path: str):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM files WHERE project_id = ? AND path = ?", (project_id, path))
            row = cursor.fetchone()
            if row:
                file_id = row[0]
                cursor.execute("DELETE FROM calls WHERE caller_id = ? OR callee_id = ?", (file_id, file_id))
                cursor.execute("DELETE FROM refs WHERE from_id = ? OR to_id = ?", (file_id, file_id))
                cursor.execute("DELETE FROM functions WHERE file_id = ?", (file_id,))
                cursor.execute("DELETE FROM types WHERE file_id = ?", (file_id,))
                cursor.execute("DELETE FROM files WHERE id = ?", (file_id,))

    def insert_type(self, file_id: int, name: str, kind: str, line_start: int = None, line_end: int = None) -> int:
        logger.debug(f"insert_type: 插入类型 file_id={file_id}, name={name}, kind={kind}")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # 检查是否已存在
            cursor.execute(
                "SELECT id FROM types WHERE file_id = ? AND name = ? AND kind = ?",
                (file_id, name, kind)
            )
            row = cursor.fetchone()
            if row:
                # 更新
                cursor.execute(
                    "UPDATE types SET line_start = ?, line_end = ? WHERE id = ?",
                    (line_start, line_end, row[0])
                )
                type_id = row[0]
                logger.debug(f"insert_type: 类型已存在，已更新 type_id={type_id}")
            else:
                # 插入新记录
                cursor.execute(
                    "INSERT INTO types (file_id, name, kind, line_start, line_end) VALUES (?, ?, ?, ?, ?)",
                    (file_id, name, kind, line_start, line_end)
                )
                type_id = cursor.lastrowid
                logger.debug(f"insert_type: 类型已插入 type_id={type_id}")
            return type_id

    def insert_function(self, file_id: int, type_id: Optional[int], name: str, line_start: int = None, line_end: int = None) -> int:
        logger.debug(f"insert_function: 插入函数 file_id={file_id}, type_id={type_id}, name={name}")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # 检查是否已存在
            cursor.execute(
                "SELECT id FROM functions WHERE file_id = ? AND type_id IS ? AND name = ?",
                (file_id, type_id, name)
            )
            row = cursor.fetchone()
            if row:
                # 更新
                cursor.execute(
                    "UPDATE functions SET line_start = ?, line_end = ? WHERE id = ?",
                    (line_start, line_end, row[0])
                )
                func_id = row[0]
                logger.debug(f"insert_function: 函数已存在，已更新 func_id={func_id}")
            else:
                # 插入新记录
                cursor.execute(
                    "INSERT INTO functions (file_id, type_id, name, line_start, line_end) VALUES (?, ?, ?, ?, ?)",
                    (file_id, type_id, name, line_start, line_end)
                )
                func_id = cursor.lastrowid
                logger.debug(f"insert_function: 函数已插入 func_id={func_id}")
            return func_id

    def insert_call(self, caller_id: int, caller_type: str, callee_id: int, callee_type: str):
        logger.debug(f"insert_call: 插入调用关系 caller_id={caller_id}, callee_id={callee_id}")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR IGNORE INTO calls (caller_id, caller_type, callee_id, callee_type) VALUES (?, ?, ?, ?)",
                (caller_id, caller_type, callee_id, callee_type)
            )

    def insert_ref(self, from_id: int, from_type: str, to_id: int, to_type: str, kind: str):
        logger.debug(f"insert_ref: 插入引用关系 from_id={from_id}, to_id={to_id}")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR IGNORE INTO refs (from_id, from_type, to_id, to_type, kind) VALUES (?, ?, ?, ?, ?)",
                (from_id, from_type, to_id, to_type, kind)
            )

    def get_graph_data(self, project_id: int) -> Dict[str, Any]:
        logger.debug(f"get_graph_data: 获取图谱数据 project_id={project_id}")
        try:
            valid_project_id = validate_project_id(project_id)
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT DISTINCT t.id, t.name, t.kind, f.id as file_id, f.path as file_path
                    FROM types t
                    JOIN files f ON t.file_id = f.id
                    WHERE f.project_id = ?
                """, (valid_project_id,))
                type_nodes = [dict(row) for row in cursor.fetchall()]

                cursor.execute("""
                    SELECT DISTINCT f.id, f.name, f.type_id, f.file_id, ff.path as file_path
                    FROM functions f
                    JOIN files ff ON f.file_id = ff.id
                    WHERE ff.project_id = ?
                """, (valid_project_id,))
                func_nodes = [dict(row) for row in cursor.fetchall()]

                nodes = []
                for t in type_nodes:
                    nodes.append({
                        "id": f"type_{t['id']}",
                        "name": t['name'],
                        "type": "type",
                        "kind": t['kind'],
                        "file_id": t['file_id'],
                        "file_path": t['file_path']
                    })

                for f in func_nodes:
                    nodes.append({
                        "id": f"func_{f['id']}",
                        "name": f['name'],
                        "type": "function",
                        "kind": "function",
                        "file_id": f['file_id'],
                        "file_path": f['file_path'],
                        "type_id": f['type_id']
                    })

                cursor.execute("""
                    SELECT c.caller_id, c.caller_type, c.callee_id, c.callee_type
                    FROM calls c
                    JOIN files f1 ON (c.caller_type = 'type' AND c.caller_id IN (SELECT id FROM types WHERE file_id = f1.id))
                                   OR (c.caller_type = 'function' AND c.caller_id IN (SELECT id FROM functions WHERE file_id = f1.id))
                    JOIN files f2 ON (c.callee_type = 'type' AND c.callee_id IN (SELECT id FROM types WHERE file_id = f2.id))
                                   OR (c.callee_type = 'function' AND c.callee_id IN (SELECT id FROM types WHERE file_id = f2.id))
                    WHERE f1.project_id = ? AND f2.project_id = ?
                """, (valid_project_id, valid_project_id))
                calls = [dict(row) for row in cursor.fetchall()]

                cursor.execute("""
                    SELECT r.from_id, r.from_type, r.to_id, r.to_type, r.kind
                    FROM refs r
                    JOIN files f1 ON (r.from_type = 'type' AND r.from_id IN (SELECT id FROM types WHERE file_id = f1.id))
                                  OR (r.from_type = 'function' AND r.from_id IN (SELECT id FROM functions WHERE file_id = f1.id))
                    JOIN files f2 ON (r.to_type = 'type' AND r.to_id IN (SELECT id FROM types WHERE file_id = f2.id))
                                  OR (r.to_type = 'function' AND r.to_id IN (SELECT id FROM functions WHERE file_id = f2.id))
                    WHERE f1.project_id = ? AND f2.project_id = ?
                """, (valid_project_id, valid_project_id))
                refs = [dict(row) for row in cursor.fetchall()]

                links = []
                for c in calls:
                    links.append({
                        "source": f"{c['caller_type']}_{c['caller_id']}",
                        "target": f"{c['callee_type']}_{c['callee_id']}",
                        "relation": "call"
                    })

                for r in refs:
                    links.append({
                        "source": f"{r['from_type']}_{r['from_id']}",
                        "target": f"{r['to_type']}_{r['to_id']}",
                        "relation": r['kind']
                    })

                logger.debug(f"get_graph_data: 构建完成，{len(nodes)} 个节点，{len(links)} 个关系")
                return {"nodes": nodes, "links": links}
        except ValidationError as e:
            logger.error(f"get_graph_data: 验证失败 - {e}")
            raise ValueError(str(e))

    def search(self, project_id: int, query: str, type_filter: str = None) -> List[Dict[str, Any]]:
        logger.debug(f"search: 开始搜索 project_id={project_id}, query={query}")
        try:
            valid_project_id = validate_project_id(project_id)
            clean_query = validate_search_query(query)
            
            with self.get_connection() as conn:
                cursor = conn.cursor()
                results = []

                if not type_filter or type_filter == "type":
                    cursor.execute("""
                        SELECT t.id, t.name, t.kind, f.path as file_path, 'type' as entity_type
                        FROM types t
                        JOIN files f ON t.file_id = f.id
                        WHERE f.project_id = ? AND t.name LIKE ?
                    """, (valid_project_id, f"%{clean_query}%"))
                    results.extend([dict(row) for row in cursor.fetchall()])

                if not type_filter or type_filter == "function":
                    cursor.execute("""
                        SELECT f.id, f.name, 'function' as kind, ff.path as file_path, 'function' as entity_type
                        FROM functions f
                        JOIN files ff ON f.file_id = ff.id
                        WHERE ff.project_id = ? AND f.name LIKE ?
                    """, (valid_project_id, f"%{clean_query}%"))
                    results.extend([dict(row) for row in cursor.fetchall()])

                logger.debug(f"search: 搜索完成，找到 {len(results)} 个结果")
                return results
        except ValidationError as e:
            logger.error(f"search: 验证失败 - {e}")
            raise ValueError(str(e))

    def get_stats(self, project_id: int) -> Dict[str, Any]:
        logger.debug(f"get_stats: 获取统计信息 project_id={project_id}")
        try:
            valid_project_id = validate_project_id(project_id)
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM files WHERE project_id = ?", (valid_project_id,))
                file_count = cursor.fetchone()[0]

                cursor.execute("""
                    SELECT COUNT(*) FROM types t
                    JOIN files f ON t.file_id = f.id
                    WHERE f.project_id = ?
                """, (valid_project_id,))
                type_count = cursor.fetchone()[0]

                cursor.execute("""
                    SELECT COUNT(*) FROM functions f
                    JOIN files ff ON f.file_id = ff.id
                    WHERE ff.project_id = ?
                """, (valid_project_id,))
                func_count = cursor.fetchone()[0]

                cursor.execute("""
                    SELECT f.language, COUNT(*) as count FROM files f
                    WHERE f.project_id = ?
                    GROUP BY f.language
                """, (valid_project_id,))
                languages = {row[0]: row[1] for row in cursor.fetchall()}

                stats = {
                    "file_count": file_count,
                    "type_count": type_count,
                    "function_count": func_count,
                    "languages": languages
                }
                logger.debug(f"get_stats: 统计完成 {stats}")
                return stats
        except ValidationError as e:
            logger.error(f"get_stats: 验证失败 - {e}")
            raise ValueError(str(e))

db = Database()
