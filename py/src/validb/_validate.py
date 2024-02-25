import typing as t

from sqlalchemy.orm import Session, scoped_session
from sqlalchemy.sql import text

from ._detected import Detected, ID, MSG, MSG_TYPE
from ._rule import Rule
from ._detectiondata import DetectionData, TooManyDetectionException


def validate_db(
    *,
    rules: t.Collection[Rule[ID, MSG_TYPE, MSG]],
    detected: t.Callable[[ID, MSG_TYPE, MSG], Detected[ID, MSG_TYPE, MSG]],
    session: t.Union[Session, scoped_session[Session]],
    max_detection: t.Optional[int] = None,
) -> DetectionData[ID, MSG_TYPE, MSG]:
    detection_data: DetectionData[ID, MSG_TYPE, MSG] = DetectionData(
        max_detection=max_detection,
    )

    try:
        for rule in rules:
            sql = text(rule.sql)
            for r in session.execute(sql):
                msg_type, msg = rule.detected()
                detection_data.append(detected(rule.id_of_row(r), msg_type, msg))
    except TooManyDetectionException:
        pass

    return detection_data
