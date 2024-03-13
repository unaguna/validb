import abc
import typing as t

import sqlalchemy


class EmbeddedVariablesExtender(abc.ABC):
    @abc.abstractmethod
    def extend(
        self, vars_seq: t.Sequence[t.Any], vars_map: t.Mapping[str, t.Any]
    ) -> t.Mapping[str, t.Any]: ...


class EmbeddedVariables:
    _sequence: t.Sequence[t.Any]
    _mapping: t.Mapping[str, t.Any]

    def __init__(self, seq: t.Sequence[t.Any], mapping: t.Mapping[str, t.Any]):
        self._sequence = seq
        self._mapping = mapping

    @classmethod
    def from_sqlalchemy(cls, row: sqlalchemy.Row[t.Any]) -> "EmbeddedVariables":
        return EmbeddedVariables(
            row,
            row._mapping,  # type: ignore
        )

    def __len__(self) -> int:
        return len(self._sequence)

    def __getitem__(self, key: t.Union[int, str]) -> t.Any:
        if isinstance(key, str):
            return self._mapping[key]
        else:
            return self._sequence[key]

    def get(self, key: t.Union[int, str], default: t.Any = None) -> t.Any:
        if isinstance(key, str):
            return self._mapping.get(key, default)
        else:
            if 0 <= key < len(self._sequence):
                return self._sequence[key]
            else:
                return default

    @property
    def sequence(self) -> t.Sequence[t.Any]:
        return self._sequence

    @property
    def mapping(self) -> t.Mapping[str, t.Any]:
        return self._mapping

    def extended(
        self,
        extender: t.Union[
            t.Iterable[EmbeddedVariablesExtender], EmbeddedVariablesExtender
        ],
    ) -> "EmbeddedVariables":
        """Returns variables extended by applying the specified extenders.

        This method is non-destructive and creates a new instance that is different from self.

        Parameters
        ----------
        extender : Iterator[EmbeddedVariablesExtender] | EmbeddedVariablesExtender
            extenders

        Returns
        -------
        EmbeddedVariables
            variables extended by applying the specified extenders
        """
        if not isinstance(extender, t.Iterable):
            return self.extended([extender])

        current_vars_map = self.mapping
        for ex in extender:
            current_vars_map = ex.extend(self.sequence, current_vars_map)

        return EmbeddedVariables(self.sequence, current_vars_map)
