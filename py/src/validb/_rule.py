import abc
import importlib
import pathlib
import typing as t

from ._embedder import Embedder
from ._row import Row
from ._detected import ID, MSG, DETECTION_TYPE


DEFAULT_LEVEL = 0


class Rule(t.Generic[ID, DETECTION_TYPE, MSG], abc.ABC):
    """validation rule definition"""

    @classmethod
    def create(
        cls,
        sql: str,
        id_of_row: t.Callable[[Row], ID],
        level: int,
        detection_type: DETECTION_TYPE,
        msg: t.Callable[[Row], MSG],
        embedders: t.Optional[t.Sequence[Embedder]] = None,
    ) -> "Rule[ID, DETECTION_TYPE, MSG]":
        return _RuleImpl(
            sql, id_of_row, level, detection_type, msg, embedders=embedders
        )

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


class _RuleImpl(t.Generic[ID, DETECTION_TYPE, MSG], Rule[ID, DETECTION_TYPE, MSG]):
    """validation rule definition"""

    _sql: str
    _id_of_row: t.Callable[[Row], ID]
    _level: int
    _detection_type: DETECTION_TYPE
    _msg: t.Callable[[Row], MSG]
    _embedders: t.Sequence[Embedder]

    def __init__(
        self,
        sql: str,
        id_of_row: t.Callable[[Row], ID],
        level: int,
        detection_type: DETECTION_TYPE,
        msg: t.Callable[[Row], MSG],
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


class SimpleRule(Rule[str, str, str]):
    _sql: str
    _id_template: str
    _level: int
    _detection_type: str
    _msg: str
    _embedders: t.Sequence[Embedder]

    def __init__(
        self,
        sql: str,
        id_template: str,
        level: int,
        detection_type: str,
        msg: str,
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
        embedders: Sequence[Embedder]
            Generator of embedding variables to be used when creating messages.
            If not specified, only fields obtained by SQL can be embedded.
        """
        super().__init__()

        self._sql = sql
        self._id_template = id_template
        self._level = level
        self._detection_type = detection_type
        self._msg = msg
        self._embedders = embedders if embedders is not None else []

    @property
    def sql(self) -> str:
        return self._sql

    def id_of_row(self, row: Row) -> str:
        return self._id_template.format(*row.sequence, **row.mapping)

    def level(self) -> int:
        return self._level

    def detection_type(self) -> str:
        return self._detection_type

    def message(self, row: Row) -> str:
        final_row = row.extended(self._embedders)
        return self._msg.format(*final_row.sequence, **final_row.mapping)


class RuleDefRequired(t.TypedDict):
    sql: str
    id: str
    detection_type: str
    msg: str


class RuleDef(RuleDefRequired, total=False):
    level: int
    embedders: t.List[str]


class RulesFile(t.TypedDict):
    rules: t.Sequence[RuleDef]
    embedders: t.Mapping[str, t.Any]


def load_rules_from_yaml(
    filepath: t.Union[str, bytes, pathlib.Path]
) -> t.List[SimpleRule]:
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

    embedders: t.MutableMapping[str, Embedder] = {}

    for embedder_name, embedder_init in rules["embedders"].items():
        embedder_path_str = embedder_init["class"]
        if not isinstance(embedder_path_str, str):
            raise ValueError("embedders.*.class must be a string like 'module.class'")

        embedder_path = embedder_path_str.split(".")
        if len(embedder_path) < 2:
            raise ValueError("embedders.*.class must be a string like 'module.class'")

        embedder_module_str = ".".join(embedder_path[:-1])
        embedder_class_name = embedder_path[-1]
        embedder_module = importlib.import_module(embedder_module_str)

        embedder_class = getattr(embedder_module, embedder_class_name)
        embedder = embedder_class(
            **{key: value for key, value in embedder_init.items() if key != "class"}
        )

        embedders[embedder_name] = embedder

    return [
        SimpleRule(
            sql=rule["sql"],
            id_template=rule["id"],
            level=rule.get("level", DEFAULT_LEVEL),
            detection_type=rule["detection_type"],
            msg=rule["msg"],
            embedders=_construct_embedders(rule.get("embedders"), embedders),
        )
        for rule in rules["rules"]
    ]


def _construct_embedders(
    embedders: t.Optional[t.Sequence[str]], embedder_instances: t.Mapping[str, Embedder]
) -> t.Optional[t.Sequence[Embedder]]:
    if embedders is None:
        return None

    return [embedder_instances[embedder_name] for embedder_name in embedders]
