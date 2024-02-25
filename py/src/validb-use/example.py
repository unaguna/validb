import enum
import os
import typing as t

from validb import Detected, SimpleRule


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


rules: t.List[SimpleRule[MyMsgType, str]] = [
    SimpleRule(
        "SELECT * FROM country where InDepYear is NULL",
        MyMsgType.NULL_YEAR,
        "null year",
    ),
    SimpleRule(
        "SELECT * FROM country where SurfaceArea < Population",
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

    detected_list: t.List[MyDetected] = []
    for rule in rules:
        sql = text(rule.sql)
        for r in session.execute(sql).mappings():
            msg_type, msg = rule.detected()
            detected_list.append(MyDetected(id=r["Code"], msg_type=msg_type, msg=msg))

    print([d.row() for d in detected_list])
