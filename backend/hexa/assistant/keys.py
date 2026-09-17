from enum import StrEnum


class AgentKey(StrEnum):
    """Identifies an agent (e.g.: used in ASSISTANT_AGENT_MODELS env var)"""

    GENERAL = "general"
    CREATE_PIPELINE = "create_pipeline"
    EDIT_PIPELINE = "edit_pipeline"
    EDIT_WEBAPP = "edit_webapp"
    GENERATE_SQL = "generate_sql"
    NAMING = "naming"
