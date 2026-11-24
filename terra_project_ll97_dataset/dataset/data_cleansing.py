"""Normalize BBL keys and numeric LL84 columns before calculations.

A non-numeric energy or floor-area value becomes 0.0 so later arithmetic
does not see NaN. BBL normalization removes dashes, slashes, and
surrounding whitespace so the LL97 and LL84 keys can be joined. A missing
expected LL84 header fails with that column's name.
"""

import pandas as pd

from terra_project_ll97_dataset.util import common

NUMERICAL_LL84_COLUMNS: tuple[str, ...] = tuple(
    energy_type.source_column for energy_type in common.ENERGY_TYPES
) + (
    common.LARGEST_PROPERTY_USE_GFA_SQFT,
    common.SECOND_LARGEST_PROPERTY_USE_GFA_SQFT,
    common.THIRD_LARGEST_PROPERTY_USE_GFA_SQFT,
)

REQUIRED_LL84_COLUMNS: tuple[str, ...] = (
    common.LL84_BBL,
    *NUMERICAL_LL84_COLUMNS,
    common.LARGEST_PROPERTY_USE_TYPE,
)


class MissingLl84ColumnError(Exception):
    """An expected LL84 header is absent.

    Attributes:
        columns: Missing headers, in the order they were required.
    """

    def __init__(self, columns: list[str]) -> None:
        """Store columns and build the error message.

        Args:
            columns: Missing headers. Must contain at least one name.
        """
        self.columns = list(columns)
        if len(self.columns) == 1:
            message = (
                "LL84 data is missing required column: "
                f"{self.columns[0]!r}"
            )
        else:
            names = ", ".join(repr(column) for column in self.columns)
            message = f"LL84 data is missing required columns: {names}"
        super().__init__(message)


def require_ll84_columns(
    frame: pd.DataFrame,
    columns: tuple[str, ...] | list[str],
) -> None:
    """Raise when an expected LL84 header is absent.

    Args:
        frame: LL84 rows, or a joined frame that should contain them.
        columns: Headers that must be present, in report order.

    Raises:
        MissingLl84ColumnError: One or more columns are absent. The
            message names every missing column.
    """
    missing = [column for column in columns if column not in frame.columns]
    if missing:
        raise MissingLl84ColumnError(missing)


def clean_format_numerical_columns(
    clean_joined_df: pd.DataFrame,
) -> pd.DataFrame:
    """Coerce energy use and floor area to floats, in place.

    Args:
        clean_joined_df: Joined building rows. This frame is mutated.

    Returns:
        The same frame. Unparseable cells, including blank cells, are 0.0.

    Raises:
        MissingLl84ColumnError: An energy or floor-area header is absent.
            The message names every missing column.
    """
    require_ll84_columns(clean_joined_df, NUMERICAL_LL84_COLUMNS)

    for column in NUMERICAL_LL84_COLUMNS:
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
