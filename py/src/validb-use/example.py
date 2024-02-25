import enum
import os
import typing as t

from validb import Detected


class MyMsgType(enum.Enum):
    NULL_YEAR = "NULL_YEAR"


class MyDetected(Detected[str, MyMsgType, str]):
    def row(self) -> t.Tuple[str, str, str]:
        return (
            self.id,
            self.msg_type.value,
            self.msg,
        )


if __name__ == "__main__":
    from sqlalchemy import create_engine
    from sqlalchemy.orm import scoped_session, sessionmaker
    from sqlalchemy.sql import text

    engine = create_engine(os.environ["DEV_DB_URL"])
    session = scoped_session(
        sessionmaker(autocommit=False, autoflush=False, bind=engine)
    )

    detected_list: t.List[MyDetected] = []
    sql = text("SELECT * FROM country where InDepYear is NULL")
    for r in session.execute(sql).mappings():
        detected_list.append(
            MyDetected(id=r["Code"], msg_type=MyMsgType.NULL_YEAR, msg="?")
        )

    print([d.row() for d in detected_list])
