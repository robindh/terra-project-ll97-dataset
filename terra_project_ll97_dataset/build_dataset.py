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
    """
    Main entry point for the dataset builder.
    Parses command line arguments and executes the dataset building process.
    """
    # Initialize and parse command line arguments
    arguments = BuildDatasetArguments()
    arguments.parse_args()
    
    # Create and run the dataset builder
    builder = DatasetBuilder(arguments.args)
    builder.run()


if __name__ == '__main__':
    main()
