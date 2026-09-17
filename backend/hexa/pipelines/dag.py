"""Static extraction of a pipeline's task graph from its source code.

OpenHEXA persists no task graph. The SDK builds it at runtime by deferred execution:
``@<pipeline>.task`` rebinds a function name to a ``PipelineWithTask`` object, so calling
it inside the pipeline body creates a ``Task`` node holding references to the ``Task``
objects it received as arguments. Those references are the edges, and they only exist in
the worker's memory for the duration of a run — nothing is ever sent back to the app.

This module replays that same reasoning statically, over the stored source text: it tracks
which local name holds which task's result, and emits an edge whenever such a name reaches
another task's arguments.

The result is a *lower bound* on the real graph. It never invents a dependency, but it
cannot see through loops, conditionals, or indirection through undecorated helpers.
"""

import ast
import io
from zipfile import ZipFile

ENTRYPOINT = "pipeline.py"


def extract_dag_from_zipfile(zipfile_data: bytes) -> dict:
    """Return the task graph of a pipeline version's zip archive.

    Only ``pipeline.py`` at the archive root is read, mirroring the SDK's ``get_pipeline()``.
    Scanning the archive for a ``@pipeline`` decorator would risk describing a module that
    never runs.
    """
    try:
        with ZipFile(io.BytesIO(zipfile_data)) as zip_file:
            source = zip_file.read(ENTRYPOINT).decode()
    except Exception:
        return _empty()

    return extract_dag(source)


def extract_dag(source: str) -> dict:
    """Return ``{"tasks": [...], "edges": [...]}`` for a pipeline module's source.

    Task ids are function names; edge sources are either a task id or a parameter code, and
    the caller discriminates by looking the source up in the task list.

    Unlike ``_parse_parameters_from_zipfile``, which raises so a bad upload is rejected, this
    is deliberately silent: it feeds a read-only view and must never break the pipeline page.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return _empty()

    entrypoint = _find_pipeline_function(tree)
    if entrypoint is None:
        return _empty()

    # The @pipeline decorator rebinds the decorated function's name to a Pipeline instance,
    # so the function's own name is what tasks are decorated with.
    pipeline_var = entrypoint.name
    tasks = _find_tasks(tree, pipeline_var)
    edges = _find_edges(entrypoint, set(tasks))

    return {
        "tasks": [{"id": name, "name": name} for name in tasks],
        "edges": [
            {"source": source_id, "target": target} for source_id, target in edges
        ],
    }


def _empty() -> dict:
    return {"tasks": [], "edges": []}


def _find_pipeline_function(tree: ast.Module) -> ast.FunctionDef | None:
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef):
            continue
        for decorator in node.decorator_list:
            if (
                isinstance(decorator, ast.Call)
                and isinstance(decorator.func, ast.Name)
                and decorator.func.id == "pipeline"
            ):
                return node
    return None


def _find_tasks(tree: ast.Module, pipeline_var: str) -> list[str]:
    """Return the names of functions decorated with ``@<pipeline_var>.task``.

    The decorator takes no arguments, so it is a bare ``ast.Attribute`` and never an
    ``ast.Call`` — which is why the SDK's own ``_get_decorators_by_name`` cannot be reused
    here: it only considers ``ast.Call`` decorators and would match nothing.
    """
    tasks = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef) or node.name in tasks:
            continue
        for decorator in node.decorator_list:
            if (
                isinstance(decorator, ast.Attribute)
                and decorator.attr == "task"
                and isinstance(decorator.value, ast.Name)
                and decorator.value.id == pipeline_var
            ):
                tasks.append(node.name)
                break
    return tasks


def _find_edges(
    entrypoint: ast.FunctionDef, task_names: set[str]
) -> list[tuple[str, str]]:
    """Walk the pipeline body, mapping local names to whatever produced them.

    The map is seeded with the pipeline function's own arguments, whose names are the
    parameter codes — so a parameter reaching a task's arguments yields an edge just like a
    task result does.
    """
    producers = {argument.arg: argument.arg for argument in entrypoint.args.args}
    edges: list[tuple[str, str]] = []

    def is_task_call(node: ast.AST) -> bool:
        return (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id in task_names
        )

    def add_edge(source: str, target: str) -> None:
        if (source, target) not in edges:
            edges.append((source, target))

    def visit_call(call: ast.Call) -> str:
        """Record the edges feeding a task call and return the task it targets.

        A nested call such as ``t3(t2(t1()))`` recurses so that ``t1`` is wired to ``t2``
        rather than to ``t3`` — mirroring the SDK, where ``t2`` is the Task that ends up
        holding a reference to ``t1``.
        """
        target = call.func.id
        arguments = list(call.args) + [keyword.value for keyword in call.keywords]
        for argument in arguments:
            if isinstance(argument, ast.Name) and argument.id in producers:
                add_edge(producers[argument.id], target)
            elif is_task_call(argument):
                add_edge(visit_call(argument), target)
        return target

    for statement in ast.walk(entrypoint):
        target = None
        if isinstance(statement, ast.Assign):
            call = statement.value
            if len(statement.targets) == 1 and isinstance(
                statement.targets[0], ast.Name
            ):
                target = statement.targets[0].id
        elif isinstance(statement, ast.Expr):
            call = statement.value
        else:
            continue

        if not is_task_call(call):
            continue

        producer = visit_call(call)
        if target is not None:
            producers[target] = producer

    return edges
