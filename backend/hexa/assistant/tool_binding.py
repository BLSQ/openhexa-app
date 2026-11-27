import functools
import inspect
from collections.abc import Callable


def bind_context(func: Callable, context: dict) -> Callable:
    """Fix the arguments of `func` named in `context` and hide them from the model.

    A bound argument always takes its context value, even when the model sends one
    of its own: it is what confines the assistant to its conversation's workspace.
    """
    params = inspect.signature(func).parameters
    inject = {k: v for k, v in context.items() if k in params}
    if not inject:
        return func

    @functools.wraps(func)
    def bound(*args, **kwargs):
        return func(*args, **{**kwargs, **inject})

    bound.__signature__ = inspect.signature(func).replace(
        parameters=[p for n, p in params.items() if n not in inject]
    )
    return bound
