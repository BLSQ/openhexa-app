from typing import Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from mcp.server.fastmcp import FastMCP
import sys
import logging
import os
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file in the same directory
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('postgres-mcp-server')

# Initialize server
mcp = FastMCP("PostgreSQL Explorer")

# Connection string from --conn flag or POSTGRES_CONNECTION_STRING env var
parser = argparse.ArgumentParser(description="PostgreSQL Explorer MCP server")
parser.add_argument(
    "--conn",
    dest="conn",
    default=os.getenv("POSTGRES_CONNECTION_STRING"),
    help="PostgreSQL connection string or DSN"
)
args, _ = parser.parse_known_args()
CONNECTION_STRING: Optional[str] = args.conn

def mask_conn_string(conn_str):
    if not conn_str:
        return None
    # Try to mask user:password@host:port/db
    try:
        if '@' in conn_str:
            userinfo, rest = conn_str.split('@', 1)
            if ':' in userinfo:
                user, _ = userinfo.split(':', 1)
                return f"{user}:***@{rest[:4]}...{rest[-4:]}"
            else:
                return f"***@{rest[:4]}...{rest[-4:]}"
        return '***'
    except Exception:
        return '***'

logger.info(
    "Starting PostgreSQL MCP server – connection %s",
    mask_conn_string(CONNECTION_STRING)
)

def get_connection():
    if not CONNECTION_STRING:
        raise RuntimeError(
            "POSTGRES_CONNECTION_STRING is not set. Provide --conn DSN or export POSTGRES_CONNECTION_STRING."
        )
    try:
        conn = psycopg2.connect(CONNECTION_STRING)
        logger.debug("Database connection established successfully")
        return conn
    except Exception as e:
        logger.error(f"Failed to establish database connection: {str(e)}")
        raise

@mcp.tool()
def query(sql: str, parameters: Optional[list] = None) -> str:
    """Execute a SQL query against the PostgreSQL database."""
    conn = None
    try:
        try:
            conn = get_connection()
        except RuntimeError as e:
            return str(e)
        logger.info(f"Executing query: {sql[:100]}{'...' if len(sql) > 100 else ''}")
        
        # Use RealDictCursor for better handling of special characters in column names
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            try:
                # Properly escape the query using mogrify
                if parameters:
                    query_string = cur.mogrify(sql, parameters).decode('utf-8')
                    logger.debug(f"Query with parameters: {query_string}")
                else:
                    query_string = sql
                
                # Execute the escaped query
                cur.execute(query_string)
                
                # For non-SELECT queries
                if cur.description is None:
                    conn.commit()
                    affected_rows = cur.rowcount
                    logger.info(f"Non-SELECT query executed successfully. Rows affected: {affected_rows}")
                    return f"Query executed successfully. Rows affected: {affected_rows}"
                
                # For SELECT queries
                rows = cur.fetchall()
                if not rows:
                    logger.info("Query returned no results")
                    return "No results found"
                
                logger.info(f"Query returned {len(rows)} rows")

                # Limit rows to prevent token overflow (max 50 rows)
                max_rows = 50
                rows_to_display = rows[:max_rows]
                truncated = len(rows) > max_rows

                # Format results with proper string escaping
                result_lines = ["Results:", "--------"]
                for row in rows_to_display:
                    try:
                        # Convert each value to string safely
                        line_items = []
                        for key, val in row.items():
                            if val is None:
                                formatted_val = "NULL"
                            elif isinstance(val, (bytes, bytearray)):
                                formatted_val = val.decode('utf-8', errors='replace')
                            else:
                                formatted_val = str(val).replace('%', '%%')
                            line_items.append(f"{key}: {formatted_val}")
                        result_lines.append(" | ".join(line_items))
                    except Exception as row_error:
                        error_msg = f"Error formatting row: {str(row_error)}"
                        logger.error(error_msg)
                        result_lines.append(error_msg)
                        continue

                # Add truncation notice if applicable
                if truncated:
                    result_lines.append(f"... (showing {max_rows} of {len(rows)} rows)")

                return "\n".join(result_lines)
                
            except Exception as exec_error:
                error_msg = f"Query error: {str(exec_error)}\nQuery: {sql}"
                logger.error(error_msg)
                return error_msg
    except Exception as conn_error:
        error_msg = f"Connection error: {str(conn_error)}"
        logger.error(error_msg)
        return error_msg
    finally:
        if conn:
            conn.close()
            logger.debug("Database connection closed")

@mcp.tool()
def list_schemas() -> str:
    """List all schemas in the database."""
    logger.info("Listing database schemas")
    return query("SELECT schema_name FROM information_schema.schemata ORDER BY schema_name")

@mcp.tool()
def list_tables(db_schema: str = 'public') -> str:
    """List all tables in a specific schema.
    
    Args:
        db_schema: The schema name to list tables from (defaults to 'public')
    """
    logger.info(f"Listing tables in schema: {db_schema}")
    sql = """
    SELECT table_name, table_type
    FROM information_schema.tables
    WHERE table_schema = %s
    ORDER BY table_name
    """
    return query(sql, [db_schema])

