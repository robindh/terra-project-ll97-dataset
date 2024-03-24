#!/usr/bin/python3

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
