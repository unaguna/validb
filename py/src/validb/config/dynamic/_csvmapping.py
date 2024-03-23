import typing as t

from ..._classloader import (
    construct_imported_dinamically,
    IllegalPathError,
    NonClassLoadedError,
    UnexpectedClassLoadedError,
)
from ...csvmapping import DetectionCsvMapping


def construct_csvmapping(csvmapping_attr: t.Mapping[str, t.Any]) -> DetectionCsvMapping:
    try:
        return construct_imported_dinamically(
            csvmapping_attr,
            DetectionCsvMapping,
        )
    except IllegalPathError as e:
        raise ValueError(
            f"csvmapping.*.class must be a string like 'module.class'; actually specified path: {e.actual_path}"
        )
    except (UnexpectedClassLoadedError, NonClassLoadedError) as e:
        raise TypeError(
            f"csvmapping must be instance of {DetectionCsvMapping.__name__}; actual loaded: {e.actual_loaded}"
        )
