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
from ..rules import SimpleSQLAlchemyRule, DEFAULT_LEVEL
from ._type import RulesFile


def load_rules_from_yaml(
    filepath: t.Union[str, bytes, pathlib.Path]
) -> t.Tuple[
    t.List[SimpleSQLAlchemyRule], DataSources, t.Optional[DetectionCsvMapping]
]:
    """Load validation rules from the YAML file.

    Parameters
    ----------
    filepath : str | bytes | Path
        filepath to the YAML file

    Returns
    -------
    list[Rule]
        the validation rules
    """
    import yaml

    with open(filepath, mode="r") as fp:
        rules: RulesFile = yaml.safe_load(fp)

    embedders: t.MutableMapping[str, Embedder] = {
        embedder_name: _construct_embedder(embedder_attr)
        for embedder_name, embedder_attr in rules.get("embedders", {}).items()
    }

    datasources: t.Mapping[str, DataSource] = {
        datasource_name: _construct_datasource(datasource_attr)
        for datasource_name, datasource_attr in rules.get("datasources", {}).items()
    }

    csvmappings: t.Mapping[str, DetectionCsvMapping] = {
        csvmapping_name: _construct_csvmapping(csvmapping_attr)
        for csvmapping_name, csvmapping_attr in rules.get("csvmappings", {}).items()
    }

    return (
        [
            SimpleSQLAlchemyRule(
                sql=rule["sql"],
                id_template=rule["id"],
                level=rule.get("level", DEFAULT_LEVEL),
                detection_type=rule["detection_type"],
                msg=rule["msg"],
                datasource=rule["datasource"],
                embedders=_construct_embedders(rule.get("embedders"), embedders),
            )
            for rule in rules.get("rules", [])
        ],
        DataSources(datasources),
        csvmappings.get("detected"),
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


def _construct_embedders(
    embedders: t.Optional[t.Sequence[str]], embedder_instances: t.Mapping[str, Embedder]
) -> t.Optional[t.Sequence[Embedder]]:
    if embedders is None:
        return None

    return [embedder_instances[embedder_name] for embedder_name in embedders]


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
