# LL97 Dataset Builder

A Python tool for processing and analyzing Local Law 97 (LL97) compliance data for buildings in New York City. This tool processes LL97 and LL84 datasets to calculate carbon emissions, energy costs, and penalties for buildings.

This project was developed as part of a [terra.do](https://terra.do) course by a collaborative group of learners focused on climate tech and sustainability solutions.

## Project Context

This tool was created as a group project during a terra.do course, bringing together individuals passionate about addressing climate change through technology. The collaborative nature of this project allowed us to combine diverse perspectives and expertise to create a comprehensive solution for analyzing building emissions compliance in New York City.

For detailed project documentation and background, visit our [project documentation page](https://tame-echo-70d.notion.site/Local-Law-97-Terra-do-final-project-46e92934b03f46d790f190ce599127c1).

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

- Python 3.12 or newer
- Poetry for dependency management

## Installation

1. Clone the repository:
```bash
git clone https://github.com/robindh/terra-project-ll97-dataset.git
cd terra-project-ll97-dataset
```

2. Install dependencies using Poetry. This also installs the test tools:
```bash
poetry install
```

## Usage

### Basic Usage

The tool creates `--output_dir` when that folder does not exist, including any missing parent folders. A path that already exists must be a directory.

```bash
poetry run python -m terra_project_ll97_dataset.build_dataset \
    --ll97_dataset path/to/ll97_data.csv \
    --ll84_dataset path/to/ll84_data.csv \
    --output_dir path/to/output_directory
```

### Required Arguments

- `--ll97_dataset`: Path to an existing LL97 dataset CSV file
- `--ll84_dataset`: Path to an existing LL84 dataset CSV file
- `--output_dir`: Directory where output files will be saved. Created when it does not already exist.

### Optional Arguments

- `--carbon_emissions_by_building_type`: Path to the carbon emissions thresholds file. The default is the table shipped with this package, and that default works from any working directory.
- `-v, --verbose`: Accepted, and currently silent. Setting it does not change the output.

Each run prints how many LL97 buildings had no matching LL84 row. Those buildings remain in both output files with energy use of zero. A count of zero means every LL97 building matched.

A missing expected LL84 header stops the run. The error names every missing column.

## Output Files

The tool generates two main output files:

1. `dataset_estimated_emissions_cost_penalties_for_each_year.csv`
   - Contains yearly calculations for each building
   - Includes carbon emissions, energy costs, thresholds, and penalties

2. `dataset_estimated_emissions_cost_penalties_for_year_range.csv`
   - Averages the same metrics over each compliance period
   - Period columns are `2024-2029`, `2030-2034`, `2035-2039`, `2040-2049`, and `2050+`
   - `2050+` averages only the year 2050

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

`poetry install` from the installation steps is enough to run the tests. To activate that environment in the current shell:

```bash
source $(poetry env activate)
```

### Running Tests

```bash
poetry run pytest
```

Pull requests and pushes to `main` run this same command on Python 3.12 in GitHub Actions.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [NYC Open Data](https://opendata.cityofnewyork.us/) - The source of our building datasets
- Local Law 97 (LL97) documentation
- Local Law 84 (LL84) documentation

## Support

For support, please open an issue in the GitHub repository.
