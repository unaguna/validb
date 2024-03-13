import abc
import typing as t

from ..datasources import DataSources
from .._embedder import Embedder
from .._embedded_vars import EmbeddedVariables
from .._detected import ID, MSG, DETECTION_TYPE, Detected, DetectedType


DEFAULT_LEVEL = 0


class Rule(t.Generic[ID, DETECTION_TYPE, MSG], abc.ABC):
    """validation rule definition"""

    @property
    @abc.abstractmethod
    def sql(self) -> str:
        """query to be executed to detect anomalies"""
        pass

    @abc.abstractmethod
    def id_of_row(self, embedded_vars: EmbeddedVariables) -> ID:
        """The function to calc the record ID from each row of SQL result.

        This ID is used to determine which record in the DB has the abnormality,
        so the ID is usually created from the primary key.

        Parameters
        ----------
        embedded_vars : EmbeddedVariables
            variables according to a result of SQL execution

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
    def message(self, embedded_vars: EmbeddedVariables) -> MSG:
        """Message to be used when an abnormality is detected.

        Parameters
        ----------
        embedded_vars : EmbeddedVariables
            variables according to a result of SQL execution
        """
        pass

    @abc.abstractmethod
    def embedders(self) -> t.Iterator[Embedder]:
        """an iterator of the embedders registered in self

        The variables used to create Detected instances while detecting anomalies are extended using these embedders.
        """
        pass

    @abc.abstractmethod
    def exec(
        self, datasources: DataSources, detected: DetectedType[ID, DETECTION_TYPE, MSG]
    ) -> t.Sequence[Detected[ID, DETECTION_TYPE, MSG]]:
        """exec validation according the rule

        Parameters
        ----------
        datasources : DataSources
            data sources;
            The data sources required by the rule are used.
        detected : DetectedType[ID, DETECTION_TYPE, MSG]
            constructor of detected anomalies;
            If anomalies are detected, this constructor is executed for that number of instances,
            and the returned instances become elements of the final detection list.

        Returns
        -------
        Sequence[Detected[ID, DETECTION_TYPE, MSG]]
            List of detected anomalies
        """
        ...

    def detect(
        self,
        embedded_vars: EmbeddedVariables,
        constructor: DetectedType[ID, DETECTION_TYPE, MSG],
    ) -> Detected[ID, DETECTION_TYPE, MSG]:
        """construct Detected instance

        Parameters
        ----------
        embedded_vars : EmbeddedVariables
            Variables obtained in the process of detection.
            In this function, the variable is extended with embedders registered in self before use.
        constructor : DetectedType
            the constructor of Detected

        Returns
        -------
        Detected
            an abnormality detection
        """
        # Extend variables using embedder registered in self
        embedded_vars = embedded_vars.extended(self.embedders())

        return constructor(
            self.id_of_row(embedded_vars),
            self.level(),
            self.detection_type(),
            self.message(embedded_vars),
            embedded_vars,
        )
