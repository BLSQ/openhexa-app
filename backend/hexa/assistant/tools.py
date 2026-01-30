def get_file_system_tools():
    return [
        {
            "name": "list_files",
            "description": "List files and directories in the workspace file system. Returns names, types (file/directory), sizes and modification dates.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Directory path relative to workspace root, e.g. 'data/raw'. Leave empty for root.",
                    }
                },
                "required": [],
            },
            "requires_approval": False,
        },
        {
            "name": "read_file",
            "description": "Read the contents of a text file from the workspace file system. Limited to 1MB files.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "File path relative to workspace root, e.g. 'data/report.csv'",
                    }
                },
                "required": ["path"],
            },
            "requires_approval": False,
        },
        {
            "name": "write_file",
            "description": "Create or overwrite a file in the workspace file system.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "File path relative to workspace root",
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write to the file",
                    },
                },
                "required": ["path", "content"],
            },
            "requires_approval": True,
        },
        {
            "name": "edit_file",
            "description": "Edit an existing file by replacing a specific string with new content. "
            "The old_string must match exactly (including whitespace and indentation). "
            "Use read_file first to see the current content, then specify the exact text to replace.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "File path relative to workspace root",
                    },
                    "old_string": {
                        "type": "string",
                        "description": "The exact text to find and replace. Must be unique within the file.",
                    },
                    "new_string": {
                        "type": "string",
                        "description": "The text to replace old_string with. Use empty string to delete.",
                    },
                },
                "required": ["path", "old_string", "new_string"],
            },
            "requires_approval": True,
        },
        {
            "name": "search_files",
            "description": "Search for files matching a glob pattern in the workspace file system.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Glob pattern like '*.csv' or '*.pdf'",
                    },
                    "path": {
                        "type": "string",
                        "description": "Directory to search in, relative to workspace root. Leave empty for root.",
                    },
                },
                "required": ["pattern"],
            },
            "requires_approval": False,
        },
    ]


def get_database_tools():
    return [
        {
            "name": "query_database",
            "description": "Execute a read-only SQL query on the workspace PostgreSQL database. Only SELECT queries are allowed.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "SQL SELECT query to execute",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of rows to return (default 100, max 1000)",
                    },
                },
                "required": ["query"],
            },
            "requires_approval": False,
        },
        {
            "name": "describe_tables",
            "description": "Get schema information for database tables. If table_name is omitted, lists all tables. If provided, returns column details for that table.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Specific table name to describe. Omit to list all tables.",
                    }
                },
                "required": [],
            },
            "requires_approval": False,
        },
    ]


def get_tools_requiring_approval() -> set[str]:
    all_tools = get_file_system_tools() + get_database_tools()
    return {t["name"] for t in all_tools if t.get("requires_approval", False)}


def get_tools_for_api() -> list[dict]:
    all_tools = get_file_system_tools() + get_database_tools()
    return [
        {k: v for k, v in tool.items() if k != "requires_approval"}
        for tool in all_tools
    ]
