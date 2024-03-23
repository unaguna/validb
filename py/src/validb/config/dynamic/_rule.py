import typing as t

from ..._classloader import construct_imported_dinamically
from ...rules import Rule


def construct_rule(rule_attr: t.Mapping[str, t.Any]) -> Rule[t.Any, t.Any, t.Any]:
    return construct_imported_dinamically(
        rule_attr,
        Rule,  # type: ignore
    )
