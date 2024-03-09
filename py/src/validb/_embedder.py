import abc
import typing as t

from ._row import RowExtender


class Embedder(RowExtender, abc.ABC):
    """Embedding Variable Generator"""

    def extend(
        self, vars: t.Sequence[t.Any], kw_vars: t.Mapping[str, t.Any]
    ) -> t.Mapping[str, t.Any]:
        """generate embedding variables

        It is executed in the process of preparing variables for embedding.
        It takes a variables in the process of creation as an argument and
        returns an object to which the variables has been added based on the variables.

        Parameters
        ----------
        vars : t.Sequence[t.Any]
            position variables in the process of variable generation.
        kw_vars : t.Mapping[str, t.Any]
            keyword variables in the process of variable generation.

        Returns
        -------
        t.Mapping[str, t.Any]
            generated keyword variables;
            It is usually a dictionary with some fields added to the argument `kw_vars`.
        """
        return kw_vars
