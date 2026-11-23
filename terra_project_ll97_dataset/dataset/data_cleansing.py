"""Normalize BBL keys and numeric LL84 columns before calculations.

A non-numeric energy or floor-area value becomes 0.0 so later arithmetic
does not see NaN. BBL normalization removes dashes, slashes, and
surrounding whitespace so the LL97 and LL84 keys can be joined.
"""

import pandas as pd

from terra_project_ll97_dataset.util import common


def clean_format_numerical_columns(
    clean_joined_df: pd.DataFrame,
) -> pd.DataFrame:
    """Coerce energy use and floor area to floats, in place.

    Args:
        clean_joined_df: Joined building rows. This frame is mutated.

    Returns:
        The same frame. Unparseable cells, including blank cells, are 0.0.
    """
    columns_to_convert = [
        energy_type.source_column for energy_type in common.ENERGY_TYPES
    ] + [
        common.LARGEST_PROPERTY_USE_GFA_SQFT,
        common.SECOND_LARGEST_PROPERTY_USE_GFA_SQFT,
        common.THIRD_LARGEST_PROPERTY_USE_GFA_SQFT,
    ]

    for column in columns_to_convert:
        numeric = pd.to_numeric(clean_joined_df[column], errors="coerce")
        clean_joined_df[column] = numeric.fillna(0.0)

    return clean_joined_df


def normalise_bbl(key: str) -> str:
    """Return a BBL key with dashes, slashes, and outer space removed.

    Args:
        key: Borough-block-lot text from either input file.

    Returns:
        The join key. Interior digits are left unchanged.
    """
    return key.replace("-", "").replace("/", "").strip()
