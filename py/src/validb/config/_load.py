import pathlib
import typing as t

from .._classloader import (
    import_class_dinamically,
    IllegalPathError,
    UnexpectedClassLoadedError,
)
from ..datasources import DataSource, DataSources
from .._embedder import Embedder
from ..rules import SimpleSQLAlchemyRule, DEFAULT_LEVEL
from ._type import RulesFile


def load_rules_from_yaml(
    filepath: t.Union[str, bytes, pathlib.Path]
) -> t.Tuple[t.List[SimpleSQLAlchemyRule], DataSources]:
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

    return [
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
    ], DataSources(datasources)


def _construct_embedder(embedder_attr: t.Mapping[str, t.Any]) -> Embedder:
    embedder_class = _import_embedder(embedder_attr["class"])
    embedder = embedder_class(
        **{key: value for key, value in embedder_attr.items() if key != "class"}
    )
    return embedder


def _import_embedder(path: t.Any) -> t.Type[Embedder]:
    try:
        embedder_class = import_class_dinamically(
            path,
            expected_class=Embedder,
        )
    except IllegalPathError:
        raise ValueError("embedders.*.class must be a string like 'module.class'")
    except UnexpectedClassLoadedError:
        raise TypeError(f"embedder must be instance of {Embedder.__name__}")

    return embedder_class


def _construct_embedders(
    embedders: t.Optional[t.Sequence[str]], embedder_instances: t.Mapping[str, Embedder]
) -> t.Optional[t.Sequence[Embedder]]:
    if embedders is None:
        return None

    return [embedder_instances[embedder_name] for embedder_name in embedders]


def _construct_datasource(datasource_attr: t.Mapping[str, t.Any]) -> DataSource:
    datasource_class = _import_datasource(datasource_attr["class"])
    datasource = datasource_class(
        **{key: value for key, value in datasource_attr.items() if key != "class"}
    )
    return datasource


def _import_datasource(path: t.Any) -> t.Type[DataSource]:
    try:
        datasource_class = import_class_dinamically(
            path,
            expected_class=DataSource,
        )
    except IllegalPathError:
        raise ValueError("datasources.*.class must be a string like 'module.class'")
    except UnexpectedClassLoadedError:
        raise TypeError(f"datasource must be instance of {DataSource.__name__}")

    return datasource_class
