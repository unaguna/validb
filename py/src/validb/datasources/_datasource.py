import abc
import typing as t


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


class DataSources(t.ContextManager):
    _datasources: t.MutableMapping[str, DataSource]

    def __init__(
        self, datasources: t.Optional[t.MutableMapping[str, DataSource]] = None
    ) -> None:
        self._datasources = datasources if datasources is not None else {}

    def __getitem__(self, key: str) -> DataSource:
        return self._datasources[key]

    def __enter__(self) -> "DataSources":
        try:
            for datasource in self._datasources.values():
                datasource.__enter__()
        except:
            # TODO: logging ERROR
            self.close()
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
        for datasource in self._datasources.values():
            try:
                datasource.close()
            except:
                # TODO: logging WARNING
                pass
