import pathlib
import typing as t

from ..csvmapping import DetectionCsvMapping
from ..datasources import DataSource, DataSources
from .._embedder import Embedder
from ._type import ConfigFile
from ._config import Config
from .dynamic import (
    construct_csvmapping,
    construct_datasource,
    construct_embedder,
    construct_rule,
)


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
        name: construct_embedder(attr)
        for name, attr in config_dict.get("embedders", {}).items()
    }

    datasources: t.Mapping[str, DataSource] = {
        name: construct_datasource(attr)
        for name, attr in config_dict.get("datasources", {}).items()
    }

    csvmappings: t.Mapping[str, DetectionCsvMapping] = {
        name: construct_csvmapping(attr)
        for name, attr in config_dict.get("csvmappings", {}).items()
    }

    return Config(
        rules=[construct_rule(rule) for rule in config_dict.get("rules", [])],
        datasources=DataSources(datasources),
        detected_csvmapping=csvmappings.get("detected"),
        embedders=embedders,
    )
