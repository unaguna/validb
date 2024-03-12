import abc
import typing as t

from .._detected import ID, MSG, DETECTION_TYPE, Detected
from .._detectiondata import DetectionData


class DetectionCsvMapping(abc.ABC):
    """mapper from detection to CSV row"""

    @abc.abstractmethod
    def row(self, detected: Detected[t.Any, t.Any, t.Any]) -> t.Sequence[t.Any]:
        """mapping from detection to CSV row

        Parameters
        ----------
        detected : Detected
            Anomalies detected

        Returns
        -------
        t.Sequence
            the row of CSV
        """
        ...

    def __call__(self, detected: Detected[t.Any, t.Any, t.Any]) -> t.Sequence[t.Any]:
        """mapping from detection to CSV row

        It is same to self.row().
        """
        return self.row(detected)

    def rows(
        self, detection_data: DetectionData[t.Any, t.Any, t.Any]
    ) -> t.Iterator[t.Sequence[t.Any]]:
        """map detections to CSV rows

        It uses self.row() for each detected anomaly contained in the specified DetectionData.

        The iterator returned by this function can be used directly for CSV output;
        such as `csv_writer.writerows(csv_mapping.rows(detection_data))`.

        Parameters
        ----------
        detection_data : DetectionData
            a DetectionData, which contains detected anomalies

        Returns
        -------
        t.Iterator[t.Sequence]
            an iterator of the CSV rows
        """
        return (self(detected) for detected in detection_data.values())


class SimpleDetectionCsvMapping(DetectionCsvMapping):
    def row(
        self, detected: Detected[ID, DETECTION_TYPE, MSG]
    ) -> t.Sequence[t.Union[str, int, None]]:
        return [
            detected.id_str,
            detected.level,
            detected.detection_type_str,
            detected.msg_str,
        ]
