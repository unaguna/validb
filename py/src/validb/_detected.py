import abc
import typing as t


ID = t.TypeVar("ID")
DETECTION_TYPE = t.TypeVar("DETECTION_TYPE")
MSG = t.TypeVar("MSG")


class Detected(t.Generic[ID, DETECTION_TYPE, MSG], abc.ABC):
    """detected anomaly"""

    _id: ID
    _detection_type: DETECTION_TYPE
    _msg: MSG

    def __init__(self, id: ID, detection_type: DETECTION_TYPE, msg: MSG) -> None:
        """create detection object

        Parameters
        ----------
        id : ID
            The record ID of the record for which the abnormality was detected.
            Normally, record IDs are determined according to predefined rules.
        detection_type : DETECTION_TYPE
            Type of anomaly detected.
        msg : MSG
            The message.
        """
        self._id = id
        self._detection_type = detection_type
        self._msg = msg

    @property
    def id(self) -> ID:
        """The record ID of the record for which the abnormality was detected."""
        return self._id

    @property
    def detection_type(self) -> DETECTION_TYPE:
        """Type of anomaly detected."""
        return self._detection_type

    @property
    def msg(self) -> MSG:
        """The message"""
        return self._msg

    @abc.abstractmethod
    def row(self) -> t.Sequence[t.Any]:
        pass


class TextDetected(Detected[str, str, str]):
    def row(self) -> t.Tuple[str, str, str]:
        return (
            self.id,
            self.detection_type,
            self.msg,
        )

    def __repr__(self) -> str:
        return f"<TextDetected: {self.row()}>"
