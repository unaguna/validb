import typing as t

from ..._classloader import construct_imported_dinamically
from ...datasources import DataSource


def construct_datasource(datasource_attr: t.Mapping[str, t.Any]) -> DataSource:
    return construct_imported_dinamically(
        datasource_attr,
        DataSource,
    )
