import abc
import pathlib
import typing as t

import sqlalchemy

from ._detected import ID, MSG, MSG_TYPE


class Rule(t.Generic[ID, MSG_TYPE, MSG], abc.ABC):
    """validation rule definition"""

    @property
    @abc.abstractmethod
    def sql(self) -> str:
        """query to be executed to detect anomalies"""
        pass

    @abc.abstractmethod
    def id_of_row(self, row: sqlalchemy.Row[t.Any]) -> ID:
        """The function to calc the record ID from each row of SQL result.

        This ID is used to determine which record in the DB has the abnormality,
        so the ID is usually created from the primary key.

        Parameters
        ----------
        row : sqlalchemy.Row
            each row of a result of SQL execution

        Returns
        -------
        ID
            the record ID
        """
        pass

    @abc.abstractmethod
    def detected(self) -> t.Tuple[MSG_TYPE, MSG]:
        """Message type and message to be used when an abnormality is detected.

        Since the message type is used to distinguish which anomaly was found by which rule,
        it is usually specified as a different value for each rule.
        """
        pass


class SimpleRule(t.Generic[ID, MSG_TYPE, MSG], Rule[ID, MSG_TYPE, MSG]):
    """validation rule definition"""

    _sql: str
    _id_of_row: t.Callable[[sqlalchemy.Row[t.Any]], ID]
    _msg_type: MSG_TYPE
    _msg: MSG

    def __init__(
        self,
        sql: str,
        id_of_row: t.Callable[[sqlalchemy.Row[t.Any]], ID],
        msg_type: MSG_TYPE,
        msg: MSG,
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
        msg_type : MSG_TYPE
            the type of message;
            Since this is used to distinguish which anomaly was found by which rule,
            it is usually specified as a different value for each rule.
        msg : MSG
            the message of detection
        """
        super().__init__()

        self._sql = sql
        self._id_of_row = id_of_row
        self._msg_type = msg_type
        self._msg = msg

    @property
    def sql(self) -> str:
        return self._sql

    def id_of_row(self, row: t.Any) -> ID:
        return self._id_of_row(row)

    def detected(self) -> t.Tuple[MSG_TYPE, MSG]:
        return self._msg_type, self._msg


class TextRule(Rule[str, str, str]):
    _sql: str
    _id_template: str
    _msg_type: str
    _msg: str

    def __init__(self, sql: str, id_template: str, msg_type: str, msg: str) -> None:
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
        msg_type : MSG_TYPE
            the type of message;
            Since this is used to distinguish which anomaly was found by which rule,
            it is usually specified as a different value for each rule.
        msg : MSG
            the message of detection
        """
        super().__init__()

        self._sql = sql
        self._id_template = id_template
        self._msg_type = msg_type
        self._msg = msg

    @property
    def sql(self) -> str:
        return self._sql

    def id_of_row(self, row: sqlalchemy.Row[t.Any]) -> str:
        return self._id_template.format(*row)

    def detected(self) -> t.Tuple[str, str]:
        return self._msg_type, self._msg


class RuleDef(t.TypedDict):
    sql: str
    id: str
    msg_type: str
    msg: str


def load_rules_from_yaml(
    filepath: t.Union[str, bytes, pathlib.Path]
) -> t.List[TextRule]:
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
        TextRule(
            sql=rule["sql"],
            id_template=rule["id"],
            msg_type=rule["msg_type"],
            msg=rule["msg"],
        )
        for rule in rules
    ]
