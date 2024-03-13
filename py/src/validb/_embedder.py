import abc
import typing as t

from ._embedded_vars import EmbeddedVariablesExtender


class Embedder(EmbeddedVariablesExtender, abc.ABC):
    """Embedding Variable Generator"""

    def extend(
        self, vars_seq: t.Sequence[t.Any], vars_map: t.Mapping[str, t.Any]
    ) -> t.Mapping[str, t.Any]:
        """generate embedding variables

        It is executed in the process of preparing variables for embedding.
        It takes a variables in the process of creation as an argument and
        returns an object to which the variables has been added based on the variables.

        Parameters
        ----------
        vars_seq : Sequence[Any]
            position variables in the process of variable generation.
        vars_map : Mapping[str, Any]
            keyword variables in the process of variable generation.

        Returns
        -------
        t.Mapping[str, Any]
            generated keyword variables;
            It is usually a dictionary with some fields added to the argument `vars_map`.
        """
        return vars_map
