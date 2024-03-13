import typing as t

from sqlalchemy.sql import text

from ..datasources import DataSources, SQLAlchemyDataSource
from .._embedder import Embedder
from .._embedded_vars import EmbeddedVariables
from .._detected import ID, MSG, DETECTION_TYPE, Detected, DetectedType
from ._rule import Rule


class SQLAlchemyRule(t.Generic[ID, DETECTION_TYPE, MSG], Rule[ID, DETECTION_TYPE, MSG]):
    """validation rule definition"""

    _sql: str
    _id_of_row: t.Callable[[EmbeddedVariables], ID]
    _level: int
    _detection_type: DETECTION_TYPE
    _msg: t.Callable[[EmbeddedVariables], MSG]
    _datasource: str
    _embedders: t.Sequence[Embedder]

    def __init__(
        self,
        sql: str,
        id_of_row: t.Callable[[EmbeddedVariables], ID],
        level: int,
        detection_type: DETECTION_TYPE,
        msg: t.Callable[[EmbeddedVariables], MSG],
        datasource: str,
        embedders: t.Optional[t.Sequence[Embedder]] = None,
    ) -> None:
        """create a validation rule

        The created rules are used as arguments to `validate_db()`.

        Parameters
        ----------
        sql : str
            query to be executed to detect anomalies
        id_of_row : Callable[[EmbeddedVariables], ID]
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

    def id_of_row(self, embedded_vars: EmbeddedVariables) -> ID:
        return self._id_of_row(embedded_vars)

    def level(self) -> int:
        return self._level

    def detection_type(self) -> DETECTION_TYPE:
        return self._detection_type

    def message(self, embedded_vars: EmbeddedVariables) -> MSG:
        return self._msg(embedded_vars)

    def embedders(self) -> t.Iterator[Embedder]:
        return iter(self._embedders)

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
            self.detect(EmbeddedVariables.from_sqlalchemy(row), constructor=detected)
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

    def _get_id_of_row(self, embedded_vars: EmbeddedVariables) -> str:
        return self._id_template.format(
            *embedded_vars.sequence, **embedded_vars.mapping
        )

    def _get_message(self, embedded_vars: EmbeddedVariables) -> str:
        return self._msg_template.format(
            *embedded_vars.sequence, **embedded_vars.mapping
        )
