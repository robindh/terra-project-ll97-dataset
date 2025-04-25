# LL97 Dataset Builder

A Python tool for processing and analyzing Local Law 97 (LL97) compliance data for buildings in New York City. This tool processes LL97 and LL84 datasets to calculate carbon emissions, energy costs, and penalties for buildings.

## Overview

Local Law 97 (LL97) is a New York City law that sets carbon emissions limits for buildings over 25,000 square feet. This tool helps analyze building compliance by:

- Processing LL97 and LL84 building data
- Calculating carbon emissions for buildings
- Computing energy costs
- Determining potential penalties for non-compliance
- Generating comprehensive reports for analysis

## Features

- Process LL97 and LL84 datasets
- Calculate yearly carbon emissions
- Compute energy costs
- Determine compliance thresholds
- Calculate potential penalties
- Generate detailed reports
- Support for multiple year ranges

## Prerequisites

- Python 3.8 or higher
- Poetry for dependency management

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/terra-project-ll97-dataset.git
cd terra-project-ll97-dataset
```

2. Install dependencies using Poetry:
```bash
poetry install
```

## Usage

### Basic Usage

```bash
poetry run python -m terra_project_ll97_dataset.build_dataset \
    --ll97_dataset path/to/ll97_data.csv \
    --ll84_dataset path/to/ll84_data.csv \
    --output_dir path/to/output_directory
```

### Required Arguments

- `--ll97_dataset`: Path to the LL97 dataset CSV file
- `--ll84_dataset`: Path to the LL84 dataset CSV file
- `--output_dir`: Directory where output files will be saved

### Optional Arguments

- `--carbon_emissions_by_building_type`: Path to the carbon emissions thresholds file (defaults to included data file)
- `-v, --verbose`: Increase output verbosity

## Output Files

The tool generates two main output files:

1. `dataset_estimated_emissions_cost_penalties_for_each_year.csv`
   - Contains yearly calculations for each building
   - Includes carbon emissions, energy costs, thresholds, and penalties

2. `dataset_estimated_emissions_cost_penalties_for_year_range.csv`
   - Contains calculations averaged over specified year ranges
   - Provides aggregated metrics for compliance analysis

## Project Structure

```
terra_project_ll97_dataset/
├── calculator/          # Calculation modules
├── dataset/            # Dataset processing modules
├── util/               # Utility functions
├── data/               # Default data files
├── build_dataset.py    # Main entry point
└── arguments.py        # Command line argument handling
```

## Development

### Setting Up Development Environment

1. Create a virtual environment:
```bash
poetry shell
```

2. Install development dependencies:
```bash
poetry install --with dev
```

### Running Tests

```bash
poetry run pytest
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- New York City Department of Buildings
- Local Law 97 (LL97) documentation
- Local Law 84 (LL84) documentation

## Support

For support, please open an issue in the GitHub repository.
