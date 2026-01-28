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
        },
    ]
