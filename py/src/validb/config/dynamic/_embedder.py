import typing as t

from ..._classloader import construct_imported_dinamically
from ..._embedder import Embedder


def construct_embedder(embedder_attr: t.Mapping[str, t.Any]) -> Embedder:
    return construct_imported_dinamically(
        embedder_attr,
        Embedder,
    )
