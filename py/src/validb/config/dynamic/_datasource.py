import typing as t

from ..._classloader import (
    construct_imported_dinamically,
    IllegalPathError,
    NonClassLoadedError,
    UnexpectedClassLoadedError,
)
from ...datasources import DataSource


def construct_datasource(datasource_attr: t.Mapping[str, t.Any]) -> DataSource:
    try:
        return construct_imported_dinamically(
            datasource_attr,
            DataSource,
        )
    except IllegalPathError as e:
        raise ValueError(
            f"datasources.*.class must be a string like 'module.class'; actually specified path: {e.actual_path}"
        )
    except (UnexpectedClassLoadedError, NonClassLoadedError) as e:
        raise TypeError(
            f"datasource must be instance of {DataSource.__name__}; actual loaded: {e.actual_loaded}"
        )
