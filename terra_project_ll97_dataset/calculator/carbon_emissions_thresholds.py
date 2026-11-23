import pandas as pd
from terra_project_ll97_dataset.util.common import (
    LARGEST_PROPERTY_USE_GFA_SQFT,
    LARGEST_PROPERTY_USE_TYPE,
    PERIOD_START_YEARS,
)


def get_carbon_emissions_threshold_by_building_type_and_start_year(carbon_emissions_by_building_type_file_path: str):
    carbon_thresholds_df = pd.read_csv(carbon_emissions_by_building_type_file_path)
    carbon_thresholds_df = carbon_thresholds_df.set_index("BuildingType")
    carbon_emissions_threshold_lookup_table = carbon_thresholds_df.to_dict('index')
    return carbon_emissions_threshold_lookup_table


def get_carbon_emissions_thresholds(carbon_emissions_threshold_lookup_table, year, row):
    if row[LARGEST_PROPERTY_USE_TYPE] not in carbon_emissions_threshold_lookup_table.keys():
        return 0.0

    # find the start year for the range this year falls in
    reference_start_year = 0
    for start_year in PERIOD_START_YEARS:
        if year < start_year:
            break
        reference_start_year = start_year

    gross_floor_area_sq_feet = float(row[LARGEST_PROPERTY_USE_GFA_SQFT])
    carbon_emissions_threshold_per_sq_foot = carbon_emissions_threshold_lookup_table[row[LARGEST_PROPERTY_USE_TYPE]][
        str(reference_start_year)]

    return gross_floor_area_sq_feet * carbon_emissions_threshold_per_sq_foot
