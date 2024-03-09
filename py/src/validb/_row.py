import abc
import typing as t

import sqlalchemy


class RowExtender(abc.ABC):
    @abc.abstractmethod
    def extend(
        self, vars: t.Sequence[t.Any], kw_vars: t.Mapping[str, t.Any]
    ) -> t.Mapping[str, t.Any]: ...


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

    def extended(
        self, extender: t.Union[t.Sequence[RowExtender], RowExtender]
    ) -> "Row":
        """Returns a Row extended by applying the specified extenders.

        This method is non-destructive and creates a new instance that is different from self.

        Parameters
        ----------
        extender : Sequence[RowExtender] | RowExtender
            extenders

        Returns
        -------
        Row
            a Row extended by applying the specified extenders
        """
        if not isinstance(extender, t.Sequence):
            return self.extended([extender])

        current_kw_vars = self.mapping
        for ex in extender:
            current_kw_vars = ex.extend(self.sequence, current_kw_vars)

        return Row(self.sequence, current_kw_vars)
