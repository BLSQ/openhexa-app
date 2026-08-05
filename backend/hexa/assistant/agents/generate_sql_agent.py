import logging
import re

import psycopg2
import sqlparse
from asgiref.sync import sync_to_async
from pydantic_ai import ModelRetry
from pydantic_ai.output import TextOutput

from hexa.assistant.agents.base import BaseAgent
from hexa.assistant.instructions import InstructionSet
from hexa.databases.query_text import MultipleStatementsError
from hexa.databases.utils import (
    get_full_database_definition,
    validate_query,
)
from hexa.mcp.tools.databases import get_db_schema, get_db_table_schema

logger = logging.getLogger(__name__)

# Above this size, inlining the full schema costs more tokens than the LLM
# roundtrips it saves; fall back to table names and let the agent inspect
# individual tables through get_db_table_schema.
_SCHEMA_MAX_CHARS = 50_000

_READ_ONLY_FIRST_TOKENS = {"SELECT", "WITH"}


def _strip_markdown_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[^\n]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    return text.strip()


def _first_keyword(query: str) -> str | None:
    parsed = sqlparse.parse(query)
    if not parsed:
        return None
    token = parsed[0].token_first(skip_cm=True)
    return token.normalized.upper() if token is not None else None


def _render_schema(tables: list[dict]) -> str:
    lines = []
    for table in tables:
        columns = ", ".join(f"{c['name']} {c['type']}" for c in table["columns"])
        lines.append(f"{table['name']}({columns})")
    return "\n".join(lines)


class GenerateSqlAgent(BaseAgent):
    """Turns a natural-language request into a validated PostgreSQL query.

    The final answer is enforced to be a single read-only SQL statement: an
    output validator EXPLAINs it against the workspace database (read-only
    role) and raises ModelRetry with the database error so the model can
    correct itself.
    """

    instruction_set = InstructionSet.GENERATE_SQL
    # Schema-only tools: the agent inspects table/column metadata but is never
    # given access to the actual row data in the workspace database.
    tools = [get_db_schema, get_db_table_schema]
    max_requests = 6
    output_retries = 3

    def _output_type(self):
        return TextOutput(self._validate_sql)

    def _final_output(self, run_result) -> str | None:
        return run_result.output if run_result else None

    async def _validate_sql(self, text: str) -> str:
        query = _strip_markdown_fences(text)
        if _first_keyword(query) not in _READ_ONLY_FIRST_TOKENS:
            raise ModelRetry(
                "Your final answer must be a single read-only SQL statement "
                "(SELECT, or WITH ... SELECT). SQL comments (-- ...) are allowed, "
                "but no prose or markdown fences around the statement."
            )
        try:
            # thread_sensitive=False: plain psycopg2 connection to the workspace
            # database (no Django ORM), so it need not run on the main sync thread.
            await sync_to_async(validate_query, thread_sensitive=False)(
                self.conversation.workspace, query
            )
        except MultipleStatementsError as e:
            raise ModelRetry(str(e))
        except psycopg2.Error as e:
            raise ModelRetry(f"The database rejected the query: {str(e).strip()}")
        return query

    def _extra_instructions(self) -> str:
        try:
            tables = get_full_database_definition(self.conversation.workspace)
        except Exception:
            logger.exception("generate_sql_agent: failed to load database schema")
            return (
                "## Workspace database schema\n"
                "The schema could not be loaded. Use the `get_db_schema` tool to "
                "list the available tables and `get_db_table_schema` to inspect a "
                "table's columns."
            )
        if not tables:
            return (
                "## Workspace database schema\n"
                "The workspace database contains no tables."
            )
        schema = _render_schema(tables)
        if len(schema) > _SCHEMA_MAX_CHARS:
            names = "\n".join(f"- {table['name']}" for table in tables)
            return (
                "## Workspace database schema\n"
                "The schema is too large to show in full, so only table names are "
                "listed. Use the `get_db_table_schema` tool to inspect the columns "
                "of the tables you need.\n" + names
            )
        return (
            "## Workspace database schema\n"
            "Each line is `table(column type, ...)`.\n" + schema
        )
