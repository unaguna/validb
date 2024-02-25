from collections import defaultdict
from itertools import chain
import typing as t

from ._detected import Detected


ID = t.TypeVar("ID")
MSG_TYPE = t.TypeVar("MSG_TYPE")
MSG = t.TypeVar("MSG")


class DetectionData(t.Generic[ID, MSG_TYPE, MSG]):
    _by_id: t.MutableMapping[ID, t.List[Detected[ID, MSG_TYPE, MSG]]]
    _by_msg_type: t.MutableMapping[MSG_TYPE, t.List[Detected[ID, MSG_TYPE, MSG]]]

    def __init__(self) -> None:
        self._by_id = defaultdict(lambda: [])
        self._by_msg_type = defaultdict(lambda: [])

    def append(self, detected: Detected[ID, MSG_TYPE, MSG]):
        self._by_id[detected.id].append(detected)
        self._by_msg_type[detected.msg_type].append(detected)

    def ids(self) -> t.Iterable[ID]:
        return self._by_id.keys()

    def msg_types(self) -> t.Iterable[MSG_TYPE]:
        return self._by_msg_type.keys()

    def __getitem__(self, key: t.Any) -> t.Sequence[Detected[ID, MSG_TYPE, MSG]]:
        if key in self._by_id:
            return self._by_id[key]
        elif key in self._by_msg_type:
            return self._by_msg_type[key]
        else:
            raise KeyError(key)

    def values(self) -> t.Generator[Detected[ID, MSG_TYPE, MSG], None, None]:
        return (detected for detected in chain(*self._by_id.values()))

    def rows(self) -> t.Generator[t.Sequence[t.Any], None, None]:
        return (detected.row() for detected in self.values())
