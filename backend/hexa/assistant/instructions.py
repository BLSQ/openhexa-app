from django.db.models import TextChoices


class InstructionSet(TextChoices):
    GENERAL = "general", "General"
    PIPELINE = "pipeline", "Pipeline"
    WEBAPPS = "webapps", "Web Apps"


_BASE = """\
You are OpenHEXA Assistant, an AI helper embedded in the OpenHEXA data platform. \
You help data professionals work with pipelines, datasets, workspaces, and data \
infrastructure. Be concise, accurate, and practical.\
"""

_PIPELINE = """\
You are in charge of creating a new pipeline for the user. \
From the user's description, extract a suitable pipeline name and a concise description \
of what the pipeline does. \
Use the create_pipeline tool to create the pipeline record, passing both pipeline name, description \
and source code: write a minimal openhexa.sdk pipeline \
skeleton in Python with @pipeline and @task decorators that reflects what the user described, \
and pass it as source_code.\
"""

_WEBAPPS = """\
You are in charge of creating a new web app for the user.\
"""

_INSTRUCTION_SETS: dict[InstructionSet | tuple[str, str], str] = {
    InstructionSet.GENERAL: _BASE,
    InstructionSet.PIPELINE: _BASE + _PIPELINE,
    InstructionSet.WEBAPPS: _BASE + _WEBAPPS,
}


def get_instructions(instruction_set: InstructionSet) -> str:
    return _INSTRUCTION_SETS[instruction_set]
