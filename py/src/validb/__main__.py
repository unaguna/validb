import csv
import typing as t

import click

from validb import validate_db
from validb.config import load_config
from validb.csvmapping import SimpleDetectionCsvMapping


@click.command()
@click.option(
    "--rules", "-r", "rules_path", required=True, type=click.Path(exists=True)
)
@click.option("--dest-csv", "-D", "dest_csv_path", type=click.Path())
def main(rules_path: str, dest_csv_path: t.Union[str, None]):
    config = load_config(rules_path)

    with config.datasources:
        detection_data = validate_db(rules=config.rules, datasources=config.datasources)

    click.echo(f"Detected: {detection_data.count}")
    if detection_data.count <= 0:
        exit(0)
    else:
        detected_csvmapping = (
            config.detected_csvmapping
            if config.detected_csvmapping is not None
            else SimpleDetectionCsvMapping()
        )

        if dest_csv_path is not None:
            with open(dest_csv_path, mode="w", newline="", encoding="utf_8") as fp:
                csv_writer = csv.writer(fp)
                csv_writer.writerows(detected_csvmapping.rows(detection_data))

        exit(10)


if __name__ == "__main__":
    main()
