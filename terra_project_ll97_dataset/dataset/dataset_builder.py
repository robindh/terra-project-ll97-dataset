"""
Dataset builder for LL97 compliance analysis.
This module processes LL97 and LL84 datasets to calculate carbon emissions,
energy costs, and penalties for buildings in New York City.
"""

import argparse
import os.path
from typing import Callable

import pandas as pd

from terra_project_ll97_dataset.calculator.carbon_emissions import get_carbon_emissions, \
    get_carbon_emissions_by_year_and_energy_type
from terra_project_ll97_dataset.calculator.carbon_emissions_thresholds import \
    get_carbon_emissions_threshold_by_building_type_and_start_year, get_carbon_emissions_thresholds
from terra_project_ll97_dataset.calculator.cost_of_energy import get_cost_of_energy, \
    get_cost_of_energy_by_year_and_energy_type
from terra_project_ll97_dataset.calculator.penalties import calculate_penalties
from terra_project_ll97_dataset.dataset.data_cleansing import normalise_bbl, clean_format_numerical_columns
from terra_project_ll97_dataset.util.common import ANALYSIS_END_YEAR, ANALYSIS_START_YEAR, get_year_ranges


def _avg_over_year_range(year_range: range, row: pd.Series, func: Callable[[int, pd.Series], float]) -> float:
    if len(year_range) == 0:
        return 0.0

    total_val = 0.0
    for year in year_range:
        total_val += func(year, row)
    return total_val / len(year_range)


class DatasetBuilder:
    def __init__(self, arguments: argparse.Namespace):
        self.arguments = arguments
        self.start_year = ANALYSIS_START_YEAR
        self.end_year = ANALYSIS_END_YEAR

        self._carbon_emissions_lookup_table = get_carbon_emissions_by_year_and_energy_type(
            self.start_year, self.end_year)
        self._cost_of_energy_lookup_table = get_cost_of_energy_by_year_and_energy_type(
            self.start_year, self.end_year)
        self._carbon_emissions_threshold_lookup_table = (
            get_carbon_emissions_threshold_by_building_type_and_start_year(
                arguments.carbon_emissions_by_building_type))

    def _get_carbon_emissions(self, year: int, row: pd.Series) -> float:
        return get_carbon_emissions(self._carbon_emissions_lookup_table, year, row)

    def _get_cost_of_energy(self, year: int, row: pd.Series) -> float:
        return get_cost_of_energy(self._cost_of_energy_lookup_table, year, row)

    def _get_carbon_emissions_thresholds(self, year: int, row: pd.Series) -> float:
        return get_carbon_emissions_thresholds(self._carbon_emissions_threshold_lookup_table, year, row)

    def _add_emissions_cost_threshold_and_penalty(self, df: pd.DataFrame, column_prefix: str, name_suffix: str, compute) -> None:
        """Add carbon emissions, energy cost, the emissions threshold, and the penalty.

        ``name_suffix`` is empty for one year and ``_per_year`` for a period average.
        """
        emissions_column = f"{column_prefix}_carbon_emissions{name_suffix}"
        cost_column = f"{column_prefix}_cost_of_energy{name_suffix}"
        threshold_column = f"{column_prefix}_carbon_emissions_threshold{name_suffix}"
        penalty_column = f"{column_prefix}_estimated_penalty{name_suffix}"

        df[emissions_column] = df.apply(lambda row: compute(row, self._get_carbon_emissions), axis=1)
        df[cost_column] = df.apply(lambda row: compute(row, self._get_cost_of_energy), axis=1)
        df[threshold_column] = df.apply(lambda row: compute(row, self._get_carbon_emissions_thresholds), axis=1)
        df[penalty_column] = df.apply(
            lambda row: calculate_penalties(row, emissions_column, threshold_column),
            axis=1,
        )

    def _build_yearly_dataset(self):
        df_with_yearly_values = self._joined_dataset.copy()

        for year in range(self.start_year, self.end_year + 1):
            self._add_emissions_cost_threshold_and_penalty(
                df_with_yearly_values,
                str(year),
                "",
                lambda row, func, year=year: func(year, row),
            )

        df_with_yearly_values.to_csv(
            os.path.join(self.arguments.output_dir, "dataset_estimated_emissions_cost_penalties_for_each_year.csv"))

    def _build_dataset_for_range_of_years(self):
        df_for_range_of_years = self._joined_dataset.copy()

        for period in get_year_ranges():
            self._add_emissions_cost_threshold_and_penalty(
                df_for_range_of_years,
                period.label,
                "_per_year",
                lambda row, func, years=period.years: _avg_over_year_range(years, row, func),
            )

        df_for_range_of_years.to_csv(
            os.path.join(self.arguments.output_dir, "dataset_estimated_emissions_cost_penalties_for_year_range.csv"))

    def _join_ll97_ll84_datasets(self):
        ll97_df = pd.read_csv(self.arguments.ll97_dataset, dtype={"BBL": 'string'})
        ll97_df["BBL"] = ll97_df["BBL"].apply(normalise_bbl)
        ll97_df_indexed = ll97_df.set_index("BBL").sort_index().fillna(pd.NA)

        ll84_df = pd.read_csv(self.arguments.ll84_dataset, dtype={"NYC Borough, Block and Lot (BBL)": 'string'})
        ll84_df["BBL"] = ll84_df["NYC Borough, Block and Lot (BBL)"].apply(normalise_bbl)
        ll84_df_indexed = ll84_df.drop_duplicates().set_index("BBL").sort_index().fillna(pd.NA)

        self._joined_dataset = ll97_df_indexed.join(ll84_df_indexed, how='left').fillna(pd.NA)
        self._joined_dataset = clean_format_numerical_columns(self._joined_dataset)

    def run(self):
        self._join_ll97_ll84_datasets()
        self._build_yearly_dataset()
        self._build_dataset_for_range_of_years()
