import csv
import typing as t

import click

from validb import validate_db, DetectionData
from validb.config import load_config, Config
from validb.csvmapping import SimpleDetectionCsvMapping


@click.command()
@click.option(
    "--config", "-c", "config_path", required=True, type=click.Path(exists=True)
)
@click.option("--dest-csv", "-D", "dest_csv_path", type=click.Path())
def main(config_path: str, dest_csv_path: t.Union[str, None]):
    config = load_config(config_path)

    with config.datasources:
        detection_data = validate_db(
            rules=config.rules,
            datasources=config.datasources,
            embedders=config.embedders,
        )

    if detection_data.count <= 0:
        click.echo(f"No anomalies detected.")
        exit(0)
    else:
        _output_summary(detection_data)
        click.echo()
        click.echo(f"Detected: {detection_data.count}")

        if dest_csv_path is not None:
            _output_csv(dest_csv_path, detection_data, config)

        exit(10)


def _output_summary(detection_data: DetectionData[str, str, str]):
    title_row = ("DETECTION_TYPE", "COUNT")
    rows = [
        (detection_name, len(detection_data[detection_name]))
        for detection_name in detection_data.detection_types()
    ]

    max_detection_type_len = max(len(title_row[0]), max(len(name) for name, _ in rows))
    max_count_len = max(len(title_row[1]), max(len(str(count)) for _, count in rows))

    for detection_type, count in (title_row, *rows):
        click.echo(
            "{}  {}".format(
                format(detection_type, f"<{max_detection_type_len}"),
                format(count, f">{max_count_len}"),
            )
        )


def _output_csv(
    dest_csv_path: str,
    detection_data: DetectionData[str, str, str],
    config: Config[str, str, str],
):
    detected_csvmapping = (
        config.detected_csvmapping
        if config.detected_csvmapping is not None
        else SimpleDetectionCsvMapping()
    )

    with open(dest_csv_path, mode="w", newline="", encoding="utf_8") as fp:
        csv_writer = csv.writer(fp)
        csv_writer.writerows(detected_csvmapping.rows(detection_data))


if __name__ == "__main__":
    main()
