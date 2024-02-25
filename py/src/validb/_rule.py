import abc
import typing as t
from ._detected import MSG, MSG_TYPE


class Rule(t.Generic[MSG_TYPE, MSG], abc.ABC):
    @property
    @abc.abstractmethod
    def sql(self) -> str:
        pass

    @abc.abstractmethod
    def detected(self) -> t.Tuple[MSG_TYPE, MSG]:
        pass


class SimpleRule(t.Generic[MSG_TYPE, MSG], Rule[MSG_TYPE, MSG]):
    _sql: str
    _msg_type: MSG_TYPE
    _msg: MSG

    def __init__(self, sql: str, msg_type: MSG_TYPE, msg: MSG) -> None:
        super().__init__()

        self._sql = sql
        self._msg_type = msg_type
        self._msg = msg

    @property
    def sql(self) -> str:
        return self._sql

    def detected(self) -> t.Tuple[MSG_TYPE, MSG]:
        return self._msg_type, self._msg
