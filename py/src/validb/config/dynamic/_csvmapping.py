import typing as t

from ..._classloader import construct_imported_dinamically
from ...csvmapping import DetectionCsvMapping


def construct_csvmapping(csvmapping_attr: t.Mapping[str, t.Any]) -> DetectionCsvMapping:
    return construct_imported_dinamically(
        csvmapping_attr,
        DetectionCsvMapping,
    )
