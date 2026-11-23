"""Join LL97 and LL84 rows and write the emissions datasets.

The yearly file has one emissions, cost, limit, and penalty column per
calendar year from 2024 through 2050. The period file averages those same
quantities. The 2050+ columns average only the year 2050.
"""

import os.path
from typing import Callable

import pandas as pd

from terra_project_ll97_dataset.calculator import carbon_emissions
from terra_project_ll97_dataset.calculator import carbon_emissions_thresholds
from terra_project_ll97_dataset.calculator import cost_of_energy
from terra_project_ll97_dataset.calculator import penalties
from terra_project_ll97_dataset.dataset import data_cleansing
from terra_project_ll97_dataset.util import common


def _avg_over_year_range(
    year_range: range,
    row: pd.Series,
    func: Callable[[int, pd.Series], float],
) -> float:
    """Average func over every year in year_range.

    Args:
        year_range: Years to include. An empty range averages to 0.0.
        row: One joined building row.
        func: Per-year calculation. Called as func(year, row).

    Returns:
        The arithmetic mean of func across year_range.
    """
    if len(year_range) == 0:
        return 0.0

    total_val = 0.0
    for year in year_range:
        total_val += func(year, row)
    return total_val / len(year_range)


class DatasetBuilder:
    """Writer for the yearly and period LL97 datasets.

    Attributes:
        arguments: Parsed command-line arguments.
        start_year: First year written to the yearly file.
        end_year: Last year written to the yearly file.
    """

    def __init__(self, arguments) -> None:
        """Load the emission, price, and limit lookup tables.

        Args:
            arguments: Parsed arguments with the three input paths and
                output_dir.
        """
        self.arguments = arguments
        self.start_year = common.ANALYSIS_START_YEAR
        self.end_year = common.ANALYSIS_END_YEAR

        limits_path = arguments.carbon_emissions_by_building_type
        self._carbon_emissions_lookup_table = (
            carbon_emissions.get_carbon_emissions_by_year_and_energy_type(
                self.start_year,
                self.end_year,
            )
        )
        self._cost_of_energy_lookup_table = (
            cost_of_energy.get_cost_of_energy_by_year_and_energy_type(
                self.start_year,
                self.end_year,
            )
        )
        self._carbon_emissions_threshold_lookup_table = (
            carbon_emissions_thresholds
            .get_carbon_emissions_threshold_by_building_type_and_start_year(
                limits_path
            )
        )

    def _get_carbon_emissions(self, year: int, row: pd.Series) -> float:
        """Return emissions in tCO2e for one building and year."""
        return carbon_emissions.get_carbon_emissions(
            self._carbon_emissions_lookup_table,
            year,
            row,
        )

    def _get_cost_of_energy(self, year: int, row: pd.Series) -> float:
        """Return energy cost in dollars for one building and year."""
        return cost_of_energy.get_cost_of_energy(
            self._cost_of_energy_lookup_table,
            year,
            row,
        )

    def _get_carbon_emissions_thresholds(
        self,
        year: int,
        row: pd.Series,
    ) -> float:
        """Return the emissions limit in tCO2e for one building and year."""
        return carbon_emissions_thresholds.get_carbon_emissions_thresholds(
            self._carbon_emissions_threshold_lookup_table,
            year,
            row,
        )

    def _add_emissions_cost_threshold_and_penalty(
        self,
        df: pd.DataFrame,
        column_prefix: str,
        name_suffix: str,
        compute: Callable,
    ) -> None:
        """Add emissions, cost, limit, and penalty columns in place.

        name_suffix is empty for one calendar year and "_per_year" for a
        period average. compute receives the building row and the per-year
        function. The penalty uses the emissions and limit columns just
        written, so it matches that same year or period.

        Args:
            df: Building frame to extend.
            column_prefix: Year or period label.
            name_suffix: "" or "_per_year".
            compute: Turns a row and a per-year function into a float.
        """
        emissions_column = f"{column_prefix}_carbon_emissions{name_suffix}"
        cost_column = f"{column_prefix}_cost_of_energy{name_suffix}"
        threshold_column = (
            f"{column_prefix}_carbon_emissions_threshold{name_suffix}"
        )
        penalty_column = f"{column_prefix}_estimated_penalty{name_suffix}"

        df[emissions_column] = df.apply(
            lambda row: compute(row, self._get_carbon_emissions),
            axis=1,
        )
        df[cost_column] = df.apply(
            lambda row: compute(row, self._get_cost_of_energy),
            axis=1,
        )
        df[threshold_column] = df.apply(
            lambda row: compute(row, self._get_carbon_emissions_thresholds),
            axis=1,
        )
        df[penalty_column] = df.apply(
            lambda row: penalties.calculate_penalties(
                row,
                emissions_column,
                threshold_column,
            ),
            axis=1,
        )

    def _build_yearly_dataset(self) -> None:
        """Write one row per building with a column group per year."""
        df_with_yearly_values = self._joined_dataset.copy()

        for year in range(self.start_year, self.end_year + 1):
            # Bind year now. A closure over the loop variable would use
            # the final year for every column.
            self._add_emissions_cost_threshold_and_penalty(
                df_with_yearly_values,
                str(year),
                "",
                lambda row, func, year=year: func(year, row),
            )

        yearly_name = (
            "dataset_estimated_emissions_cost_penalties_for_each_year.csv"
        )
        df_with_yearly_values.to_csv(
            os.path.join(self.arguments.output_dir, yearly_name)
        )

    def _build_dataset_for_range_of_years(self) -> None:
        """Write one row per building with a column group per period."""
        df_for_range_of_years = self._joined_dataset.copy()

        for period in common.get_year_ranges():
            # Bind this period's years before the next iteration.
            years = period.years
            self._add_emissions_cost_threshold_and_penalty(
                df_for_range_of_years,
                period.label,
                "_per_year",
                lambda row, func, years=years: _avg_over_year_range(
                    years,
                    row,
                    func,
                ),
            )

        range_name = (
            "dataset_estimated_emissions_cost_penalties_for_year_range.csv"
        )
        df_for_range_of_years.to_csv(
            os.path.join(self.arguments.output_dir, range_name)
        )

    def _join_ll97_ll84_datasets(self) -> None:
        """Join the inputs on a normalized BBL and store the result.

        The index is the normalized key. The original LL84 BBL text is kept
        as its own column. Rows present only in LL97 stay in the result.
        """
        ll97_df = pd.read_csv(
            self.arguments.ll97_dataset,
            dtype={"BBL": "string"},
        )
        ll97_df["BBL"] = ll97_df["BBL"].apply(data_cleansing.normalise_bbl)
        ll97_df_indexed = ll97_df.set_index("BBL").sort_index().fillna(pd.NA)

        bbl_column = "NYC Borough, Block and Lot (BBL)"
        ll84_df = pd.read_csv(
            self.arguments.ll84_dataset,
            dtype={bbl_column: "string"},
        )
        ll84_df["BBL"] = ll84_df[bbl_column].apply(data_cleansing.normalise_bbl)
        ll84_df_indexed = (
            ll84_df.drop_duplicates()
            .set_index("BBL")
            .sort_index()
            .fillna(pd.NA)
        )

        self._joined_dataset = ll97_df_indexed.join(
            ll84_df_indexed,
            how="left",
        ).fillna(pd.NA)
        self._joined_dataset = data_cleansing.clean_format_numerical_columns(
            self._joined_dataset
        )

    def run(self) -> None:
        """Join the inputs and write the yearly and period CSVs."""
        self._join_ll97_ll84_datasets()
        self._build_yearly_dataset()
        self._build_dataset_for_range_of_years()
