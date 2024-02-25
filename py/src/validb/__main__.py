import csv
import typing as t

import click
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from validb import load_rules_from_yaml, validate_db


@click.command()
@click.argument("db", required=True)
@click.option(
    "--rules", "-r", "rules_path", required=True, type=click.Path(exists=True)
)
@click.option("--dest-csv", "-D", "dest_csv_path", type=click.Path())
def main(db: str, rules_path: str, dest_csv_path: t.Union[str, None]):
    rules = load_rules_from_yaml(rules_path)

    engine = create_engine(db)
    with Session(engine) as session:
        detection_data = validate_db(rules=rules, session=session)

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
