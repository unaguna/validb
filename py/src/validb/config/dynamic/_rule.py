import typing as t

from ..._classloader import (
    construct_imported_dinamically,
    IllegalPathError,
    NonClassLoadedError,
    UnexpectedClassLoadedError,
)
from ...rules import Rule


def construct_rule(rule_attr: t.Mapping[str, t.Any]) -> Rule[t.Any, t.Any, t.Any]:
    try:
        return construct_imported_dinamically(
            rule_attr,
            Rule,  # type: ignore
        )
    except IllegalPathError as e:
        raise ValueError(
            f"rules.*.class must be a string like 'module.class'; actually specified path: {e.actual_path}"
        )
    except (UnexpectedClassLoadedError, NonClassLoadedError) as e:
        raise TypeError(
            f"rule must be instance of {Rule.__name__}; actual loaded: {e.actual_loaded}"
        )
