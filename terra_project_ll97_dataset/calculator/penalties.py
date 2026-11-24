"""Estimate the Local Law 97 penalty for emissions above the limit.

Emissions at or below the limit have no penalty. Each tonne of CO2
equivalent above the limit is charged at PENALTY_DOLLARS_PER_TCO2E.
"""

import pandas as pd

from terra_project_ll97_dataset.util import common


def calculate_penalty_amounts(
    emissions: pd.Series,
    limits: pd.Series,
) -> pd.Series:
    """Return penalties for aligned emissions and limit values.

    This is calculate_penalties for a whole column. Emissions at or below
    the limit are zero. Each tonne above the limit is charged at
    PENALTY_DOLLARS_PER_TCO2E.

    Args:
        emissions: Emissions in tCO2e, one building per row.
        limits: Limits in tCO2e, aligned with emissions.

    Returns:
        Penalty dollars, aligned with emissions.
    """
    excess = emissions - limits
    charged = common.PENALTY_DOLLARS_PER_TCO2E * excess
    return charged.where(emissions > limits, 0.0)


def calculate_penalties(
    row: pd.Series,
    carbon_emmissions_column_name: str,
    carbon_emissions_threshold_column_name: str,
) -> float:
    """Return the penalty for one building row.

    The emissions column parameter keeps its historical spelling.

    Args:
        row: A row that already has emissions and threshold columns.
        carbon_emmissions_column_name: Column holding emissions in tCO2e.
        carbon_emissions_threshold_column_name: Column holding the limit
            in tCO2e.

    Returns:
        Zero when emissions are at or below the limit. Otherwise the
        excess tonnes times the statutory dollars per tCO2e.
    """
    emissions = row[carbon_emmissions_column_name]
    limit = row[carbon_emissions_threshold_column_name]
    if emissions <= limit:
        return 0.0

    return common.PENALTY_DOLLARS_PER_TCO2E * (emissions - limit)
