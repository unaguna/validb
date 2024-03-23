import pathlib
import typing as t

from .._classloader import construct_imported_dinamically
from ..csvmapping import DetectionCsvMapping
from ..datasources import DataSource, DataSources
from .._embedder import Embedder
from ..rules import Rule
from ._type import ConfigFile
from ._config import Config


def load_config(filepath: t.Union[str, bytes, pathlib.Path]) -> Config[str, str, str]:
    """Load validation config from the YAML file.

    Parameters
    ----------
    filepath : str | bytes | Path
        filepath to the YAML file

    Returns
    -------
    Config
        the configuration of validation
    """
    import yaml

    with open(filepath, mode="r") as fp:
        config_dict: ConfigFile = yaml.safe_load(fp)

    embedders: t.MutableMapping[str, Embedder] = {
        name: parse_object(attr, f"embedders.{name}", Embedder)
        for name, attr in config_dict.get("embedders", {}).items()
    }

    datasources: t.Mapping[str, DataSource] = {
        name: parse_object(attr, f"datasources.{name}", DataSource)
        for name, attr in config_dict.get("datasources", {}).items()
    }

    csvmappings: t.Mapping[str, DetectionCsvMapping] = {
        name: parse_object(attr, f"csvmappings.{name}", DetectionCsvMapping)
        for name, attr in config_dict.get("csvmappings", {}).items()
    }

    return Config(
        rules=[
            parse_object(attr, f"rules.{index}", Rule)  # type: ignore
            for index, attr in enumerate(config_dict.get("rules", []))
        ],
        datasources=DataSources(datasources),
        detected_csvmapping=csvmappings.get("detected"),
        embedders=embedders,
    )


_T = t.TypeVar("_T")


def parse_object(
    attr: t.Mapping[str, t.Any], path: str, expected_class: t.Type[_T]
) -> _T:
    try:
        return construct_imported_dinamically(attr, expected_class=expected_class)
    except Exception as e:
        raise ParseObjectException(path) from e


class ParseObjectException(Exception):
    def __init__(self, object_path: str) -> None:
        super().__init__(f"failed to parse object {object_path}")
