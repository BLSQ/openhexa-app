import json

from pydantic import BaseModel

from hexa.assistant.models import Conversation
from hexa.assistant.tools.proposals import (
    nothing_to_delete_error,
    pending_proposal,
    resolve_commit_message,
    resolve_deleted_paths,
    working_files,
)
from hexa.core.text_files import (
    AGENT_READ,
    GREP_HEAD_LIMIT,
    GrepOutputMode,
    TextFiles,
)
from hexa.git.enums import FileEncoding
from hexa.webapps.models import GitWebapp


class ProposedFile(BaseModel):
    path: str
    content: str


class FilePatch(BaseModel):
    path: str
    old_string: str
    new_string: str


def _webapp_files(webapp: GitWebapp, conversation: Conversation | None) -> TextFiles:
    return working_files(
        webapp.get_text_files(), conversation, "propose_webapp_version"
    )


def glob_webapp_files(
    webapp: GitWebapp, pattern: str, conversation: Conversation | None = None
) -> dict:
    """Find web app files by path pattern, e.g. `**/*.js`, `css/*.css` or `*.{html,js}`.

    `*` stays within a directory and `**` spans any depth. Returns sorted paths, at most
    100: when `truncated` is true, narrow the pattern. Lists binary files too. Reflects
    the pending proposal if there is one.
    """
    return _webapp_files(webapp, conversation).glob(pattern)


def grep_webapp_files(
    webapp: GitWebapp,
    pattern: str,
    glob: str | None = None,
    output_mode: GrepOutputMode = GrepOutputMode.FILES_WITH_MATCHES,
    ignore_case: bool = False,
    context: int = 0,
    head_limit: int = GREP_HEAD_LIMIT,
    offset: int = 0,
    conversation: Conversation | None = None,
) -> dict:
    """Search the contents of the web app's text files with a Python regular expression.

    Use it to find where something is defined or used before reading a file, instead of
    reading whole files. Patterns match within a single line; escape regex metacharacters
    such as `{`, `(` or `.` with a backslash. Restrict the files searched with `glob`
    (e.g. `**/*.js`).

    output_mode: `files_with_matches` (default) lists matching paths; `content` returns
    matching lines as `path:line:text`, with `context` lines around each match as
    `path-line-text`; `count` returns matches per file and their total.
    head_limit and offset page through the entries; `truncated` tells there are more.
    Reflects the pending proposal if there is one.
    """
    return _webapp_files(webapp, conversation).grep(
        pattern,
        glob=glob,
        output_mode=output_mode,
        ignore_case=ignore_case,
        context=context,
        head_limit=head_limit,
        offset=offset,
    )


def read_webapp_file(
    webapp: GitWebapp,
    path: str,
    start_line: int | None = None,
    end_line: int | None = None,
    conversation: Conversation | None = None,
) -> dict:
    """Read a web app text file, with line numbers (`     N<TAB>line`, not part of the file).

    Pass start_line and end_line (1-indexed, inclusive) to read a section; find it first
    with grep_webapp_files. A read returns at most 2000 lines, with a notice telling how
    to read the rest, and clips lines over 2000 characters. Returns `total_lines`.
    Reflects the pending proposal if there is one: always read files from here, so your
    patches match what the next proposal builds on.
    """
    return _webapp_files(webapp, conversation).read(
        path, start_line, end_line, AGENT_READ
    )


def propose_webapp_version(
    webapp: GitWebapp,
    modified_files: list[ProposedFile] | None = None,
    file_patches: list[FilePatch] | str | None = None,
    deleted_files: list[str] | None = None,
    commit_message: str | None = None,
    conversation: Conversation | None = None,
) -> dict:
    """Propose changes to the web app files.

    Two ways to describe changes — use whichever fits:

    - modified_files: pass the full new content for files you created or rewrote entirely
      (each entry needs a 'path' and 'content').
    - file_patches: for targeted edits to existing files, pass {path, old_string, new_string}.
      The backend finds old_string in the current file and replaces it with new_string.
      Prefer this over modified_files when changing a few lines of a large file — you
      only need to read and reproduce the lines that actually change.

    List any files to remove in deleted_files. A directory path removes everything under it.
    Deletions cover binary files (images, fonts) too, even though their content is never
    inlined here.
    Unchanged files are preserved automatically.
    You can mix modified_files and file_patches in the same call.
    Pass commit_message to describe the change as a Conventional Commit: a
    `type(scope): summary` subject line, optionally followed by a blank line and a
    short body explaining why.
    It becomes the commit message if the user accepts the proposal.
    """
    if isinstance(file_patches, str):
        try:
            raw = json.loads(file_patches)
            file_patches = [FilePatch(**item) for item in raw]
        except (json.JSONDecodeError, TypeError, ValueError):
            return {
                "error": "file_patches must be a list of {path, old_string, new_string} objects."
            }

    if not modified_files and not file_patches and not deleted_files:
        return {
            "error": (
                "No changes provided. Pass modified files in modified_files, "
                "targeted find/replace edits in file_patches, or paths to remove "
                "in deleted_files. Do not call this tool until you have the actual changes ready."
            )
        }

    current_files: dict[str, str] = {}
    deleted_paths: set[str] = set()

    pending = pending_proposal(conversation, "propose_webapp_version")

    repo_files = None
    if pending and pending.tool_output:
        for f in pending.tool_output.get("files", []):
            current_files[f["path"]] = f["content"]
        deleted_paths.update(pending.tool_output.get("deleted_paths", []))
    else:
        repo_files = webapp.get_files(include_binary_content=False)
        for f in repo_files:
            if f.get("encoding") == FileEncoding.TEXT and f.get("content") is not None:
                current_files[f["path"]] = f["content"]

    for patch in file_patches or []:
        if patch.path not in current_files:
            return {
                "error": f"Cannot patch '{patch.path}': file not found in the current version."
            }
        original = current_files[patch.path]
        if patch.old_string not in original:
            return {
                "error": (
                    f"Cannot patch '{patch.path}': old_string not found in the file. "
                    "Make sure it matches the current content exactly, including whitespace."
                )
            }
        current_files[patch.path] = original.replace(
            patch.old_string, patch.new_string, 1
        )

    for f in modified_files or []:
        current_files[f.path] = f.content
        deleted_paths.discard(f.path)

    if deleted_files:
        if repo_files is None:
            repo_files = webapp.get_files(include_binary_content=False)
        known_paths = (
            {f["path"] for f in repo_files if f.get("type") == "file"}
            | set(current_files)
            | deleted_paths
        )
        resolved, unmatched = resolve_deleted_paths(deleted_files, known_paths)
        if unmatched:
            return nothing_to_delete_error(unmatched)
        deleted_paths |= resolved
        for path in resolved:
            current_files.pop(path, None)

    output = {
        "files": [{"path": k, "content": v} for k, v in current_files.items()],
        "deleted_paths": sorted(deleted_paths),
    }
    message = resolve_commit_message(
        commit_message, pending.tool_output if pending else None
    )
    if message:
        output["commit_message"] = message
    return output
