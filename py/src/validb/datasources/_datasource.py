import abc
import typing as t

from sqlalchemy.orm import Session, scoped_session


class DataSource(t.ContextManager, abc.ABC):
    @abc.abstractmethod
    def close(self):
        """close this datasource

        This function is executed when Datasources containing this datasource is closed.
        Proper termination processing (e.g., closing the connection) is required here.
        """
        ...

    def __enter__(self) -> "DataSource":
        return self

    def __exit__(
        self,
        __exc_type: t.Optional[t.Type[BaseException]],
        __exc_value: t.Optional[BaseException],
        __traceback: t.Any,
    ) -> t.Optional[bool]:
        self.close()


class SQLAlchemyDataSource(DataSource):
    _session: t.Union[Session, scoped_session[Session]]

    def __init__(self, session: t.Union[Session, scoped_session[Session]]) -> None:
        self._session = session

    def close(self):
        self._session.close()

    @property
    def session(self) -> t.Union[Session, scoped_session[Session]]:
        return self._session


class DataSources(t.Dict[str, DataSource], t.ContextManager):
    def __enter__(self) -> "DataSources":
        return self

    def __exit__(
        self,
        __exc_type: t.Optional[t.Type[BaseException]],
        __exc_value: t.Optional[BaseException],
        __traceback: t.Any,
    ) -> t.Optional[bool]:
        self.close()

    def close(self):
        # close all datasources
        for datasource in self.values():
            try:
                datasource.close()
            except:
                # TODO: logging WARNING
                pass
