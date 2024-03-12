from collections import defaultdict
from itertools import chain
import typing as t

from ._detected import Detected


ID = t.TypeVar("ID")
DETECTION_TYPE = t.TypeVar("DETECTION_TYPE")
MSG = t.TypeVar("MSG")


class TooManyDetectionException(Exception):
    """An exception thrown when more anomalies are detected than the initially specified number.

    Normally, there is no need to be aware of the existence of this exception,
    since it is caught inside validb.
    """

    pass


class DetectionData(t.Generic[ID, DETECTION_TYPE, MSG]):
    """Result data of DB validation"""

    _append_cnt: int
    _max_detection: int
    _too_many_detection_flag: bool
    _by_id: t.MutableMapping[ID, t.List[Detected[ID, DETECTION_TYPE, MSG]]]
    _by_detection_type: t.MutableMapping[
        DETECTION_TYPE, t.List[Detected[ID, DETECTION_TYPE, MSG]]
    ]
    _by_level_detection_type: t.MutableMapping[
        int, t.MutableMapping[DETECTION_TYPE, t.List[Detected[ID, DETECTION_TYPE, MSG]]]
    ]

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
        self._by_detection_type = defaultdict(lambda: [])
        self._by_level_detection_type = defaultdict(lambda: defaultdict(lambda: []))

    def append(self, detected: Detected[ID, DETECTION_TYPE, MSG]):
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
        self._by_detection_type[detected.detection_type].append(detected)
        self._by_level_detection_type[detected.level][detected.detection_type].append(
            detected
        )

    def extend(self, detecteds: t.Iterable[Detected[ID, DETECTION_TYPE, MSG]]):
        """append detecteds anomaly

        Normally, this function is used only inside validb.

        Parameters
        ----------
        detecteds : Iterable[Detected]
            iterator of detected anomaly

        Raises
        ------
        TooManyDetectionException
            If the maximum number of detections specified at the time of instance creation is exceeded.
        """
        for detected in detecteds:
            self.append(detected)

    def ids(self) -> t.Iterable[ID]:
        """create the iterator of IDs of records for which anomalies were detected.

        The record ID used here is obtained by the method specified in the Rule.

        Returns
        -------
        Iterable[ID]
            the iterator of IDs of records for which anomalies were detected.
        """
        return self._by_id.keys()

    def detection_types(self) -> t.Iterable[DETECTION_TYPE]:
        """create the iterator of detection types for which anomalies were detected."""
        return self._by_detection_type.keys()

    def levels_detection_types(self) -> t.Iterable[t.Tuple[int, DETECTION_TYPE]]:
        """create the iterator of tupels of levels and detection types for which anomalies were detected.

        It will be sorted by level.
        """
        return (
            (level, detection_type)
            for level in sorted(self._by_level_detection_type.keys(), reverse=True)
            for detection_type in self._by_level_detection_type[level].keys()
        )

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

    def __getitem__(self, key: t.Any) -> t.Sequence[Detected[ID, DETECTION_TYPE, MSG]]:
        if key in self._by_id:
            return self._by_id[key]
        if key in self._by_detection_type:
            return self._by_detection_type[key]

        if isinstance(key, t.Sized) and len(key) == 2 and isinstance(key, t.Sequence):
            key_level: t.Any = key[0]
            key_dt_type: t.Any = key[1]

            if key_level in self._by_level_detection_type:
                of_level_by_detection_type = self._by_level_detection_type[key_level]
                if key_dt_type in of_level_by_detection_type:
                    return self._by_level_detection_type[key_level][key_dt_type]

        raise KeyError(key)  # type: ignore

    def values(self) -> t.Generator[Detected[ID, DETECTION_TYPE, MSG], None, None]:
        """create the iterator of detection"""
        return (detected for detected in chain(*self._by_id.values()))
