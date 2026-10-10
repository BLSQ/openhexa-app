"""Resolution of `openhexa.*` symbols against the installed packages.

Introspecting the installed `openhexa-sdk` and `openhexa-toolbox` rather than a
hardcoded list keeps the rule current: bump either pin and agents using a
removed API start failing.

A module that exists but cannot be imported here is reported as unverifiable
rather than missing. `openhexa.toolbox.era5.extract` is the example: it needs
xarray, which the app image does not install. Calling that a hallucination would
blame the agent for the image's dependency set.
"""

from __future__ import annotations

import importlib
import importlib.util
from enum import Enum
from functools import cache
from types import ModuleType

OPENHEXA_ROOT = "openhexa"


class ModuleStatus(str, Enum):
    MISSING = "missing"
    IMPORTABLE = "importable"
    UNIMPORTABLE = "unimportable"


def _guard(name: str) -> None:
    if name != OPENHEXA_ROOT and not name.startswith(f"{OPENHEXA_ROOT}."):
        raise ValueError(f"refusing to resolve non-openhexa module {name!r}")


@cache
def module_status(name: str) -> ModuleStatus:
    _guard(name)
    try:
        spec = importlib.util.find_spec(name)
    except ModuleNotFoundError as exc:
        # find_spec imports parent packages; a failure naming this module (or an
        # ancestor of it) means it genuinely does not exist, whereas a failure
        # naming anything else is a missing third-party dependency.
        missing = exc.name or ""
        return (
            ModuleStatus.MISSING
            if name.startswith(missing)
            else ModuleStatus.UNIMPORTABLE
        )
    except Exception:
        return ModuleStatus.UNIMPORTABLE
    if spec is None:
        return ModuleStatus.MISSING
    try:
        importlib.import_module(name)
    except Exception:
        return ModuleStatus.UNIMPORTABLE
    return ModuleStatus.IMPORTABLE


@cache
def import_module(name: str) -> ModuleType | None:
    if module_status(name) is not ModuleStatus.IMPORTABLE:
        return None
    return importlib.import_module(name)


@cache
def module_exports(name: str) -> frozenset[str]:
    module = import_module(name)
    if module is None:
        return frozenset()
    return frozenset(attr for attr in dir(module) if not attr.startswith("_"))


def module_exists(name: str) -> bool | None:
    """True / False, or None when the module exists but cannot be imported here."""
    status = module_status(name)
    if status is ModuleStatus.UNIMPORTABLE:
        return None
    return status is ModuleStatus.IMPORTABLE


def module_has(name: str, attr: str) -> bool | None:
    """Whether `attr` is an export or a submodule, or None if unverifiable."""
    status = module_status(name)
    if status is ModuleStatus.UNIMPORTABLE:
        return None
    if status is ModuleStatus.MISSING:
        return False
    if attr in module_exports(name):
        return True
    return module_exists(f"{name}.{attr}")


@cache
def _singleton_attrs(export: str) -> frozenset[str]:
    """Public attributes of an SDK singleton such as `workspace`.

    Introspects the live object rather than its class, so attributes set in
    __init__ are included.
    """
    sdk = import_module(f"{OPENHEXA_ROOT}.sdk")
    if sdk is None or not hasattr(sdk, export):
        return frozenset()
    obj = getattr(sdk, export)
    return frozenset(attr for attr in dir(obj) if not attr.startswith("_"))


def workspace_attrs() -> frozenset[str]:
    return _singleton_attrs("workspace")


def current_run_attrs() -> frozenset[str]:
    return _singleton_attrs("current_run")


def sdk_available() -> bool:
    return module_status(f"{OPENHEXA_ROOT}.sdk") is ModuleStatus.IMPORTABLE
