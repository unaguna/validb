import abc
import typing as t

from ._embedded_vars import EmbeddedVariables


ID = t.TypeVar("ID")
DETECTION_TYPE = t.TypeVar("DETECTION_TYPE")
MSG = t.TypeVar("MSG")


class Detected(t.Generic[ID, DETECTION_TYPE, MSG], abc.ABC):
    """detected anomaly"""

    _id: ID
    _level: int
    _detection_type: DETECTION_TYPE
    _msg: MSG
    _embedded_vars: EmbeddedVariables

    def __init__(
        self,
        id: ID,
        level: int,
        detection_type: DETECTION_TYPE,
        msg: MSG,
        embedded_vars: EmbeddedVariables,
    ) -> None:
        """create detection object

        Parameters
        ----------
        id : ID
            The record ID of the record for which the abnormality was detected.
            Normally, record IDs are determined according to predefined rules.
        level: int
            the level of detection;
            The higher the number, the more serious the detection is treated as.
        detection_type : DETECTION_TYPE
            Type of anomaly detected.
        msg : MSG
            The message.
        embedded_vars : EmbeddedVariables
            variables embedded while the detection
        """
        self._id = id
        self._level = level
        self._detection_type = detection_type
        self._msg = msg
        self._embedded_vars = embedded_vars

    @property
    def id(self) -> ID:
        """The record ID of the record for which the abnormality was detected."""
        return self._id

    @property
    def id_str(self) -> t.Optional[str]:
        """str expression of `self.id`

        Use when string representation is required, such as in CSV output.
        """
        id_ = self._id
        return str(id_) if id_ is not None else None

    @property
    def level(self) -> int:
        """Level of detection.

        The higher the number, the more serious the detection is treated as.
        """
        return self._level

    @property
    def detection_type(self) -> DETECTION_TYPE:
        """Type of anomaly detected."""
        return self._detection_type

    @property
    def detection_type_str(self) -> t.Optional[str]:
        """str expression of `self.detection_type`

        Use when string representation is required, such as in CSV output.
        """
        detection_type = self.detection_type
        return str(detection_type) if detection_type is not None else None

    @property
    def msg(self) -> MSG:
        """The message"""
        return self._msg

    @property
    def msg_str(self) -> t.Optional[str]:
        """str expression of `self.msg`

        Use when string representation is required, such as in CSV output.
        """
        msg = self.msg
        return str(msg) if msg is not None else None

    @property
    def embedded_vars(self) -> EmbeddedVariables:
        """variables embedded while detection"""
        return self._embedded_vars


class TextDetected(Detected[str, str, str]):
    def __repr__(self) -> str:
        return (
            f"<TextDetected: {self.id_str}, {self.detection_type_str}, {self.msg_str}>"
        )


class DetectedType(t.Protocol, t.Generic[ID, DETECTION_TYPE, MSG]):
    def __call__(
        self,
        id: ID,
        level: int,
        detection_type: DETECTION_TYPE,
        msg: MSG,
        embedded_vars: EmbeddedVariables,
    ) -> Detected[ID, DETECTION_TYPE, MSG]: ...
