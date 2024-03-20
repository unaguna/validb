from dataclasses import dataclass
import typing as t

from .._detected import ID, MSG, DETECTION_TYPE
from ..rules import Rule
from ..datasources import DataSources
from ..csvmapping import DetectionCsvMapping


@dataclass
class Config(t.Generic[ID, DETECTION_TYPE, MSG]):
    """Configuration for validating"""

    rules: t.Sequence[Rule[ID, DETECTION_TYPE, MSG]]
    datasources: DataSources
    detected_csvmapping: t.Optional[DetectionCsvMapping]
