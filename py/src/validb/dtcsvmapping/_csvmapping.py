import abc
import typing as t

from .._detected import ID, MSG, DETECTION_TYPE, Detected


class DetectionCsvMapping(t.Generic[ID, DETECTION_TYPE, MSG], abc.ABC):
    @abc.abstractmethod
    def row(self, detected: Detected[ID, DETECTION_TYPE, MSG]) -> t.Sequence[t.Any]: ...

    def __call__(
        self, detected: Detected[ID, DETECTION_TYPE, MSG]
    ) -> t.Sequence[t.Any]:
        return self.row(detected)


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
