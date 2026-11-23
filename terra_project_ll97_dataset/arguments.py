"""Command-line arguments for the LL97 dataset builder.

Required inputs are the LL97 covered-buildings file, the latest LL84
disclosure, and a directory for the two output CSVs. A missing output
directory is created, including any missing parent directories. The
carbon-limit table defaults to the copy shipped with this package, so
the default resolves correctly from any working directory.
"""

import argparse
import os

_PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CARBON_THRESHOLDS_CSV = os.path.join(
    _PACKAGE_DIR,
    "data",
    "carbon_thresholds_by_building_type.csv",
)


def _dir_path(path: str) -> str:
    """Return path, creating the directory when it is missing.

    An existing path must already be a directory. A missing path is
    created, including any missing parent directories.

    Args:
        path: Candidate output directory.

    Returns:
        The same path.

    Raises:
        argparse.ArgumentTypeError: path exists and is not a directory,
            or the directory could not be created.
    """
    if os.path.isdir(path):
        return path
    if os.path.exists(path):
        raise argparse.ArgumentTypeError(
            f"readable_dir:{path} is not a valid path"
        )
    try:
        os.makedirs(path)
    except OSError as error:
        raise argparse.ArgumentTypeError(
            f"readable_dir:{path} is not a valid path"
        ) from error
    return path


def _file_path(path: str) -> str:
    """Return path when it names an existing file.

    A directory does not qualify. The check uses os.path.isfile.

    Args:
        path: Candidate input CSV.

    Returns:
        The same path.

    Raises:
        argparse.ArgumentTypeError: path is not a file.
    """
    if os.path.isfile(path):
        return path
    raise argparse.ArgumentTypeError(
        f"readable_file:{path} is not a valid file"
    )


class BuildDatasetArguments:
    """Parser for the dataset builder's command line.

    Attributes:
        args: Parsed arguments after parse_args, otherwise None.
        parser: The argparse parser. Tests inspect its defaults directly.
    """

    def __init__(self) -> None:
        """Create the parser and register every flag."""
        self.args = None
        self.parser = argparse.ArgumentParser(
            description=(
                "Build LL97 dataset with carbon emissions, energy costs, "
                "and penalties"
            )
        )
        self.add_arguments()

    def add_arguments(self) -> None:
        """Register the input, output, and verbosity flags.

        --verbose is accepted and stored, but the builder does not print
        extra output when it is set.
        """
        self.parser.add_argument(
            "-v",
            "--verbose",
            action="store_true",
            help="increase output verbosity",
        )
        self.parser.add_argument(
            "--ll97_dataset",
            type=_file_path,
            required=True,
            help="location of the .csv file that contains the LL97 dataset",
        )
        self.parser.add_argument(
            "--ll84_dataset",
            type=_file_path,
            required=True,
            help=(
                "location of the .csv file that contains the LL84 dataset "
                "for the most recent year"
            ),
        )
        self.parser.add_argument(
            "--carbon_emissions_by_building_type",
            type=_file_path,
            help=(
                "location of the .csv file that contains the carbon "
                "emission targets for each building type"
            ),
            default=DEFAULT_CARBON_THRESHOLDS_CSV,
        )
        self.parser.add_argument(
            "--output_dir",
            type=_dir_path,
            required=True,
            help=(
                "directory where the output will be written. "
                "Created when it does not already exist"
            ),
        )

    def parse_args(self) -> None:
        """Parse sys.argv and store the result on self.args."""
        self.args = self.parser.parse_args()