@mcp.tool()
def describe_table(table_name: str, db_schema: str = 'public') -> str:
    """Get detailed information about a table.
    
    Args:
        table_name: The name of the table to describe
        db_schema: The schema name (defaults to 'public')
    """
    logger.info(f"Describing table: {db_schema}.{table_name}")
    sql = """
    SELECT 
        column_name,
        data_type,
        is_nullable,
        column_default,
        character_maximum_length
    FROM information_schema.columns
    WHERE table_schema = %s AND table_name = %s
    ORDER BY ordinal_position
    """
    return query(sql, [db_schema, table_name])

@mcp.tool()
def get_foreign_keys(table_name: str, db_schema: str = 'public') -> str:
    """Get foreign key information for a table.
    
    Args:
        table_name: The name of the table to get foreign keys from
        db_schema: The schema name (defaults to 'public')
    """
    logger.info(f"Getting foreign keys for table: {db_schema}.{table_name}")
    sql = """
    SELECT 
        tc.constraint_name,
        kcu.column_name as fk_column,
        ccu.table_schema as referenced_schema,
        ccu.table_name as referenced_table,
        ccu.column_name as referenced_column
    FROM information_schema.table_constraints tc
    JOIN information_schema.key_column_usage kcu
        ON tc.constraint_name = kcu.constraint_name
        AND tc.table_schema = kcu.table_schema
    JOIN information_schema.referential_constraints rc
        ON tc.constraint_name = rc.constraint_name
    JOIN information_schema.constraint_column_usage ccu
        ON rc.unique_constraint_name = ccu.constraint_name
    WHERE tc.constraint_type = 'FOREIGN KEY'
        AND tc.table_schema = %s
        AND tc.table_name = %s
    ORDER BY tc.constraint_name, kcu.ordinal_position
    """
    return query(sql, [db_schema, table_name])

@mcp.tool()
def find_relationships(table_name: str, db_schema: str = 'public') -> str:
    """Find both explicit and implied relationships for a table.
    
    Args:
        table_name: The name of the table to analyze relationships for
        db_schema: The schema name (defaults to 'public')
    """
    logger.info(f"Finding relationships for table: {db_schema}.{table_name}")
    try:
        # First get explicit foreign key relationships
        fk_sql = """
        SELECT 
            kcu.column_name,
            ccu.table_name as foreign_table,
            ccu.column_name as foreign_column,
            'Explicit FK' as relationship_type,
            1 as confidence_level
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu 
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
        JOIN information_schema.constraint_column_usage ccu
            ON ccu.constraint_name = tc.constraint_name
            AND ccu.table_schema = tc.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_schema = %s
            AND tc.table_name = %s
        """
        
        logger.debug("Querying explicit foreign key relationships")
        explicit_results = query(fk_sql, [db_schema, table_name])
        
        # Then look for implied relationships based on common patterns
        logger.debug("Querying implied relationships")
        implied_sql = """
        WITH source_columns AS (
            -- Get all ID-like columns from our table
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = %s 
            AND table_name = %s
            AND (
                column_name LIKE '%%id' 
                OR column_name LIKE '%%_id'
                OR column_name LIKE '%%_fk'
            )
        ),
        potential_references AS (
            -- Find tables that might be referenced by our ID columns
            SELECT DISTINCT
                sc.column_name as source_column,
                sc.data_type as source_type,
                t.table_name as target_table,
                c.column_name as target_column,
                c.data_type as target_type,
                CASE
                    -- Highest confidence: column matches table_id pattern and types match
                    WHEN sc.column_name = t.table_name || '_id' 
                        AND sc.data_type = c.data_type THEN 2
                    -- High confidence: column ends with _id and types match
                    WHEN sc.column_name LIKE '%%_id' 
                        AND sc.data_type = c.data_type THEN 3
                    -- Medium confidence: column contains table name and types match
                    WHEN sc.column_name LIKE '%%' || t.table_name || '%%'
                        AND sc.data_type = c.data_type THEN 4
                    -- Lower confidence: column ends with id and types match
                    WHEN sc.column_name LIKE '%%id'
                        AND sc.data_type = c.data_type THEN 5
                END as confidence_level
            FROM source_columns sc
            CROSS JOIN information_schema.tables t
            JOIN information_schema.columns c 
                ON c.table_schema = t.table_schema 
                AND c.table_name = t.table_name
                AND (c.column_name = 'id' OR c.column_name = sc.column_name)
            WHERE t.table_schema = %s
                AND t.table_name != %s  -- Exclude self-references
        )
        SELECT 
            source_column as column_name,
            target_table as foreign_table,
            target_column as foreign_column,
            CASE 
                WHEN confidence_level = 2 THEN 'Strong implied relationship (exact match)'
                WHEN confidence_level = 3 THEN 'Strong implied relationship (_id pattern)'
                WHEN confidence_level = 4 THEN 'Likely implied relationship (name match)'
                ELSE 'Possible implied relationship'
            END as relationship_type,
            confidence_level
        FROM potential_references
        WHERE confidence_level IS NOT NULL
        ORDER BY confidence_level, source_column;
        """
        implied_results = query(implied_sql, [db_schema, table_name])
        
        return "Explicit Relationships:\n" + explicit_results + "\n\nImplied Relationships:\n" + implied_results
        
    except Exception as e:
        error_msg = f"Error finding relationships: {str(e)}"
        logger.error(error_msg)
        return error_msg

if __name__ == "__main__":
    try:
        logger.info("Starting MCP Postgres server...")
        mcp.run()
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        sys.exit(1)