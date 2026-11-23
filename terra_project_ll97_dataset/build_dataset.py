#!/usr/bin/env python3
"""Build the LL97 emissions, cost, and penalty datasets.

Run this module with the LL97 and LL84 CSV paths and an output directory.
It writes one CSV of yearly estimates and one CSV of period averages.
"""

from terra_project_ll97_dataset import arguments
from terra_project_ll97_dataset.dataset import dataset_builder


def main() -> None:
    """Parse the command line and write both output datasets."""
    parsed = arguments.BuildDatasetArguments()
    parsed.parse_args()

    builder = dataset_builder.DatasetBuilder(parsed.args)
    builder.run()


if __name__ == "__main__":
    main()
