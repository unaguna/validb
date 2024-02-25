import abc
import typing as t

import sqlalchemy

from ._detected import ID, MSG, MSG_TYPE


class Rule(t.Generic[ID, MSG_TYPE, MSG], abc.ABC):
    @property
    @abc.abstractmethod
    def sql(self) -> str:
        pass

    @abc.abstractmethod
    def id_of_row(self, row: sqlalchemy.Row[t.Any]) -> ID:
        pass

    @abc.abstractmethod
    def detected(self) -> t.Tuple[MSG_TYPE, MSG]:
        pass


class SimpleRule(t.Generic[ID, MSG_TYPE, MSG], Rule[ID, MSG_TYPE, MSG]):
    _sql: str
    _id_of_row: t.Callable[[t.Any], ID]
    _msg_type: MSG_TYPE
    _msg: MSG

    def __init__(
        self, sql: str, id_of_row: t.Callable[[t.Any], ID], msg_type: MSG_TYPE, msg: MSG
    ) -> None:
        super().__init__()

        self._sql = sql
        self._id_of_row = id_of_row
        self._msg_type = msg_type
        self._msg = msg

    @property
    def sql(self) -> str:
        return self._sql

    def id_of_row(self, row: t.Any) -> ID:
        return self._id_of_row(row)

    def detected(self) -> t.Tuple[MSG_TYPE, MSG]:
        return self._msg_type, self._msg


class TextRule(Rule[str, str, str]):
    _sql: str
    _id_template: str
    _msg_type: str
    _msg: str

    def __init__(self, sql: str, id_template: str, msg_type: str, msg: str) -> None:
        super().__init__()

        self._sql = sql
        self._id_template = id_template
        self._msg_type = msg_type
        self._msg = msg

    @property
    def sql(self) -> str:
        return self._sql

    def id_of_row(self, row: sqlalchemy.Row[t.Any]) -> str:
        return self._id_template.format(*row)

    def detected(self) -> t.Tuple[str, str]:
        return self._msg_type, self._msg


class RuleDef(t.TypedDict):
    sql: str
    id: str
    msg_type: str
    msg: str


def load_rules_from_yaml(filepath: str) -> t.List[TextRule]:
    import yaml

    with open(filepath, mode="r") as fp:
        rules: t.List[RuleDef] = yaml.safe_load(fp)

    return [
        TextRule(
            sql=rule["sql"],
            id_template=rule["id"],
            msg_type=rule["msg_type"],
            msg=rule["msg"],
        )
        for rule in rules
    ]
