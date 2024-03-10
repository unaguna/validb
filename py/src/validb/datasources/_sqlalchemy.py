import typing as t

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import Session, scoped_session

from ._datasource import DataSource


class SQLAlchemyDataSource(DataSource):
    _engine: Engine
    _session: t.Union[Session, scoped_session[Session]]

    def __init__(self, **kwargs: t.Any) -> None:
        self._engine = create_engine(**kwargs)

    def __enter__(self) -> DataSource:
        self._session = Session(self._engine)
        return super().__enter__()

    def close(self):
        self._session.close()

    @property
    def session(self) -> t.Union[Session, scoped_session[Session]]:
        return self._session
