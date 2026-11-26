#!/usr/bin/env python3
"""Build the LL97 emissions, cost, and penalty datasets.

Run this module with the LL97 and LL84 CSV paths and an output directory.
It writes one CSV of yearly estimates and one CSV of period averages.
A missing expected LL84 header is printed and the run stops.
"""

import sys

from terra_project_ll97_dataset import arguments
from terra_project_ll97_dataset.dataset import data_cleansing
from terra_project_ll97_dataset.dataset import dataset_builder
from terra_project_ll97_dataset.dataset import ll84_source


def main() -> None:
    """Parse the command line and write both output datasets."""
    parsed = arguments.BuildDatasetArguments()
    parsed.parse_args()

    builder = dataset_builder.DatasetBuilder(parsed.args)
    try:
        builder.run()
    except (
        data_cleansing.MissingLl84ColumnError,
        ll84_source.Ll84SourceError,
    ) as error:
        print(error, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
