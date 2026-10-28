import psycopg2
from django.core.exceptions import PermissionDenied

from hexa.assistant.agents.base import BaseAgent
from hexa.assistant.agents.generate_sql_agent import (
    _READ_ONLY_FIRST_TOKENS,
    _first_keyword,
    _strip_markdown_fences,
    render_database_schema,
)
from hexa.assistant.instructions import InstructionSet
from hexa.assistant.keys import AgentKey
from hexa.data_studio.models import SavedQuery
from hexa.databases.query_text import MultipleStatementsError
from hexa.databases.utils import validate_query
from hexa.git.exceptions import GitError
from hexa.mcp.tools.databases import get_db_schema, get_db_table_schema
from hexa.mcp.tools.saved_queries import get_saved_query, list_saved_queries
from hexa.user_management.models import User


def save_saved_query_version(saved_query: SavedQuery, user: User, content: str) -> dict:
    """Save the SQL as a new version of the saved query the user is editing.

    content is the complete statement: a single read-only SQL statement (SELECT, or
    WITH ... SELECT), without markdown fences; SQL comments are fine. It is checked
    against the workspace database first, and a rejected statement comes back as an
    error to fix rather than being saved. On success the user sees the new version
    in their editor right away, so do not repeat the SQL in your reply.
    """
    query = _strip_markdown_fences(content)
    if _first_keyword(query) not in _READ_ONLY_FIRST_TOKENS:
        return {
            "error": (
                "content must be a single read-only SQL statement (SELECT, or "
                "WITH ... SELECT), without prose or markdown fences around it."
            )
        }
    try:
        validate_query(saved_query.workspace, query)
    except MultipleStatementsError as e:
        return {"error": str(e)}
    except psycopg2.Error as e:
        return {"error": f"The database rejected the query: {str(e).strip()}"}

    try:
        saved_query.update_if_has_perm(principal=user, content=query)
    except PermissionDenied:
        return {"error": "The user is not allowed to edit this saved query."}
    except GitError:
        return {
            "error": (
                "The new version could not be recorded, so nothing was saved. "
                "Call the tool again."
            )
        }
    return {
        "slug": saved_query.slug,
        "name": saved_query.name,
        "content": saved_query.content,
    }


class EditSavedQueryAgent(BaseAgent):
    """Iterates on a saved query with the user, saving each change as a version.

    Unlike the pipeline and web app edit agents it proposes nothing: a saved query
    is one SQL statement that the editor shows right away, so the tool validates
    the statement (EXPLAIN under the read-only role) and commits it directly.
    """

    instruction_set = InstructionSet.EDIT_SAVED_QUERY
    agent_key = AgentKey.EDIT_SAVED_QUERY
    # Schema-only tools: the agent never reads the rows of the workspace database.
    tools = [
        get_db_schema,
        get_db_table_schema,
        list_saved_queries,
        get_saved_query,
        save_saved_query_version,
    ]
    max_requests = 10

    @property
    def _context(self) -> dict:
        return {**super()._context, "saved_query": self.conversation.linked_object}

    def _extra_instructions(self) -> str:
        saved_query = self.conversation.linked_object
        if saved_query is None:
            return ""
        if not isinstance(saved_query, SavedQuery):
            raise TypeError(
                "EditSavedQueryAgent requires a SavedQuery linked object, got "
                f"{type(saved_query).__name__}"
            )
        lines = [
            "## Current saved query",
            f"Name: {saved_query.name}",
            f"Slug: {saved_query.slug}",
        ]
        if saved_query.description:
            lines.append(f"Description: {saved_query.description}")
        lines.append("")
        if saved_query.content.strip():
            lines.append("### SQL\n```sql\n" + saved_query.content + "\n```")
        else:
            lines.append("### SQL\nThe query is still empty.")
        return "\n".join(lines) + "\n\n" + render_database_schema(saved_query.workspace)
