import typing as t

import sqlalchemy

from ._embedder import Embedder


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

    def extended(self, embedder: t.Union[t.Sequence[Embedder], Embedder]) -> "Row":
        """Returns a Row extended by applying the specified variable generators.

        This method is non-destructive and creates a new instance that is different from self.

        Parameters
        ----------
        embedder : Sequence[Embedder] | Embedder
            variable generators

        Returns
        -------
        Row
            a Row extended by applying the specified variable generators
        """
        if not isinstance(embedder, t.Sequence):
            return self.extended([embedder])

        current_kw_vars = self.mapping
        for em in embedder:
            current_kw_vars = em.extend(self.sequence, current_kw_vars)

        return Row(self.sequence, current_kw_vars)
