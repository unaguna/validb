import abc
import pathlib
import typing as t

from ._row import Row
from ._detected import ID, MSG, DETECTION_TYPE


class Rule(t.Generic[ID, DETECTION_TYPE, MSG], abc.ABC):
    """validation rule definition"""

    @classmethod
    def create(
        cls,
        sql: str,
        id_of_row: t.Callable[[Row], ID],
        detection_type: DETECTION_TYPE,
        msg: t.Callable[[Row], MSG],
    ) -> "Rule[ID, DETECTION_TYPE, MSG]":
        return _RuleImpl(sql, id_of_row, detection_type, msg)

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
    _detection_type: DETECTION_TYPE
    _msg: t.Callable[[Row], MSG]

    def __init__(
        self,
        sql: str,
        id_of_row: t.Callable[[Row], ID],
        detection_type: DETECTION_TYPE,
        msg: t.Callable[[Row], MSG],
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
        """
        super().__init__()

        self._sql = sql
        self._id_of_row = id_of_row
        self._detection_type = detection_type
        self._msg = msg

    @property
    def sql(self) -> str:
        return self._sql

    def id_of_row(self, row: Row) -> ID:
        return self._id_of_row(row)

    def detection_type(self) -> DETECTION_TYPE:
        return self._detection_type

    def message(self, row: Row) -> MSG:
        return self._msg(row)


class SimpleRule(Rule[str, str, str]):
    _sql: str
    _id_template: str
    _detection_type: str
    _msg: str

    def __init__(
        self, sql: str, id_template: str, detection_type: str, msg: str
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
        detection_type : str
            the type of detection;
            Since this is used to distinguish which anomaly was found by which rule,
            it is usually specified as a different value for each rule.
        msg : MSG
            the message of detection
        """
        super().__init__()

        self._sql = sql
        self._id_template = id_template
        self._detection_type = detection_type
        self._msg = msg

    @property
    def sql(self) -> str:
        return self._sql

    def id_of_row(self, row: Row) -> str:
        return self._id_template.format(*row.sequence, **row.mapping)

    def detection_type(self) -> str:
        return self._detection_type

    def message(self, row: Row) -> str:
        return self._msg.format(*row.sequence, **row.mapping)


class RuleDef(t.TypedDict):
    sql: str
    id: str
    detection_type: str
    msg: str


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
        rules: t.List[RuleDef] = yaml.safe_load(fp)

    return [
        SimpleRule(
            sql=rule["sql"],
            id_template=rule["id"],
            detection_type=rule["detection_type"],
            msg=rule["msg"],
        )
        for rule in rules
    ]
