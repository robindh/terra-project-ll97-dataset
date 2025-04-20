"""
Command line argument handling for the LL97 dataset builder.
This module defines and parses command line arguments required for dataset processing.
"""

import argparse
import os


def _dir_path(path: str) -> str:
    """
    Validates that a given path is a directory.
    
    Args:
        path (str): The path to validate
        
    Returns:
        str: The validated directory path
        
    Raises:
        argparse.ArgumentTypeError: If the path is not a valid directory
    """
    if os.path.isdir(path):
        return path
    else:
        raise argparse.ArgumentTypeError(f"readable_dir:{path} is not a valid path")


def _file_path(path: str) -> str:
    """
    Validates that a given path is a file.
    
    Args:
        path (str): The path to validate
        
    Returns:
        str: The validated file path
        
    Raises:
        argparse.ArgumentTypeError: If the path is not a valid file
    """
    if os.path.exists(path):
        return path
    else:
        raise argparse.ArgumentTypeError(f"readable_file:{path} is not a valid file")


class BuildDatasetArguments:
    """
    Handles command line argument parsing for the dataset builder.
    Defines and manages all required arguments for processing LL97 and LL84 datasets.
    """

    def __init__(self):
        """Initialize the argument parser and add all required arguments."""
        self.args = None
        self.parser = argparse.ArgumentParser(
            description="Build LL97 dataset with carbon emissions, energy costs, and penalties"
        )
        self.add_arguments()

    def add_arguments(self):
        """
        Add all required command line arguments to the parser.
        Includes arguments for input datasets, output directory, and verbosity.
        """
        self.parser.add_argument(
            "-v", "--verbose",
            action="store_true",
            help="increase output verbosity"
        )
        self.parser.add_argument(
            "--ll97_dataset",
            type=_file_path,
            help="location of the .csv file that contains the LL97 dataset"
        )
        self.parser.add_argument(
            "--ll84_dataset",
            type=_file_path,
            help="location of the .csv file that contains the LL84 dataset for the most recent year"
        )
        self.parser.add_argument(
            "--carbon_emissions_by_building_type",
            type=_file_path,
            help="location of the .csv file that contains the carbon emission targets for each building type",
            default="./terra_project_ll97_dataset/data/carbon_thresholds_by_building_type.csv"
        )
        self.parser.add_argument(
            "--output_dir",
            type=_dir_path,
            help="directory where the output will be written"
        )

    def parse_args(self):
        """Parse the command line arguments and store them in self.args."""
        self.args = self.parser.parse_args()

