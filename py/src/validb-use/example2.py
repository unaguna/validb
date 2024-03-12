import os
import sys

from validb import validate_db
from validb.config import load_rules_from_yaml
from validb.dtcsvmapping import SimpleDetectionCsvMapping


if __name__ == "__main__":
    import csv
    import os

    # allow to import custom classes
    sys.path.append(os.path.join(os.path.dirname(__file__), "pythonpath"))

    rules, datasources = load_rules_from_yaml(
        os.path.join(os.path.dirname(__file__), "rules_host.yml")
    )
    with datasources:
        detection_data = validate_db(
            rules=rules,
            datasources=datasources,
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
