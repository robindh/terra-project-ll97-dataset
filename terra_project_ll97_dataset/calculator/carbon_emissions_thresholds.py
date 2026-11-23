"""Look up the LL97 emissions limit for a building and year.

Only the largest property-use type sets the limit. The second and third
uses are ignored, even when their floor area is larger than the first.
An unknown use type has a limit of zero.
"""

import pandas as pd

from terra_project_ll97_dataset.util import common


def get_carbon_emissions_threshold_by_building_type_and_start_year(
    carbon_emissions_by_building_type_file_path: str,
) -> dict:
    """Load the limit factors from the building-type CSV.

    Args:
        carbon_emissions_by_building_type_file_path: CSV whose first column
            is BuildingType and whose other columns are period start years.

    Returns:
        A mapping of building type to a mapping of period-start year
        (as text) to tCO2e per square foot.
    """
    carbon_thresholds_df = pd.read_csv(
        carbon_emissions_by_building_type_file_path
    )
    carbon_thresholds_df = carbon_thresholds_df.set_index("BuildingType")
    return carbon_thresholds_df.to_dict("index")


def get_carbon_emissions_thresholds(
    carbon_emissions_threshold_lookup_table: dict,
    year: int,
    row: pd.Series,
) -> float:
    """Return one building's emissions limit for one year.

    The limit is the largest-use floor area times that use type's factor
    for the latest period that has already started.

    Args:
        carbon_emissions_threshold_lookup_table: Table from
            get_carbon_emissions_threshold_by_building_type_and_start_year.
        year: Calendar year.
        row: One LL84 building row.

    Returns:
        The limit in tCO2e, or 0.0 when the largest use type is unknown.
    """
    use_type = row[common.LARGEST_PROPERTY_USE_TYPE]
    if use_type not in carbon_emissions_threshold_lookup_table:
        return 0.0

    # Latest period start year that is still less than or equal to year.
    reference_start_year = 0
    for start_year in common.PERIOD_START_YEARS:
        if year < start_year:
            break
        reference_start_year = start_year

    gross_floor_area_sq_feet = float(row[common.LARGEST_PROPERTY_USE_GFA_SQFT])
    factor = carbon_emissions_threshold_lookup_table[use_type][
        str(reference_start_year)
    ]
    return gross_floor_area_sq_feet * factor
