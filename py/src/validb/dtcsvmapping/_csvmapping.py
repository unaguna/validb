import abc
import typing as t

from .._detected import ID, MSG, DETECTION_TYPE, Detected
from .._detectiondata import DetectionData


class DetectionCsvMapping(t.Generic[ID, DETECTION_TYPE, MSG], abc.ABC):
    @abc.abstractmethod
    def row(self, detected: Detected[ID, DETECTION_TYPE, MSG]) -> t.Sequence[t.Any]: ...

    def __call__(
        self, detected: Detected[ID, DETECTION_TYPE, MSG]
    ) -> t.Sequence[t.Any]:
        return self.row(detected)

    def rows(
        self, detection_data: DetectionData[ID, DETECTION_TYPE, MSG]
    ) -> t.Iterator[t.Sequence[t.Any]]:
        return (self(detected) for detected in detection_data.values())


class SimpleDetectionCsvMapping(
    DetectionCsvMapping[ID, DETECTION_TYPE, MSG], t.Generic[ID, DETECTION_TYPE, MSG]
):
    def row(
        self, detected: Detected[ID, DETECTION_TYPE, MSG]
    ) -> t.Sequence[t.Union[str, int]]:
        return [
            detected.id_str,
            detected.level,
            detected.detection_type_str,
            detected.msg_str,
        ]
