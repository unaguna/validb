import typing as t

from ..._classloader import (
    construct_imported_dinamically,
    IllegalPathError,
    NonClassLoadedError,
    UnexpectedClassLoadedError,
)
from ..._embedder import Embedder


def construct_embedder(embedder_attr: t.Mapping[str, t.Any]) -> Embedder:
    try:
        return construct_imported_dinamically(
            embedder_attr,
            Embedder,
        )
    except IllegalPathError as e:
        raise ValueError(
            f"embedders.*.class must be a string like 'module.class'; actually specified path: {e.actual_path}"
        )
    except (UnexpectedClassLoadedError, NonClassLoadedError) as e:
        raise TypeError(
            f"embedder must be instance of {Embedder.__name__}; actual loaded: {e.actual_loaded}"
        )
