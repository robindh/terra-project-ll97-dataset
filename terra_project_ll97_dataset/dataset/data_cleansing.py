import pandas as pd

from terra_project_ll97_dataset.util.common import (
    ENERGY_TYPES,
    LARGEST_PROPERTY_USE_GFA_SQFT,
    SECOND_LARGEST_PROPERTY_USE_GFA_SQFT,
    THIRD_LARGEST_PROPERTY_USE_GFA_SQFT,
)


def clean_format_numerical_columns(clean_joined_df: pd.DataFrame) -> pd.DataFrame:
    columns_to_convert = [energy_type.source_column for energy_type in ENERGY_TYPES] + [
        LARGEST_PROPERTY_USE_GFA_SQFT,
        SECOND_LARGEST_PROPERTY_USE_GFA_SQFT,
        THIRD_LARGEST_PROPERTY_USE_GFA_SQFT,
    ]

    for column in columns_to_convert:
        clean_joined_df[column] = pd.to_numeric(clean_joined_df[column], errors='coerce').fillna(0.0)

    return clean_joined_df


def normalise_bbl(key: str) -> str:
    return key.replace("-", "").replace("/", "").strip()
