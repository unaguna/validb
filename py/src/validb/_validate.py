import typing as t


from .datasources import DataSources
from ._detected import DetectedType, ID, MSG, DETECTION_TYPE, TextDetected
from ._detectiondata import DetectionData, TooManyDetectionException
from .rules import Rule


def validate_db(
    *,
    rules: t.Collection[Rule[ID, DETECTION_TYPE, MSG]],
    detected: DetectedType[ID, DETECTION_TYPE, MSG] = TextDetected,
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
        for rule in sorted(rules, key=lambda r: r.level(), reverse=True):
            detected_list = rule.exec(datasources=datasources, detected=detected)
            detection_data.extend(detected_list)
    except TooManyDetectionException:
        pass

    return detection_data
