import os
import sys

from validb import validate_db, load_rules_from_yaml


if __name__ == "__main__":
    import csv
    import os
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session

    rules = load_rules_from_yaml(os.path.join(os.path.dirname(__file__), "rules.yml"))

    engine = create_engine(os.environ["DEV_DB_URL"])

    with Session(engine) as session:
        detection_data = validate_db(
            rules=rules,
            session=session,
        )

    # Outputs a summary of anomalies per record
    for id in detection_data.ids():
        print(detection_data[id])

    # Outputs a summary of anomalies per detection type
    for detection_type in detection_data.detection_types():
        print(detection_data[detection_type])

    # Outputs anomalies as CSV
    spamwriter = csv.writer(sys.stdout)
    spamwriter.writerows(detection_data.rows())

    print(f"too_many_detection={detection_data.too_many_detection}")
