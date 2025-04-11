"""The Jac Programming Language."""

from typing import Callable

from jaclang.plugin.default import JacFeatureImpl
from jaclang.plugin.feature import JacFeature, plugin_manager


plugin_manager.register(JacFeatureImpl)
plugin_manager.load_setuptools_entrypoints("jac")


def with_entry(func: Callable) -> Callable:
    """Mark a method as jac entry with this decorator."""
    setattr(func, "__jac_entry", True)  # noqa: B010
    return func


def with_exit(func: Callable) -> Callable:
    """Mark a method as jac exit with this decorator."""
    setattr(func, "__jac_exit", True)  # noqa: B010
    return func


__all__ = ["with_entry", "with_exit", "JacFeature"]
