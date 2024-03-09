import typing as t

from sqlalchemy.orm import Session, scoped_session
from sqlalchemy.sql import text

from ._row import Row
from ._detected import Detected, ID, MSG, DETECTION_TYPE, TextDetected
from ._rule import Rule
from ._detectiondata import DetectionData, TooManyDetectionException


class _DetectedType(t.Protocol, t.Generic[ID, DETECTION_TYPE, MSG]):
    def __call__(
        self, id: ID, detection_type: DETECTION_TYPE, msg: MSG
    ) -> Detected[ID, DETECTION_TYPE, MSG]: ...


def validate_db(
    *,
    rules: t.Collection[Rule[ID, DETECTION_TYPE, MSG]],
    detected: _DetectedType[ID, DETECTION_TYPE, MSG] = TextDetected,
    session: t.Union[Session, scoped_session[Session]],
    max_detection: t.Optional[int] = None,
) -> DetectionData[ID, DETECTION_TYPE, MSG]:
    """Validate data in the database.

    Parameters
    ----------
    rules : Collection[Rule]
        the list of validation rules
    detected : Callable[[ID, DETECTION_TYPE, MSG], Detected]
        the constructor of Detected class;
        Typically, it is sufficient to specify the subclass itself of Detected.
    session : Session
        a session to the database
    max_detection : int, optional
        maximum number of detections.
        More detections than the specified number is ignored.
        If more incorrect data are detected than the specified number, flag `too_many_detection` of the result is set to True.

    Returns
    -------
    DetectionData
        the result data
    """
    detection_data: DetectionData[ID, DETECTION_TYPE, MSG] = DetectionData(
        max_detection=max_detection,
    )

    try:
        for rule in rules:
            sql = text(rule.sql)
            for r in session.execute(sql):
                row = Row(r)
                detection_data.append(
                    detected(
                        rule.id_of_row(row), rule.detection_type(), rule.message(row)
                    )
                )
    except TooManyDetectionException:
        pass

    return detection_data
