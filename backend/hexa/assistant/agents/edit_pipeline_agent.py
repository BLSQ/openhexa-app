import io
import zipfile

from pydantic import BaseModel

from hexa.assistant.agents.base import BaseAgent
from hexa.assistant.instructions import InstructionSet


class ProposedFile(BaseModel):
    name: str
    content: str


def propose_pipeline_version(files: list[ProposedFile]) -> dict:
    """Propose a new version of the pipeline with updated files.

    Include ALL files in the proposal, not only the ones you modified.
    Each file must have a 'name' (e.g. 'pipeline.py') and 'content' (the full file text).
    """
    return {"files": [f.model_dump() for f in files]}


class EditPipelineAgent(BaseAgent):
    instruction_set = InstructionSet.EDIT_PIPELINE
    tools = [propose_pipeline_version]

    def _extra_instructions(self) -> str:
        pipeline = getattr(self.conversation, "pipeline", None)
        if not pipeline:
            return ""

        lines = [
            "## Current Pipeline",
            f"Name: {pipeline.name}",
            f"Code: {pipeline.code}",
        ]
        if pipeline.description:
            lines.append(f"Description: {pipeline.description}")

        current_version = pipeline.last_version
        if not current_version:
            return "\n".join(lines)

        lines.append(f"Current version: {current_version.version_name}")

        if current_version.zipfile:
            lines.append("")
            lines.append("### Files")
            with zipfile.ZipFile(io.BytesIO(bytes(current_version.zipfile)), "r") as zf:
                for name in sorted(zf.namelist()):
                    try:
                        content = zf.read(name).decode("utf-8")
                    except UnicodeDecodeError:
                        continue
                    lines.append(f"\n#### {name}\n```\n{content}\n```")

        return "\n".join(lines)
