import pathlib
import typing as t

from .._classloader import (
    construct_imported_dinamically,
    IllegalPathError,
    NonClassLoadedError,
    UnexpectedClassLoadedError,
)
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
        name: _construct_embedder(attr)
        for name, attr in config_dict.get("embedders", {}).items()
    }

    datasources: t.Mapping[str, DataSource] = {
        name: _construct_datasource(attr)
        for name, attr in config_dict.get("datasources", {}).items()
    }

    csvmappings: t.Mapping[str, DetectionCsvMapping] = {
        name: _construct_csvmapping(attr)
        for name, attr in config_dict.get("csvmappings", {}).items()
    }

    return Config(
        rules=[_construct_rule(rule) for rule in config_dict.get("rules", [])],
        datasources=DataSources(datasources),
        detected_csvmapping=csvmappings.get("detected"),
        embedders=embedders,
    )


def _construct_rule(rule_attr: t.Mapping[str, t.Any]) -> Rule[t.Any, t.Any, t.Any]:
    try:
        return construct_imported_dinamically(
            rule_attr,
            Rule,  # type: ignore
        )
    except IllegalPathError as e:
        raise ValueError(
            f"rules.*.class must be a string like 'module.class'; actually specified path: {e.actual_path}"
        )
    except (UnexpectedClassLoadedError, NonClassLoadedError) as e:
        raise TypeError(
            f"rule must be instance of {Rule.__name__}; actual loaded: {e.actual_loaded}"
        )


def _construct_embedder(embedder_attr: t.Mapping[str, t.Any]) -> Embedder:
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


def _construct_datasource(datasource_attr: t.Mapping[str, t.Any]) -> DataSource:
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


def _construct_csvmapping(
    csvmapping_attr: t.Mapping[str, t.Any]
) -> DetectionCsvMapping:
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
