import abc
import typing as t


ID = t.TypeVar("ID")
MSG_TYPE = t.TypeVar("MSG_TYPE")
MSG = t.TypeVar("MSG")


class Detected(t.Generic[ID, MSG_TYPE, MSG], abc.ABC):
    _id: ID
    _msg_type: MSG_TYPE
    _msg: MSG

    def __init__(self, id: ID, msg_type: MSG_TYPE, msg: MSG) -> None:
        self._id = id
        self._msg_type = msg_type
        self._msg = msg

    @property
    def id(self) -> ID:
        return self._id

    @property
    def msg_type(self) -> MSG_TYPE:
        return self._msg_type

    @property
    def msg(self) -> MSG:
        return self._msg

    @abc.abstractmethod
    def row(self) -> t.Sequence[t.Any]:
        pass


class TextDetected(Detected[str, str, str]):
    def row(self) -> t.Tuple[str, str, str]:
        return (
            self.id,
            self.msg_type,
            self.msg,
        )

    def __repr__(self) -> str:
        return f"<TextDetected: {self.row()}>"
