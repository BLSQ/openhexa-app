import io
import json
import logging
import os

import psycopg2
import psycopg2.extras

from hexa.databases.api import get_db_server_credentials
from hexa.files import storage
from hexa.workspaces.models import Workspace

logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 1_000_000  # 1 MB


def _validate_path(path: str) -> str | None:
    normalized = os.path.normpath(path)
    if os.path.isabs(normalized) or normalized.startswith(".."):
        return None
    return normalized


class WorkspaceFileSystemTools:
    def __init__(self, workspace: Workspace):
        self.workspace = workspace
        self.bucket_name = workspace.bucket_name

    def list_files(self, path: str = ""):
        if path and _validate_path(path) is None:
            return {"error": "Invalid path."}
        try:
            result = storage.list_bucket_objects(
                self.bucket_name,
                prefix=path or "",
                per_page=100,
            )
            files = []
            for item in result.items:
                files.append(
                    {
                        "name": item.name,
                        "path": str(item.key),
                        "type": item.type,
                        "size": item.size,
                        "updated_at": str(item.updated_at) if item.updated_at else None,
                    }
                )
            return {"files": files, "count": len(files)}
        except storage.exceptions.NotFound:
            return {"error": f"Path not found: {path}"}
        except Exception as e:
            logger.exception("Error listing files")
            return {"error": str(e)}

    def read_file(self, path: str):
        if _validate_path(path) is None:
            return {"error": "Invalid path."}
        try:
            obj = storage.get_bucket_object(self.bucket_name, path)
            if obj.type == "directory":
                return {"error": "Cannot read a directory. Use list_files instead."}
            if obj.size > MAX_FILE_SIZE:
                return {
                    "error": f"File too large ({obj.size} bytes). Maximum is {MAX_FILE_SIZE} bytes."
                }

            full_path = storage.path(self.bucket_name, path)
            with open(full_path, "r") as f:
                content = f.read()
            return {"content": content, "size": obj.size, "path": path}
        except storage.exceptions.NotFound:
            return {"error": f"File not found: {path}"}
        except UnicodeDecodeError:
            return {"error": "File is binary and cannot be read as text."}
        except Exception as e:
            logger.exception("Error reading file")
            return {"error": str(e)}

    def write_file(self, path: str, content: str):
        if _validate_path(path) is None:
            return {"error": "Invalid path."}
        try:
            file_bytes = content.encode("utf-8")
            storage.save_object(self.bucket_name, path, io.BytesIO(file_bytes))
            return {"success": True, "path": path, "size": len(file_bytes)}
        except Exception as e:
            logger.exception("Error writing file")
            return {"error": str(e)}

    def edit_file(self, path: str, old_string: str, new_string: str):
        if _validate_path(path) is None:
            return {"error": "Invalid path."}
        try:
            obj = storage.get_bucket_object(self.bucket_name, path)
            if obj.type == "directory":
                return {"error": "Cannot edit a directory."}
            if obj.size > MAX_FILE_SIZE:
                return {
                    "error": f"File too large ({obj.size} bytes). Maximum is {MAX_FILE_SIZE} bytes."
                }

            full_path = storage.path(self.bucket_name, path)
            with open(full_path, "r") as f:
                content = f.read()

            count = content.count(old_string)
            if count == 0:
                return {"error": "old_string not found in file."}
            if count > 1:
                return {
                    "error": f"old_string found {count} times. It must be unique. Provide more context to disambiguate."
                }

            new_content = content.replace(old_string, new_string, 1)
            file_bytes = new_content.encode("utf-8")
            storage.save_object(self.bucket_name, path, io.BytesIO(file_bytes))
            return {"success": True, "path": path, "size": len(file_bytes)}
        except storage.exceptions.NotFound:
            return {"error": f"File not found: {path}"}
        except UnicodeDecodeError:
            return {"error": "File is binary and cannot be edited as text."}
        except Exception as e:
            logger.exception("Error editing file")
            return {"error": str(e)}

    def search_files(self, pattern: str, path: str = ""):
        if path and _validate_path(path) is None:
            return {"error": "Invalid path."}
        try:
            result = storage.list_bucket_objects(
                self.bucket_name,
                prefix=path or "",
                match_glob=pattern,
                per_page=100,
            )
            files = []
            for item in result.items:
                files.append(
                    {
                        "name": item.name,
                        "path": str(item.key),
                        "type": item.type,
                        "size": item.size,
                    }
                )
            return {"files": files, "count": len(files), "pattern": pattern}
        except storage.exceptions.NotFound:
            return {"error": f"Path not found: {path}"}
        except Exception as e:
            logger.exception("Error searching files")
            return {"error": str(e)}


class WorkspaceDatabaseTools:
    def __init__(self, workspace: Workspace):
        self.workspace = workspace

    def _get_readonly_connection(self):
        credentials = get_db_server_credentials()
        host = credentials["host"]
        port = credentials["port"]
        conn = psycopg2.connect(
            host=host,
            port=port,
            dbname=self.workspace.db_name,
            user=f"{self.workspace.db_name}_ro",
            password=self.workspace.db_ro_password,
        )
        conn.set_session(readonly=True)
        return conn

    def query_database(self, query: str, limit: int = 100):
        limit = min(limit, 1000)
        query = query.strip().rstrip(";")
        limited_query = f"SELECT * FROM ({query}) AS _q LIMIT {limit}"

        conn = None
        try:
            conn = self._get_readonly_connection()
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                cursor.execute(limited_query)
                rows = cursor.fetchall()
                columns = (
                    [desc[0] for desc in cursor.description]
                    if cursor.description
                    else []
                )
            serializable_rows = [
                {k: _make_serializable(v) for k, v in row.items()} for row in rows
            ]
            return {
                "columns": columns,
                "rows": serializable_rows,
                "row_count": len(rows),
            }
        except psycopg2.Error as e:
            return {"error": str(e).strip()}
        except Exception as e:
            logger.exception("Error querying database")
            return {"error": str(e)}
        finally:
            if conn:
                conn.close()

    def describe_tables(self, table_name: str = None):
        conn = None
        try:
            conn = self._get_readonly_connection()
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                if table_name:
                    cursor.execute(
                        """
                        SELECT column_name AS name, data_type AS type, is_nullable
                        FROM information_schema.columns
                        WHERE table_name = %s AND table_schema = 'public'
                        ORDER BY ordinal_position;
                        """,
                        (table_name,),
                    )
                    columns = cursor.fetchall()
                    if not columns:
                        return {"error": f"Table not found: {table_name}"}
                    return {"table": table_name, "columns": [dict(c) for c in columns]}
                else:
                    cursor.execute(
                        """
                        SELECT table_name AS name
                        FROM information_schema.tables
                        WHERE table_schema = 'public'
                        ORDER BY table_name;
                        """
                    )
                    tables = cursor.fetchall()
                    return {"tables": [row["name"] for row in tables]}
        except Exception as e:
            logger.exception("Error describing tables")
            return {"error": str(e)}
        finally:
            if conn:
                conn.close()


def _make_serializable(value):
    if value is None:
        return value
    try:
        json.dumps(value)
        return value
    except (TypeError, ValueError):
        return str(value)
