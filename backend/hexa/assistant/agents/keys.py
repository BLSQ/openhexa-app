from django.db.models import TextChoices


class AgentKey(TextChoices):
    """Identifies an agent in ASSISTANT_AGENT_MODELS.

    Kept apart from the agent classes so the setting can be validated without
    importing them, and apart from InstructionSet so renaming a prompt set never
    silently changes what a deployed environment variable means.
    """

    GENERAL = "general", "General"
    CREATE_PIPELINE = "create_pipeline", "Create Pipeline"
    EDIT_PIPELINE = "edit_pipeline", "Edit Pipeline"
    EDIT_WEBAPP = "edit_webapp", "Edit Web App"
    GENERATE_SQL = "generate_sql", "Generate SQL"
    NAMING = "naming", "Naming"
