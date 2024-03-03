import enum
import os
import sys
import typing as t

from validb import Detected, Rule, validate_db


class MyMsgType(enum.Enum):
    NULL_YEAR = "NULL_YEAR"
    TOO_SMALL = "TOO_SMALL"


class MyDetected(Detected[str, MyMsgType, str]):
    def row(self) -> t.Tuple[str, str, str]:
        return (
            self.id,
            self.msg_type.value,
            self.msg,
        )

    def __repr__(self) -> str:
        return f"<MyDetected: {self.row()}>"


rules: t.List[Rule[str, MyMsgType, str]] = [
    Rule.create(
        "SELECT Code FROM country where InDepYear is NULL",
        lambda r: r[0],
        MyMsgType.NULL_YEAR,
        lambda r: "null year",
    ),
    Rule.create(
        "SELECT Code, SurfaceArea, Population FROM country where SurfaceArea < Population",
        lambda r: r["Code"],
        MyMsgType.TOO_SMALL,
        lambda r: f"too small; SurfaceArea={r[1]}, Population={r['Population']}",
    ),
]


if __name__ == "__main__":
    import csv
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session

    engine = create_engine(os.environ["DEV_DB_URL"])

    with Session(engine) as session:
        detection_data = validate_db(
            rules=rules,
            detected=MyDetected,
            session=session,
            max_detection=None,
        )

    # Outputs a summary of anomalies per record
    for id in detection_data.ids():
        print(detection_data[id])

    # Outputs a summary of anomalies per message type
    for msg_type in detection_data.msg_types():
        print(detection_data[msg_type])

    # Outputs anomalies as CSV
    spamwriter = csv.writer(sys.stdout)
    spamwriter.writerows(detection_data.rows())

    print(f"too_many_detection={detection_data.too_many_detection}")
