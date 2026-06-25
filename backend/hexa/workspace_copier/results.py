"""Result dataclasses for a copy run, plus summary formatting.

Each resource copier records what it did/skipped/failed in its own per-resource
result, attached to the run-wide :class:`CopyResult`. The CLI and admin
views render that aggregate via :func:`format_summary`.
"""

from dataclasses import dataclass, field


@dataclass
class FilesResult:
    """What the files copier did, for the summary."""

    copied: list[tuple[str, int]] = field(default_factory=list)
    """(object_key, byte_size) for each file copied to target."""

    failed: list[str] = field(default_factory=list)
    """Object keys whose download or upload failed; user must handle manually."""


@dataclass
class ConnectionsResult:
    """What the connections copier did, for the summary."""

    created: list[tuple[str, int]] = field(default_factory=list)
    """(slug, field_count) for each connection created on target."""

    skipped: list[str] = field(default_factory=list)
    """Slugs that already existed on target."""

    failed: list[str] = field(default_factory=list)
    """Slugs whose creation failed; user must handle manually."""

    warnings: list[str] = field(default_factory=list)
    """Human-readable warnings (e.g. secret fields created with no value)."""


@dataclass
class PipelinesResult:
    """What the pipelines copier did, for the summary."""

    created: list[tuple[str, list[str]]] = field(default_factory=list)
    """(pipeline_code, [version_name, ...]) for each pipeline created on target."""

    skipped: list[str] = field(default_factory=list)
    """Pipeline codes that already existed on target or could not be copied."""

    failed: list[str] = field(default_factory=list)
    """Pipeline codes whose creation failed; user must handle manually."""

    warnings: list[str] = field(default_factory=list)
    """Human-readable warnings to print in the summary."""


@dataclass
class CopyResult:
    """Aggregate of a single workspace copy run.

    Copiers attach their per-resource result here and append run-wide warnings
    (e.g. a skipped database copy or a deselected dependency) via :meth:`warn`.
    """

    workspace_name: str | None = None
    workspace_slug: str | None = None
    files: FilesResult | None = None
    connections: ConnectionsResult | None = None
    pipelines: PipelinesResult | None = None
    warnings: list[str] = field(default_factory=list)

    def warn(self, message: str) -> None:
        self.warnings.append(message)


def format_summary(result: CopyResult) -> str:
    """Render a human-readable summary of a copy run."""
    lines: list[str] = ["=== Copy summary ==="]
    lines.append(
        f"Workspace: {result.workspace_name!r} -> slug '{result.workspace_slug}'"
    )

    if result.files is not None:
        total_bytes = sum(b for _, b in result.files.copied)
        lines.append(f"Files copied: {len(result.files.copied)} ({total_bytes} bytes)")
        if result.files.failed:
            lines.append(
                f"Files that could NOT be copied "
                f"({len(result.files.failed)} — handle manually):"
            )
            lines.extend(f"  * {path}" for path in result.files.failed)

    if result.connections is not None:
        conns = result.connections
        lines.append(f"Connections created: {len(conns.created)}")
        lines.extend(f"  * {slug} ({n} field(s))" for slug, n in conns.created)
        if conns.skipped:
            lines.append(f"Connections skipped (already existed): {len(conns.skipped)}")
            lines.extend(f"  * {slug}" for slug in conns.skipped)
        if conns.failed:
            lines.append(
                f"Connections that could NOT be copied "
                f"({len(conns.failed)} — handle manually):"
            )
            lines.extend(f"  * {slug}" for slug in conns.failed)
        if conns.warnings:
            lines.append("Connection warnings:")
            lines.extend(f"  - {w}" for w in conns.warnings)

    if result.pipelines is not None:
        pipes = result.pipelines
        lines.append(f"Pipelines created: {len(pipes.created)}")
        for code, vnames in pipes.created:
            lines.append(f"  * {code}")
            lines.extend(f"      - {vn}" for vn in vnames)
        if pipes.skipped:
            lines.append(f"Pipelines skipped (already existed): {len(pipes.skipped)}")
            lines.extend(f"  * {code}" for code in pipes.skipped)
        if pipes.failed:
            lines.append(
                f"Pipelines that could NOT be copied "
                f"({len(pipes.failed)} — handle manually):"
            )
            lines.extend(f"  * {code}" for code in pipes.failed)
        if pipes.warnings:
            lines.append("Pipeline warnings:")
            lines.extend(f"  - {w}" for w in pipes.warnings)

    if result.warnings:
        lines.append("Warnings:")
        lines.extend(f"  - {w}" for w in result.warnings)

    return "\n".join(lines)
