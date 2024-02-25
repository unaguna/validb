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
