import datetime as dt
import typing as t

from validb import Embedder, DetectionCsvMapping, Detected


class TodayEmbedder(Embedder):
    _key_name: str
    _shift: dt.timedelta

    def __init__(self, *, key_name: str = "today", shift: int = 0) -> None:
        self._key_name = key_name
        self._shift = dt.timedelta(days=shift)

    def extend(
        self, vars: t.Sequence[t.Any], kw_vars: t.Mapping[str, t.Any]
    ) -> t.Mapping[str, t.Any]:
        return {
            **kw_vars,
            self._key_name: dt.date.today() + self._shift,
        }


class MyDetectionCsvMapping(DetectionCsvMapping):
    def row(self, detected: Detected[t.Any, t.Any, t.Any]) -> t.Sequence[t.Any]:
        return [
            "!",
            detected.id_str,
            detected.level,
            detected.detection_type_str,
            detected.msg_str,
        ]
