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
You are in charge of creating a new pipeline for the user.\
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
