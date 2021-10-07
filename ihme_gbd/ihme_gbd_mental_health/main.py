"""executes bulk dataset import + chart updates for the UN_SDGs dataset.
The download step is quite manual at the moment so will not be included in main.py

Usage:
    python -m ihme_gbd.ihme_gbd_mental_health.main

    python -m ihme_gbd.ihme_gbd_mental_health.main --skip_download --skip_clean
"""
import click
from ihme_gbd.ihme_gbd_mental_health import DATASET_DIR, DATASET_NAMESPACE, OUTPATH

from ihme_gbd.ihme_gbd_mental_health import download, clean
from ihme_gbd import match_variables

from standard_importer import import_dataset
from standard_importer.chart_revision_suggester import ChartRevisionSuggester


@click.command()
@click.option(
    "--download_data/--skip_download",
    default=True,
    help="Whether or not to download the data from the source as it often takes quite some time.",
)
@click.option(
    "--clean_data/--skip_clean",
    default=True,
    help="Whether or not to clean the data, useful for just upserting previously cleaned data",
)
@click.option(
    "--import_data/--skip_import",
    default=True,
    help="Whether or not to import the data",
)
def main(download_data, clean_data, import_data):
    if download_data:
        download.main()
    if clean_data:
        clean.main()
    if import_dataset:
        import_dataset.main(DATASET_DIR, DATASET_NAMESPACE)
    match_variables.main(outpath=OUTPATH)

    suggester = ChartRevisionSuggester(DATASET_DIR)
    suggester.suggest()


if __name__ == "__main__":
    main()
