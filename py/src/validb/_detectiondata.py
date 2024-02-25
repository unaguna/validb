from collections import defaultdict
from itertools import chain
import typing as t

from ._detected import Detected


ID = t.TypeVar("ID")
MSG_TYPE = t.TypeVar("MSG_TYPE")
MSG = t.TypeVar("MSG")


class TooManyDetectionException(Exception):
    """An exception thrown when more anomalies are detected than the initially specified number.

    Normally, there is no need to be aware of the existence of this exception,
    since it is caught inside validb.
    """

    pass


class DetectionData(t.Generic[ID, MSG_TYPE, MSG]):
    """Result data of DB validation"""

    _append_cnt: int
    _max_detection: int
    _too_many_detection_flag: bool
    _by_id: t.MutableMapping[ID, t.List[Detected[ID, MSG_TYPE, MSG]]]
    _by_msg_type: t.MutableMapping[MSG_TYPE, t.List[Detected[ID, MSG_TYPE, MSG]]]

    def __init__(self, max_detection: t.Optional[int]) -> None:
        """Initialize object

        Parameters
        ----------
        max_detection : int | None
            the maximum number of detections;
            An exception will be raised when an attempt is made to register a detection that exceeds this number.
        """
        self._max_detection = max_detection if max_detection is not None else 1 << 31
        self._append_cnt = 0
        self._too_many_detection_flag = False
        self._by_id = defaultdict(lambda: [])
        self._by_msg_type = defaultdict(lambda: [])

    def append(self, detected: Detected[ID, MSG_TYPE, MSG]):
        """append a detected anomaly

        Normally, this function is used only inside validb.

        Parameters
        ----------
        detected : Detected
            detected anomaly

        Raises
        ------
        TooManyDetectionException
            If the maximum number of detections specified at the time of instance creation is exceeded.
        """
        if self._append_cnt >= self._max_detection:
            self._too_many_detection_flag = True
            raise TooManyDetectionException()
        self._append_cnt += 1

        self._by_id[detected.id].append(detected)
        self._by_msg_type[detected.msg_type].append(detected)

    def ids(self) -> t.Iterable[ID]:
        """create the iterator of IDs of records for which anomalies were detected.

        The record ID used here is obtained by the method specified in the Rule.

        Returns
        -------
        Iterable[ID]
            the iterator of IDs of records for which anomalies were detected.
        """
        return self._by_id.keys()

    def msg_types(self) -> t.Iterable[MSG_TYPE]:
        """create the iterator of message types for which anomalies were detected."""
        return self._by_msg_type.keys()

    @property
    def count(self) -> int:
        """Number of anomalies detected"""
        return self._append_cnt

    @property
    def too_many_detection(self) -> bool:
        """Whether the number of detections exceeds the initially specified maximum number of detections

        This value of true means that anomalies exceeding the maximum number of
        detections are ignored and not included in this result object either.
        """
        return self._too_many_detection_flag

    def __getitem__(self, key: t.Any) -> t.Sequence[Detected[ID, MSG_TYPE, MSG]]:
        if key in self._by_id:
            return self._by_id[key]
        elif key in self._by_msg_type:
            return self._by_msg_type[key]
        else:
            raise KeyError(key)

    def values(self) -> t.Generator[Detected[ID, MSG_TYPE, MSG], None, None]:
        """create the iterator of detection"""
        return (detected for detected in chain(*self._by_id.values()))

    def rows(self) -> t.Generator[t.Sequence[t.Any], None, None]:
        """create the iterator of rows for CSV

        One row generated corresponds to one detection.

        By specifying this iterator as an argument to `csv.writer.writerows`,
        the detected anomalies can be output in CSV format.

        Returns
        -------
        t.Generator[t.Sequence[t.Any], None, None]
            the iterator of rows for CSV
        """
        return (detected.row() for detected in self.values())
