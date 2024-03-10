import abc
import importlib
import pathlib
import typing as t

from sqlalchemy.sql import text

from .datasources import DataSource, DataSources, SQLAlchemyDataSource
from ._embedder import Embedder
from ._row import Row
from ._detected import ID, MSG, DETECTION_TYPE, Detected, DetectedType


DEFAULT_LEVEL = 0


class Rule(t.Generic[ID, DETECTION_TYPE, MSG], abc.ABC):
    """validation rule definition"""

    @property
    @abc.abstractmethod
    def sql(self) -> str:
        """query to be executed to detect anomalies"""
        pass

    @abc.abstractmethod
    def id_of_row(self, row: Row) -> ID:
        """The function to calc the record ID from each row of SQL result.

        This ID is used to determine which record in the DB has the abnormality,
        so the ID is usually created from the primary key.

        Parameters
        ----------
        row : Row
            each row of a result of SQL execution

        Returns
        -------
        ID
            the record ID
        """
        pass

    def level(self) -> int:
        """Level of detection.

        The higher the number, the more serious the detection is treated as.
        """
        return DEFAULT_LEVEL

    @abc.abstractmethod
    def detection_type(self) -> DETECTION_TYPE:
        """Detection type to be used when an abnormality is detected.

        Since the detection type is used to distinguish which anomaly was found by which rule,
        it is usually specified as a different value for each rule.
        """
        pass

    @abc.abstractmethod
    def message(self, row: Row) -> MSG:
        """Message to be used when an abnormality is detected.

        Parameters
        ----------
        row : Row
            each row of a result of SQL execution
        """
        pass

    @abc.abstractmethod
    def exec(
        self, datasources: DataSources, detected: DetectedType[ID, DETECTION_TYPE, MSG]
    ) -> t.Sequence[Detected[ID, DETECTION_TYPE, MSG]]: ...

    def detect(
        self, row: Row, constructor: DetectedType[ID, DETECTION_TYPE, MSG]
    ) -> Detected[ID, DETECTION_TYPE, MSG]:
        return constructor(
            self.id_of_row(row),
            self.level(),
            self.detection_type(),
            self.message(row),
        )


class SQLAlchemyRule(t.Generic[ID, DETECTION_TYPE, MSG], Rule[ID, DETECTION_TYPE, MSG]):
    """validation rule definition"""

    _sql: str
    _id_of_row: t.Callable[[Row], ID]
    _level: int
    _detection_type: DETECTION_TYPE
    _msg: t.Callable[[Row], MSG]
    _datasource: str
    _embedders: t.Sequence[Embedder]

    def __init__(
        self,
        sql: str,
        id_of_row: t.Callable[[Row], ID],
        level: int,
        detection_type: DETECTION_TYPE,
        msg: t.Callable[[Row], MSG],
        datasource: str,
        embedders: t.Optional[t.Sequence[Embedder]] = None,
    ) -> None:
        """create a validation rule

        The created rules are used as arguments to `validate_db()`.

        Parameters
        ----------
        sql : str
            query to be executed to detect anomalies
        id_of_row : t.Callable[[sqlalchemy.Row], ID]
            the function to calc the record ID from each row of SQL result;
            This ID is used to determine which record in the DB has the abnormality,
            so the ID is usually created from the primary key.
        detection_type : DETECTION_TYPE
            the type of detection;
            Since this is used to distinguish which anomaly was found by which rule,
            it is usually specified as a different value for each rule.
        msg : MSG
            the message of detection
        datasource : str
            name of the datasource
        embedders: Sequence[Embedder]
            Generator of embedding variables to be used when creating messages.
            If not specified, only fields obtained by SQL can be embedded.
        """
        super().__init__()

        self._sql = sql
        self._id_of_row = id_of_row
        self._level = level
        self._detection_type = detection_type
        self._msg = msg
        self._datasource = datasource
        self._embedders = embedders if embedders is not None else []

    @property
    def sql(self) -> str:
        return self._sql

    def id_of_row(self, row: Row) -> ID:
        return self._id_of_row(row)

    def level(self) -> int:
        return self._level

    def detection_type(self) -> DETECTION_TYPE:
        return self._detection_type

    def message(self, row: Row) -> MSG:
        return self._msg(row.extended(self._embedders))

    @property
    def datasource_name(self) -> str:
        return self._datasource

    def exec(
        self, datasources: DataSources, detected: DetectedType[ID, DETECTION_TYPE, MSG]
    ) -> t.Sequence[Detected[ID, DETECTION_TYPE, MSG]]:
        datasource = datasources[self.datasource_name]
        if not isinstance(datasource, SQLAlchemyDataSource):
            raise TypeError(
                f"the data source for ${self.__class__.__name__} must be ${SQLAlchemyDataSource.__name__}; actual={type(datasource)}"
            )

        sql = text(self.sql)

        sql_result = datasource.session.execute(sql)
        return [
            self.detect(Row.from_sqlalchemy(row), constructor=detected)
            for row in sql_result
        ]


class SimpleSQLAlchemyRule(SQLAlchemyRule[str, str, str]):
    _id_template: str
    _msg_template: str

    def __init__(
        self,
        sql: str,
        id_template: str,
        level: int,
        detection_type: str,
        msg: str,
        datasource: str,
        embedders: t.Optional[t.Sequence[Embedder]] = None,
    ) -> None:
        """create a validation rule

        The created rules are used as arguments to `validate_db()`.

        Parameters
        ----------
        sql : str
            query to be executed to detect anomalies
        id_template : str
            the template of a record ID of each row of SQL result;
            This ID is used to determine which record in the DB has the abnormality,
            so the ID is usually created from the primary key.
        level: int
            the level of detection;
            The higher the number, the more serious the detection is treated as.
        detection_type : str
            the type of detection;
            Since this is used to distinguish which anomaly was found by which rule,
            it is usually specified as a different value for each rule.
        msg : MSG
            the message of detection
        datasource : str
            name of the datasource
        embedders: Sequence[Embedder]
            Generator of embedding variables to be used when creating messages.
            If not specified, only fields obtained by SQL can be embedded.
        """
        super().__init__(
            sql=sql,
            id_of_row=self._get_id_of_row,
            level=level,
            detection_type=detection_type,
            msg=self._get_message,
            datasource=datasource,
            embedders=embedders,
        )
        self._id_template = id_template
        self._msg_template = msg

    def _get_id_of_row(self, row: Row) -> str:
        return self._id_template.format(*row.sequence, **row.mapping)

    def _get_message(self, row: Row) -> str:
        final_row = row.extended(self._embedders)
        return self._msg_template.format(*final_row.sequence, **final_row.mapping)


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
