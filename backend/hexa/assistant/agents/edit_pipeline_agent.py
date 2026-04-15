import io
import zipfile

from pydantic import BaseModel

from hexa.assistant.agents.base import BaseAgent
from hexa.assistant.instructions import InstructionSet
from hexa.pipelines.models import Pipeline


class ProposedFile(BaseModel):
    name: str
    content: str


def propose_pipeline_version(
    pipeline: Pipeline,
    modified_files: list[ProposedFile] | None = None,
    deleted_files: list[str] | None = None,
) -> dict:
    """Propose a new version of the pipeline.

    Always call this tool with the files you modified or created in modified_files.
    Each entry must have a 'name' (e.g. 'pipeline.py') and 'content' (the full file text).
    List any files to remove in deleted_files.
    Unchanged files are preserved automatically.
    """
    current_files: dict[str, str] = {}
    current_version = pipeline.last_version if pipeline is not None else None
    if current_version and current_version.zipfile:
        with zipfile.ZipFile(io.BytesIO(bytes(current_version.zipfile)), "r") as zf:
            for name in zf.namelist():
                try:
                    current_files[name] = zf.read(name).decode("utf-8")
                except UnicodeDecodeError:
                    pass

    for f in modified_files or []:
        current_files[f.name] = f.content
    for name in deleted_files or []:
        current_files.pop(name, None)

    return {"files": [{"name": k, "content": v} for k, v in current_files.items()]}


class EditPipelineAgent(BaseAgent):
    instruction_set = InstructionSet.EDIT_PIPELINE
    tools = [propose_pipeline_version]

    @property
    def _context(self) -> dict:
        ctx = super()._context
        return {**ctx, "pipeline": self.conversation.linked_object}

    def _extra_instructions(self) -> str:
        linked_object = self.conversation.linked_object
        if linked_object is None:
            return ""
        if not isinstance(linked_object, Pipeline):
            raise TypeError(
                f"EditPipelineAgent requires a Pipeline linked object, got {type(linked_object).__name__}"
            )
        pipeline = linked_object

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
