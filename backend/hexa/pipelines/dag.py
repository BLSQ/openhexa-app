"""Static AST extraction of a pipeline's task DAG and declared outputs.

The pipeline task graph and outputs are not persisted anywhere; they only exist
while a pipeline runs. This module reconstructs them by parsing the pipeline
source code (``pipeline.py``) the same way the platform already parses code to
extract parameters.
"""

from __future__ import annotations

import ast

_OUTPUT_CALLS = {
    "add_file_output": "file",
    "add_database_output": "db",
}

# Calls that indicate a task writes a dataset (a new dataset and/or a new version).
_DATASET_WRITE_CALLS = {"create_dataset", "create_version"}


def _pipeline_var(tree: ast.Module) -> str | None:
    """Return the name of the function decorated with @pipeline(...)."""
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        for dec in node.decorator_list:
            func = dec.func if isinstance(dec, ast.Call) else dec
            if isinstance(func, ast.Name) and func.id == "pipeline":
                return node.name
    return None


def _is_task_decorator(dec: ast.expr, pipeline_var: str) -> bool:
    """True for @<pipeline_var>.task (with or without call parens)."""
    target = dec.func if isinstance(dec, ast.Call) else dec
    return (
        isinstance(target, ast.Attribute)
        and target.attr == "task"
        and isinstance(target.value, ast.Name)
        and target.value.id == pipeline_var
    )


def _task_functions(tree: ast.Module, pipeline_var: str) -> dict[str, ast.FunctionDef]:
    tasks = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and any(
            _is_task_decorator(d, pipeline_var) for d in node.decorator_list
        ):
            tasks[node.name] = node
    return tasks


def _pipeline_function(tree: ast.Module, pipeline_var: str) -> ast.FunctionDef | None:
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == pipeline_var:
            return node
    return None


def _called_name(node: ast.expr) -> str | None:
    """Return the function name for a Call expression's callee, else None."""
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
        return node.func.id
    return None


def _extract_edges(pipeline_fn: ast.FunctionDef, task_names: set[str]) -> list[dict]:
    """Infer task->task edges from how task results flow through the pipeline body.

    A dependency exists only when one task's *result* is passed into another task,
    matching the SDK runtime semantics (Task.is_ready). Two ways a result flows:
      * via a variable:  r = a(); b(r)
      * via a nested call:  b(a())
    """
    var_to_task: dict[str, str] = {}
    edges: set[tuple[str, str]] = set()

    for stmt in ast.walk(pipeline_fn):
        # r = some_task(...)
        if isinstance(stmt, ast.Assign):
            callee = _called_name(stmt.value)
            if callee in task_names:
                for tgt in stmt.targets:
                    if isinstance(tgt, ast.Name):
                        var_to_task[tgt.id] = callee

    for call in ast.walk(pipeline_fn):
        if not isinstance(call, ast.Call):
            continue
        target = _called_name(call)
        if target not in task_names:
            continue
        for arg in call.args + [kw.value for kw in call.keywords]:
            if isinstance(arg, ast.Name) and arg.id in var_to_task:
                edges.add((var_to_task[arg.id], target))
            elif _called_name(arg) in task_names:
                edges.add((_called_name(arg), target))

    return [{"source": s, "target": t} for s, t in sorted(edges)]


def _fstring_to_hint(node: ast.JoinedStr) -> str:
    parts = []
    for value in node.values:
        if isinstance(value, ast.Constant) and isinstance(value.value, str):
            parts.append(value.value)
        else:
            parts.append("…")
    return "".join(parts)


def _resolve_arg_name(arg: ast.expr, fn: ast.FunctionDef) -> str | None:
    """Best-effort literal name for an output argument.

    Resolves: a string constant; a local variable assigned a constant or an
    f-string within the same function. Falls back to the source segment.
    """
    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
        return arg.value
    if isinstance(arg, ast.JoinedStr):
        return _fstring_to_hint(arg)
    if isinstance(arg, ast.Name):
        for stmt in ast.walk(fn):
            if isinstance(stmt, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == arg.id for t in stmt.targets
            ):
                val = stmt.value
                if isinstance(val, ast.Constant) and isinstance(val.value, str):
                    return val.value
                if isinstance(val, ast.JoinedStr):
                    return _fstring_to_hint(val)
    try:
        return ast.unparse(arg)
    except Exception:  # pragma: no cover - defensive
        return None


def _dataset_output_for_task(fn: ast.FunctionDef) -> dict | None:
    """Collapse a task's dataset operations into a single output, if any.

    A task writes a dataset when it calls ``create_dataset`` and/or
    ``create_version``. The output is named after the dataset itself
    (``create_dataset`` name, falling back to ``get_dataset`` slug) rather than
    the version label, which is not a meaningful output name.
    """
    has_write = False
    create_name = None
    get_name = None
    for node in ast.walk(fn):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)):
            continue
        attr = node.func.attr
        if attr in _DATASET_WRITE_CALLS:
            has_write = True
        if attr == "create_dataset" and node.args and create_name is None:
            create_name = _resolve_arg_name(node.args[0], fn)
        elif attr == "get_dataset" and node.args and get_name is None:
            get_name = _resolve_arg_name(node.args[0], fn)
    if not has_write:
        return None
    return {"type": "dataset", "name": create_name or get_name}


def _extract_outputs(task_fns: dict[str, ast.FunctionDef]) -> list[dict]:
    outputs: list[dict] = []

    def _append(kind: str, name: str | None, task_name: str) -> None:
        outputs.append(
            {
                "id": f"output-{len(outputs)}",
                "type": kind,
                "name": name,
                # snake_case key: GraphQL field `taskId` is resolved via
                # snake_case_fallback_resolvers (see config/schema.py).
                "task_id": task_name,
            }
        )

    for task_name, fn in task_fns.items():
        for node in ast.walk(fn):
            if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)):
                continue
            kind = _OUTPUT_CALLS.get(node.func.attr)
            if kind is None:
                continue
            name = _resolve_arg_name(node.args[0], fn) if node.args else None
            _append(kind, name, task_name)

        dataset = _dataset_output_for_task(fn)
        if dataset is not None:
            _append("dataset", dataset["name"], task_name)

    return outputs


def extract_dag(source: str) -> dict:
    """Parse pipeline source into {tasks, edges, outputs}. Never raises."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return {"tasks": [], "edges": [], "outputs": []}

    pipeline_var = _pipeline_var(tree)
    if not pipeline_var:
        return {"tasks": [], "edges": [], "outputs": []}

    task_fns = _task_functions(tree, pipeline_var)
    tasks = [{"id": name, "name": name} for name in task_fns]

    pipeline_fn = _pipeline_function(tree, pipeline_var)
    edges = (
        _extract_edges(pipeline_fn, set(task_fns)) if pipeline_fn is not None else []
    )

    outputs = _extract_outputs(task_fns)
    return {"tasks": tasks, "edges": edges, "outputs": outputs}
