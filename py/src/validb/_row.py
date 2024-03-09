import typing as t

import sqlalchemy


class Row:
    _row: t.Sequence[t.Any]
    _row_mapping: t.Mapping[str, t.Any]

    def __init__(self, seq: t.Sequence[t.Any], mapping: t.Mapping[str, t.Any]):
        self._row = seq
        self._row_mapping = mapping

    @classmethod
    def from_sqlalchemy(cls, row: sqlalchemy.Row[t.Any]) -> "Row":
        return Row(
            row,
            row._mapping,  # type: ignore
        )

    def __len__(self) -> int:
        return len(self._row)

    def __getitem__(self, key: t.Union[int, str]) -> t.Any:
        if isinstance(key, str):
            return self._row_mapping[key]
        else:
            return self._row[key]

    @property
    def sequence(self) -> t.Sequence[t.Any]:
        return self._row

    @property
    def mapping(self) -> t.Mapping[str, t.Any]:
        return self._row_mapping
