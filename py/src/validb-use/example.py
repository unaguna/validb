import enum
import os
import typing as t

from validb import Detected, DetectionData, SimpleRule


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


rules: t.List[SimpleRule[str, MyMsgType, str]] = [
    SimpleRule(
        "SELECT Code FROM country where InDepYear is NULL",
        lambda r: r[0],
        MyMsgType.NULL_YEAR,
        "null year",
    ),
    SimpleRule(
        "SELECT Code FROM country where SurfaceArea < Population",
        lambda r: r[0],
        MyMsgType.TOO_SMALL,
        "too small",
    ),
]

if __name__ == "__main__":
    from sqlalchemy import create_engine
    from sqlalchemy.orm import scoped_session, sessionmaker
    from sqlalchemy.sql import text

    engine = create_engine(os.environ["DEV_DB_URL"])
    session = scoped_session(
        sessionmaker(autocommit=False, autoflush=False, bind=engine)
    )

    detection_data: DetectionData[str, MyMsgType, str] = DetectionData()
    for rule in rules:
        sql = text(rule.sql)
        for r in session.execute(sql):
            msg_type, msg = rule.detected()
            detection_data.append(
                MyDetected(id=rule.id_of_row(r), msg_type=msg_type, msg=msg)
            )

    for id in detection_data.ids():
        print(detection_data[id])

    for msg_type in detection_data.msg_types():
        print(detection_data[msg_type])
