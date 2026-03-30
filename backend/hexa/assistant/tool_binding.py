import functools
import inspect
from collections.abc import Callable


def bind_context(func: Callable, context: dict) -> Callable:
    params = inspect.signature(func).parameters
    inject = {k: v for k, v in context.items() if k in params}
    if not inject:
        return func
    bound = functools.partial(func, **inject)
    bound.__signature__ = inspect.signature(func).replace(
        parameters=[p for n, p in params.items() if n not in inject]
    )
    bound.__doc__ = func.__doc__
    bound.__name__ = func.__name__
    bound.__qualname__ = func.__qualname__
    return bound
