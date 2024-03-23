import typing as t

from validb import Rule, EmbeddedVariables
from validb.config import parse_object


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
