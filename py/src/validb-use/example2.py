import os
import sys
import typing as t

from validb import Detected, validate_db, load_rules_from_yaml


class MyDetected(Detected[str, str, str]):
    def row(self) -> t.Tuple[str, str, str]:
        return (
            self.id,
            self.msg_type,
            self.msg,
        )

    def __repr__(self) -> str:
        return f"<MyDetected: {self.row()}>"


if __name__ == "__main__":
    import csv
    import os
    from sqlalchemy import create_engine
    from sqlalchemy.orm import scoped_session, sessionmaker

    rules = load_rules_from_yaml(os.path.join(os.path.dirname(__file__), "rules.yml"))

    engine = create_engine(os.environ["DEV_DB_URL"])
    session = scoped_session(
        sessionmaker(autocommit=False, autoflush=False, bind=engine)
    )

    detection_data = validate_db(
        rules=rules,
        detected=lambda id, msg_type, msg: MyDetected(
            id=id, msg_type=msg_type, msg=msg
        ),
        session=session,
    )

    session.close()

    for id in detection_data.ids():
        print(detection_data[id])

    for msg_type in detection_data.msg_types():
        print(detection_data[msg_type])

    spamwriter = csv.writer(sys.stdout)
    spamwriter.writerows(detection_data.rows())
