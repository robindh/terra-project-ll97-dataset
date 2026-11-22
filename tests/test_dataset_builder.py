import argparse
from pathlib import Path

import pandas as pd
import pandas.testing as pdt

from terra_project_ll97_dataset.dataset.dataset_builder import DatasetBuilder

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).resolve().parent / "fixtures"
THRESHOLD_CSV = (
    REPO_ROOT / "terra_project_ll97_dataset" / "data" / "carbon_thresholds_by_building_type.csv"
)
YEARLY_NAME = "dataset_estimated_emissions_cost_penalties_for_each_year.csv"
RANGE_NAME = "dataset_estimated_emissions_cost_penalties_for_year_range.csv"

# Normalized BBLs for the three synthetic buildings.
OFFICE = "1000010001"
MULTIFAMILY = "2000020002"
UNKNOWN = "3000030003"


def test_dataset_builder_imports():
    assert DatasetBuilder.__module__ == "terra_project_ll97_dataset.dataset.dataset_builder"


def _read_frame(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, index_col="BBL", dtype={"BBL": "string"})


def _build(output_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    arguments = argparse.Namespace(
        ll97_dataset=str(FIXTURES / "ll97_synthetic.csv"),
        ll84_dataset=str(FIXTURES / "ll84_synthetic.csv"),
        carbon_emissions_by_building_type=str(THRESHOLD_CSV),
        output_dir=str(output_dir),
    )
    DatasetBuilder(arguments).run()
    return _read_frame(output_dir / YEARLY_NAME), _read_frame(output_dir / RANGE_NAME)


def test_synthetic_end_to_end_matches_hand_checked_golden(tmp_path):
    yearly, ranges = _build(tmp_path)

    assert list(yearly.index) == [OFFICE, MULTIFAMILY, UNKNOWN]
    assert yearly.index.name == "BBL"

    # Office, 20,000 kWh only, 1,000 ft². 2024 factor 0.29 kgCO2e/kWh -> 5.8 tCO2e,
    # under the 7.6 tCO2e limit (1,000 * 0.0076), so the penalty is zero.
    # The 50,000 ft² second use does not change the limit.
    office = yearly.loc[OFFICE]
    assert office["2024_carbon_emissions"] == 5.8
    assert office["2024_cost_of_energy"] == 4400.0
    assert office["2024_carbon_emissions_threshold"] == 1000 * 0.0076
    assert office["2024_estimated_penalty"] == 0.0
    assert office["2029_carbon_emissions"] == 5.8
    assert office["2nd Largest Property Use Type - Gross Floor Area (ft²)"] == 50000.0

    # From 2030 the electricity factor is 0.15 kgCO2e/kWh -> 3.0 tCO2e, over the
    # tighter Office limits. 2050's limit is zero.
    assert office["2030_carbon_emissions"] == 3.0
    assert office["2030_carbon_emissions_threshold"] == 2.7
    assert office["2035_carbon_emissions_threshold"] == 1.7
    assert office["2040_carbon_emissions_threshold"] == 0.6
    assert office["2050_carbon_emissions"] == 3.0
    assert office["2050_carbon_emissions_threshold"] == 0.0
    assert office["2030_estimated_penalty"] > 0.0
    assert office["2050_estimated_penalty"] > 0.0

    # Multifamily stays under its limit until the 2050 zero limit.
    multifamily = yearly.loc[MULTIFAMILY]
    assert multifamily["2024_carbon_emissions_threshold"] == 50000 * 0.0067
    assert multifamily["2030_carbon_emissions_threshold"] == 50000 * 0.0033
    assert multifamily["2035_carbon_emissions_threshold"] == 50000 * 0.0027
    assert multifamily["2040_carbon_emissions_threshold"] == 50000 * 0.0021
    assert multifamily["2050_carbon_emissions_threshold"] == 0.0
    assert multifamily["2024_estimated_penalty"] == 0.0
    assert multifamily["2049_estimated_penalty"] == 0.0

    # Unknown use type has a zero limit. Non-numeric electricity and floor area
    # become 0. 1,000 kBtu of gas is 10 therms * 0.005 tCO2e/therm = 0.05 tCO2e,
    # and the penalty is $268 per tCO2e.
    unknown = yearly.loc[UNKNOWN]
    assert unknown["Largest Property Use Type"] == "Spaceship"
    assert unknown["Electricity Use - Grid Purchase (kWh)"] == 0.0
    assert unknown["Largest Property Use Type - Gross Floor Area (ft²)"] == 0.0
    assert unknown["Natural Gas Use (kBtu)"] == 1000.0
    assert unknown["2024_carbon_emissions"] == 0.05
    assert unknown["2024_carbon_emissions_threshold"] == 0.0
    assert unknown["2024_cost_of_energy"] == 9.97
    assert unknown["2024_estimated_penalty"] == 268 * 0.05
    assert unknown["2050_estimated_penalty"] == 268 * 0.05

    # Join keeps the original LL84 BBL text; the index is the normalized key.
    assert yearly["NYC Borough, Block and Lot (BBL)"].tolist() == [
        "1000010001",
        "2/00002/0002",
        " 3-00003-0003 ",
    ]

    # 2050+ averages the single year 2050, the same range the builder uses today.
    for bbl in (OFFICE, MULTIFAMILY, UNKNOWN):
        assert ranges.loc[bbl, "2050+_carbon_emissions_per_year"] == yearly.loc[bbl, "2050_carbon_emissions"]
        assert ranges.loc[bbl, "2050+_cost_of_energy_per_year"] == yearly.loc[bbl, "2050_cost_of_energy"]
        assert (
            ranges.loc[bbl, "2050+_carbon_emissions_threshold_per_year"]
            == yearly.loc[bbl, "2050_carbon_emissions_threshold"]
        )
        assert ranges.loc[bbl, "2050+_estimated_penalty_per_year"] == yearly.loc[bbl, "2050_estimated_penalty"]

    pdt.assert_frame_equal(yearly, _read_frame(FIXTURES / YEARLY_NAME), check_exact=True)
    pdt.assert_frame_equal(ranges, _read_frame(FIXTURES / RANGE_NAME), check_exact=True)
