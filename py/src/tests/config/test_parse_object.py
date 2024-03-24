import typing as t

import pytest

from validb import Rule, EmbeddedVariables
from validb.config import parse_object


def test__parse_object():
    # Try this function for some class in the standard library.

    attr: t.Mapping[str, t.Any] = {
        "class": "decimal.Decimal",
        "value": "1.02",
    }
    value: t.Any = parse_object(
        attr,
        path="",
        expected_class=object,
    )

    from decimal import Decimal

    assert isinstance(value, Decimal)
    assert value == Decimal(attr["value"])


@pytest.mark.require_sqlalchemy
def test__parse_object__SimpleSQLAlchemyRule():
    attr: t.Mapping[str, t.Any] = {
        "class": "validb.rules.sqlalchemy.SimpleSQLAlchemyRule",
        "sql": "SELECT NONE",
        "id": "{0}",
        "detection_type": "DUMMY",
        "msg": "dummy rule",
        "datasource": "dummy_source",
        "embedders": [],
    }
    rule: Rule[str, str, str] = parse_object(
        attr,
        path="",
        expected_class=Rule,
    )

    from validb.rules.sqlalchemy import SimpleSQLAlchemyRule

    stub_values = EmbeddedVariables(["dummy_0"], {})

    assert isinstance(rule, SimpleSQLAlchemyRule)
    assert rule.sql == attr["sql"]
    assert rule.id_of_row(stub_values) == "dummy_0"
    assert rule.detection_type() == attr["detection_type"]
    assert rule.message(stub_values) == attr["msg"]
    assert rule.datasource_name == attr["datasource"]
    assert list(rule.embedders()) == attr["embedders"]
