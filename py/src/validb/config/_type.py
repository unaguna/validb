import typing as t


class RuleDefRequired(t.TypedDict):
    sql: str
    id: str
    detection_type: str
    msg: str
    datasource: str


class RuleDef(RuleDefRequired, total=False):
    level: int
    embedders: t.List[str]


class RulesFile(t.TypedDict, total=False):
    rules: t.Sequence[RuleDef]
    embedders: t.Mapping[str, t.Any]
    datasources: t.Mapping[str, t.Any]
