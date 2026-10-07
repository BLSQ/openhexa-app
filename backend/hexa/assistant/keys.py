from enum import StrEnum


class AgentKey(StrEnum):
    """Identifies an agent."""

    GENERAL = "general"
    CREATE_PIPELINE = "create_pipeline"
    EDIT_PIPELINE = "edit_pipeline"
    CREATE_WEBAPP = "create_webapp"
    EDIT_WEBAPP = "edit_webapp"
    GENERATE_SQL = "generate_sql"
    NAMING = "naming"
