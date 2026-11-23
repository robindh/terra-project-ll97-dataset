#!/usr/bin/python3
"""
Main script for building the LL97 dataset.
This script processes LL97 and LL84 datasets to calculate carbon emissions,
energy costs, and penalties for buildings in New York City.
"""

import argparse

from terra_project_ll97_dataset.arguments import BuildDatasetArguments
from terra_project_ll97_dataset.dataset.dataset_builder import DatasetBuilder


def main():
    arguments = BuildDatasetArguments()
    arguments.parse_args()

    builder = DatasetBuilder(arguments.args)
    builder.run()


if __name__ == '__main__':
    main()
