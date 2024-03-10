import importlib
import pathlib
import typing as t

from ..datasources import DataSource, DataSources
from .._embedder import Embedder
from .._rule import SimpleSQLAlchemyRule, DEFAULT_LEVEL


class RuleDefRequired(t.TypedDict):
    sql: str
    id: str
    detection_type: str
    msg: str
    datasource: str


class RuleDef(RuleDefRequired, total=False):
    level: int
    embedders: t.List[str]


class RulesFile(t.TypedDict):
    rules: t.Sequence[RuleDef]
    embedders: t.Mapping[str, t.Any]
    datasources: t.Mapping[str, t.Any]


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
        for embedder_name, embedder_attr in rules["embedders"].items()
    }

    datasources: t.Mapping[str, DataSource] = {
        datasource_name: _construct_datasource(datasource_attr)
        for datasource_name, datasource_attr in rules["datasources"].items()
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
        for rule in rules["rules"]
    ], DataSources(datasources)


def _construct_embedder(embedder_attr: t.Mapping[str, t.Any]) -> Embedder:
    embedder_class = _import_embedder(embedder_attr["class"])
    embedder = embedder_class(
        **{key: value for key, value in embedder_attr.items() if key != "class"}
    )
    return embedder


def _import_embedder(path: t.Any) -> t.Type[Embedder]:
    if not isinstance(path, str):
        raise ValueError("embedders.*.class must be a string like 'module.class'")

    embedder_path = path.split(".")
    if len(embedder_path) < 2:
        raise ValueError("embedders.*.class must be a string like 'module.class'")

    embedder_module_str = ".".join(embedder_path[:-1])
    embedder_class_name = embedder_path[-1]
    embedder_module = importlib.import_module(embedder_module_str)

    embedder_class = getattr(embedder_module, embedder_class_name)

    if not issubclass(embedder_class, Embedder):
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
    if not isinstance(path, str):
        raise ValueError("datasources.*.class must be a string like 'module.class'")

    datasource_path = path.split(".")
    if len(datasource_path) < 2:
        raise ValueError("datasources.*.class must be a string like 'module.class'")

    datasource_module_str = ".".join(datasource_path[:-1])
    datasource_class_name = datasource_path[-1]
    datasource_module = importlib.import_module(datasource_module_str)

    datasource_class = getattr(datasource_module, datasource_class_name)

    if not issubclass(datasource_class, DataSource):
        raise TypeError(f"datasource must be instance of {DataSource.__name__}")

    return datasource_class
