import csv
import typing as t

import click

from validb import validate_db
from validb.config import load_rules_from_yaml


@click.command()
@click.option(
    "--rules", "-r", "rules_path", required=True, type=click.Path(exists=True)
)
@click.option("--dest-csv", "-D", "dest_csv_path", type=click.Path())
def main(rules_path: str, dest_csv_path: t.Union[str, None]):
    rules, datasources = load_rules_from_yaml(rules_path)

    with datasources:
        detection_data = validate_db(rules=rules, datasources=datasources)

    click.echo(f"Detected: {detection_data.count}")
    if detection_data.count <= 0:
        exit(0)
    else:
        if dest_csv_path is not None:
            with open(dest_csv_path, mode="w", newline="", encoding="utf_8") as fp:
                csv_writer = csv.writer(fp)
                csv_writer.writerows(detection_data.rows())

        exit(10)


if __name__ == "__main__":
    main()
