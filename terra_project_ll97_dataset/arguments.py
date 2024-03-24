import argparse
import os


def _dir_path(path: str):
    if os.path.isdir(path):
        return path
    else:
        raise argparse.ArgumentTypeError(f"readable_dir:{path} is not a valid path")


def _file_path(path: str):
    if os.path.exists(path):
        return path
    else:
        raise argparse.ArgumentTypeError(f"readable_file:{path} is not a valid file")


class BuildDatasetArguments:

    def __init__(self):
        self.args = None
        self.parser = argparse.ArgumentParser()
        self.add_arguments()

    def add_arguments(self):
        self.parser.add_argument(
            "-v", "--verbose",
            action="store_true",
            help="increase output verbosity")
        self.parser.add_argument(
            "--ll97_dataset",
            type=_file_path,
            help="location of the .csv file that contains the LL97 dataset")
        self.parser.add_argument(
            "--ll84_dataset",
            type=_file_path,
            help="location of the .csv file that contains the LL84 dataset for the most recent year")
        self.parser.add_argument(
            "--carbon_emissions_by_building_type",
            type=_file_path,
            help="location of the .csv file that contains the carbon emission targets for each building type",
            default="./terra_project_ll97_dataset/data/carbon_thresholds_by_building_type.csv")
        self.parser.add_argument(
            "--output_dir",
            type=_dir_path,
            help="directory where the output will be written")

    def parse_args(self):
        self.args = self.parser.parse_args()

