import typing as t

from sqlalchemy.sql import text

from .datasources import DataSources, SQLAlchemyDataSource
from ._row import Row
from ._detected import Detected, ID, MSG, DETECTION_TYPE, TextDetected
from ._rule import Rule, SQLAlchemyRule
from ._detectiondata import DetectionData, TooManyDetectionException


class _DetectedType(t.Protocol, t.Generic[ID, DETECTION_TYPE, MSG]):
    def __call__(
        self, id: ID, level: int, detection_type: DETECTION_TYPE, msg: MSG
    ) -> Detected[ID, DETECTION_TYPE, MSG]: ...


def validate_db(
    *,
    rules: t.Collection[Rule[ID, DETECTION_TYPE, MSG]],
    detected: _DetectedType[ID, DETECTION_TYPE, MSG] = TextDetected,
    datasources: DataSources,
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
    datasources : DataSources
        datasources
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
            # TODO: ポリモーフィズムで一般の Rule で動くように
            if not isinstance(rule, SQLAlchemyRule):
                raise

            datasource = datasources[rule.datasource_name]
            if not isinstance(datasource, SQLAlchemyDataSource):
                # TODO: エラーメッセージ
                raise

            sql = text(rule.sql)
            for r in datasource.session.execute(sql):
                row = Row.from_sqlalchemy(r)
                detection_data.append(
                    detected(
                        rule.id_of_row(row),
                        rule.level(),
                        rule.detection_type(),
                        rule.message(row),
                    )
                )
    except TooManyDetectionException:
        pass

    return detection_data
