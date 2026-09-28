"""Static extraction of a pipeline's task graph from its source code.

OpenHEXA persists no task graph. The SDK builds it at runtime by deferred execution:
``@<pipeline>.task`` rebinds a function name to a ``PipelineWithTask`` object, so calling
it inside the pipeline body creates a ``Task`` node holding references to the ``Task``
objects it received as arguments. Those references are the edges, and they only exist in
the worker's memory for the duration of a run — nothing is ever sent back to the app.

This module replays that same reasoning statically, over the stored source text: it tracks
which local name holds which task's result, and emits an edge whenever such a name reaches
another task's arguments.

The body is followed in source order, each name standing for the task that last assigned it.
The result approximates the real graph: it cannot see a dependency that only appears on a later
loop iteration, it assumes every branch of a conditional runs, and it does not look inside
helper functions, whose arguments are unknown until they are called.
"""

import ast
import io
import logging
from zipfile import ZipFile

logger = logging.getLogger(__name__)

ENTRYPOINT = "pipeline.py"


def extract_dag_from_zipfile(zipfile_data: bytes | None) -> dict:
    """Return the task graph of a pipeline version's zip archive.

    Only ``pipeline.py`` at the archive root is read, mirroring the SDK's ``get_pipeline()``.
    Scanning the archive for a ``@pipeline`` decorator would risk describing a module that
    never runs.
    """
    if not zipfile_data:
        return _empty()

    try:
        with ZipFile(io.BytesIO(zipfile_data)) as zip_file:
            source = zip_file.read(ENTRYPOINT).decode()
    except KeyError:
        # Uploads without a pipeline.py are accepted (see _parse_parameters_from_zipfile).
        return _empty()
    except Exception:
        logger.exception("Failed to read pipeline source from zipfile")
        return _empty()

    return extract_dag(source)


def extract_dag(source: str) -> dict:
    """Return ``{"tasks": [...], "edges": [...]}`` for a pipeline module's source.

    Task ids are function names; edge sources are either a task id or a parameter code, and
    the caller discriminates by looking the source up in the task list.

    Unlike ``_parse_parameters_from_zipfile``, which raises so a bad upload is rejected, this
    returns an empty graph on extraction failure and logs the exception for investigation.
    """
    try:
        tree = ast.parse(source)
        entrypoint = _find_pipeline_function(tree)
        if entrypoint is None:
            return _empty()

        # The @pipeline decorator rebinds the decorated function's name to a Pipeline
        # instance, so the function's own name is what tasks are decorated with.
        pipeline_var = entrypoint.name
        declared = _find_tasks(tree, pipeline_var)
        edges, call_order = _walk_body(entrypoint, set(declared))
        # Call order is execution order; tasks never called keep their declaration order.
        tasks = call_order + [name for name in declared if name not in call_order]
    except Exception:
        logger.exception("Failed to extract DAG from pipeline source")
        return _empty()

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


def _walk_body(
    entrypoint: ast.FunctionDef, task_names: set[str]
) -> tuple[list[tuple[str, str]], list[str]]:
    """Walk the pipeline body, returning its edges and the tasks in the order they are called.

    Local names are mapped to whatever produced them. The map is seeded with the pipeline function's own arguments, whose names are the
    parameter codes — so a parameter reaching a task's arguments yields an edge just like a
    task result does.
    """
    producers = {argument.arg: argument.arg for argument in entrypoint.args.args}
    edges: list[tuple[str, str]] = []
    call_order: list[str] = []

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
        # Recorded after the arguments: in t2(t1()), t1 runs first.
        if target not in call_order:
            call_order.append(target)
        return target

    def visit_statement(statement: ast.stmt) -> None:
        target = None
        if isinstance(statement, ast.Assign):
            call = statement.value
            if len(statement.targets) == 1 and isinstance(
                statement.targets[0], ast.Name
            ):
                target = statement.targets[0].id
        elif isinstance(statement, ast.AnnAssign):
            call = statement.value
            if isinstance(statement.target, ast.Name):
                target = statement.target.id
        elif isinstance(statement, ast.Expr):
            call = statement.value
        else:
            call = None

        producer = visit_call(call) if is_task_call(call) else None

        # A name rebound to anything but a task result no longer carries the old edge.
        for name in _bound_names(statement):
            producers.pop(name, None)
        if target is not None and producer is not None:
            producers[target] = producer

    def visit_block(node: ast.AST) -> None:
        # ast.walk is breadth-first, so it would read nested blocks after every top-level
        # statement. Iterating children keeps the order in which the code actually runs.
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
                continue
            if isinstance(child, ast.stmt):
                visit_statement(child)
                visit_block(child)
            elif isinstance(child, ast.ExceptHandler | ast.match_case):
                visit_block(child)

    visit_block(entrypoint)
    return edges, call_order


def _bound_names(statement: ast.stmt) -> list[str]:
    if isinstance(statement, ast.Assign):
        targets = statement.targets
    elif isinstance(statement, ast.AnnAssign | ast.AugAssign | ast.For | ast.AsyncFor):
        targets = [statement.target]
    elif isinstance(statement, ast.With | ast.AsyncWith):
        targets = [item.optional_vars for item in statement.items if item.optional_vars]
    else:
        return []
    return [
        node.id
        for target in targets
        for node in ast.walk(target)
        if isinstance(node, ast.Name)
    ]
