import datetime as dt
import enum
import os
import sys
import typing as t

from validb import (
    DataSources,
    Detected,
    Embedder,
    Rule,
    validate_db,
)
from validb.datasources.sqlalchemy import SQLAlchemyDataSource
from validb.rules.sqlalchemy import SQLAlchemyRule
from validb.csvmapping import SimpleDetectionCsvMapping


class MyMsgType(enum.Enum):
    NULL_YEAR = "NULL_YEAR"
    TOO_SMALL = "TOO_SMALL"


class MyDetected(Detected[str, MyMsgType, str]):
    def __repr__(self) -> str:
        return f"<MyDetected: {self.id_str}, {self.detection_type_str}, {self.msg_str}>"


class MyEmbedder(Embedder):
    def extend(
        self, vars_seq: t.Sequence[t.Any], vars_map: t.Mapping[str, t.Any]
    ) -> t.Mapping[str, t.Any]:
        return {**vars_map, "today": dt.date.today()}


rules: t.List[Rule[str, MyMsgType, str]] = [
    SQLAlchemyRule(
        "SELECT Code FROM country where InDepYear is NULL",
        lambda r: r[0],
        0,
        MyMsgType.NULL_YEAR,
        lambda r: f"null year; today={r['today']}",
        datasource="mysql",
        embedders=["today"],
    ),
    SQLAlchemyRule(
        "SELECT Code, SurfaceArea, Population FROM country where SurfaceArea < Population",
        lambda r: r["Code"],
        1,
        MyMsgType.TOO_SMALL,
        lambda r: f"too small; SurfaceArea={r[1]}, Population={r['Population']}",
        datasource="mysql",
    ),
]


if __name__ == "__main__":
    import csv

    embedders = {
        "today": MyEmbedder(),
    }

    with DataSources(
        {"mysql": SQLAlchemyDataSource(url=os.environ["DEV_DB_URL"])}
    ) as datasources:
        detection_data = validate_db(
            rules=rules,
            detected=MyDetected,
            datasources=datasources,
            embedders=embedders,
            max_detection=None,
        )

    # Outputs a summary of anomalies per record
    for id in detection_data.ids():
        print(detection_data[id])

    # Outputs a summary of anomalies per detection type
    for detection_type in detection_data.detection_types():
        print(detection_data[detection_type])

    print("")
    print("")
    print("")
    print("")

    # Outputs a summary of anomalies per detection type
    for level, detection_type in detection_data.levels_detection_types():
        print(detection_data[(level, detection_type)])

    # Outputs anomalies as CSV
    csv_row = SimpleDetectionCsvMapping()
    spamwriter = csv.writer(sys.stdout)
    spamwriter.writerows(csv_row.rows(detection_data))

    print(f"too_many_detection={detection_data.too_many_detection}")
