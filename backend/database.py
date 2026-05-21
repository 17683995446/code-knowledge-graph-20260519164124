import sqlite3
import logging
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
from .config import config

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
        import time
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO projects (name, path, created_at, updated_at) VALUES (?, ?, ?, ?)",
                (name, path, int(time.time()), int(time.time()))
            )
            project_id = cursor.lastrowid
            logger.info(f"create_project: 项目创建成功 project_id={project_id}")
            return project_id

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
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
            row = cursor.fetchone()
            project = dict(row) if row else None
            if project:
                logger.debug(f"get_project: 获取到项目 {project['name']}")
            else:
                logger.warning(f"get_project: 项目不存在 project_id={project_id}")
            return project

    def delete_project(self, project_id: int):
        logger.info(f"delete_project: 开始删除项目 project_id={project_id}")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM files WHERE project_id = ?", (project_id,))
            file_ids = [row[0] for row in cursor.fetchall()]
            logger.info(f"delete_project: 将删除 {len(file_ids)} 个相关文件")

            for file_id in file_ids:
                cursor.execute("DELETE FROM calls WHERE caller_id = ? OR callee_id = ?", (file_id, file_id))
                cursor.execute("DELETE FROM refs WHERE from_id = ? OR to_id = ?", (file_id, file_id))
                cursor.execute("DELETE FROM functions WHERE file_id = ?", (file_id,))
                cursor.execute("DELETE FROM types WHERE file_id = ?", (file_id,))
                cursor.execute("DELETE FROM files WHERE id = ?", (file_id,))

            cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
            logger.info(f"delete_project: 项目删除完成 project_id={project_id}")

    def update_project_time(self, project_id: int):
        logger.debug(f"update_project_time: 更新项目时间 project_id={project_id}")
        import time
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE projects SET updated_at = ? WHERE id = ?", (int(time.time()), project_id))

    def get_or_create_file(self, project_id: int, path: str, language: str, hash: str) -> int:
        logger.debug(f"get_or_create_file: 处理文件 project_id={project_id}, path={path}, language={language}")
        import time
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO files (project_id, path, language, hash, modified) VALUES (?, ?, ?, ?, ?)",
                (project_id, path, language, hash, int(time.time()))
            )
            file_id = cursor.lastrowid
            logger.debug(f"get_or_create_file: 文件处理完成 file_id={file_id}")
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
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO types (file_id, name, kind, line_start, line_end) VALUES (?, ?, ?, ?, ?)",
                (file_id, name, kind, line_start, line_end)
            )
            return cursor.lastrowid

    def insert_function(self, file_id: int, type_id: Optional[int], name: str, line_start: int = None, line_end: int = None) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO functions (file_id, type_id, name, line_start, line_end) VALUES (?, ?, ?, ?, ?)",
                (file_id, type_id, name, line_start, line_end)
            )
            return cursor.lastrowid

    def insert_call(self, caller_id: int, caller_type: str, callee_id: int, callee_type: str):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR IGNORE INTO calls (caller_id, caller_type, callee_id, callee_type) VALUES (?, ?, ?, ?)",
                (caller_id, caller_type, callee_id, callee_type)
            )

    def insert_ref(self, from_id: int, from_type: str, to_id: int, to_type: str, kind: str):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR IGNORE INTO refs (from_id, from_type, to_id, to_type, kind) VALUES (?, ?, ?, ?, ?)",
                (from_id, from_type, to_id, to_type, kind)
            )

    def get_graph_data(self, project_id: int) -> Dict[str, Any]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT t.id, t.name, t.kind, f.id as file_id, f.path as file_path
                FROM types t
                JOIN files f ON t.file_id = f.id
                WHERE f.project_id = ?
            """, (project_id,))
            type_nodes = [dict(row) for row in cursor.fetchall()]

            cursor.execute("""
                SELECT DISTINCT f.id, f.name, f.type_id, f.file_id, ff.path as file_path
                FROM functions f
                JOIN files ff ON f.file_id = ff.id
                WHERE ff.project_id = ?
            """, (project_id,))
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
                               OR (c.callee_type = 'function' AND c.callee_id IN (SELECT id FROM functions WHERE file_id = f2.id))
                WHERE f1.project_id = ? AND f2.project_id = ?
            """, (project_id, project_id))
            calls = [dict(row) for row in cursor.fetchall()]

            cursor.execute("""
                SELECT r.from_id, r.from_type, r.to_id, r.to_type, r.kind
                FROM refs r
                JOIN files f1 ON (r.from_type = 'type' AND r.from_id IN (SELECT id FROM types WHERE file_id = f1.id))
                              OR (r.from_type = 'function' AND r.from_id IN (SELECT id FROM functions WHERE file_id = f1.id))
                JOIN files f2 ON (r.to_type = 'type' AND r.to_id IN (SELECT id FROM types WHERE file_id = f2.id))
                              OR (r.to_type = 'function' AND r.to_id IN (SELECT id FROM functions WHERE file_id = f2.id))
                WHERE f1.project_id = ? AND f2.project_id = ?
            """, (project_id, project_id))
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

            return {"nodes": nodes, "links": links}

    def search(self, project_id: int, query: str, type_filter: str = None) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            results = []

            if not type_filter or type_filter == "type":
                cursor.execute("""
                    SELECT t.id, t.name, t.kind, f.path as file_path, 'type' as entity_type
                    FROM types t
                    JOIN files f ON t.file_id = f.id
                    WHERE f.project_id = ? AND t.name LIKE ?
                """, (project_id, f"%{query}%"))
                results.extend([dict(row) for row in cursor.fetchall()])

            if not type_filter or type_filter == "function":
                cursor.execute("""
                    SELECT f.id, f.name, 'function' as kind, ff.path as file_path, 'function' as entity_type
                    FROM functions f
                    JOIN files ff ON f.file_id = ff.id
                    WHERE ff.project_id = ? AND f.name LIKE ?
                """, (project_id, f"%{query}%"))
                results.extend([dict(row) for row in cursor.fetchall()])

            return results

    def get_stats(self, project_id: int) -> Dict[str, Any]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM files WHERE project_id = ?", (project_id,))
            file_count = cursor.fetchone()[0]

            cursor.execute("""
                SELECT COUNT(*) FROM types t
                JOIN files f ON t.file_id = f.id
                WHERE f.project_id = ?
            """, (project_id,))
            type_count = cursor.fetchone()[0]

            cursor.execute("""
                SELECT COUNT(*) FROM functions f
                JOIN files ff ON f.file_id = ff.id
                WHERE ff.project_id = ?
            """, (project_id,))
            func_count = cursor.fetchone()[0]

            cursor.execute("""
                SELECT f.language, COUNT(*) as count FROM files f
                WHERE f.project_id = ?
                GROUP BY f.language
            """, (project_id,))
            languages = {row[0]: row[1] for row in cursor.fetchall()}

            return {
                "file_count": file_count,
                "type_count": type_count,
                "function_count": func_count,
                "languages": languages
            }

db = Database()
