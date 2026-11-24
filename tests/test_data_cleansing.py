import pandas as pd
import pytest

from terra_project_ll97_dataset.dataset.data_cleansing import (
    REQUIRED_LL84_COLUMNS,
    MissingLl84ColumnError,
    clean_format_numerical_columns,
    normalise_bbl,
    require_ll84_columns,
)

NUMERIC_COLUMNS = [
    "Electricity Use - Grid Purchase (kWh)",
    "Natural Gas Use (kBtu)",
    "District Steam Use (kBtu)",
    "Fuel Oil #2 Use (kBtu)",
    "Fuel Oil #4 Use (kBtu)",
    "Largest Property Use Type - Gross Floor Area (ft²)",
    "2nd Largest Property Use Type - Gross Floor Area (ft²)",
    "3rd Largest Property Use Type - Gross Floor Area (ft²)",
]


def test_normalise_bbl_removes_dashes_slashes_and_surrounding_whitespace():
    assert normalise_bbl("1-00001-0001") == "1000010001"
    assert normalise_bbl("2/00002/0002") == "2000020002"
    assert normalise_bbl("  3-00003-0003  ") == "3000030003"
    assert normalise_bbl("1-2/3") == "123"


def test_missing_numeric_column_names_that_header():
    source = {column: [1.0] for column in NUMERIC_COLUMNS}
    del source["Natural Gas Use (kBtu)"]
    with pytest.raises(MissingLl84ColumnError, match="Natural Gas Use \\(kBtu\\)"):
        clean_format_numerical_columns(pd.DataFrame(source))


def test_missing_numeric_columns_are_all_named():
    source = {NUMERIC_COLUMNS[0]: [1.0]}
    with pytest.raises(MissingLl84ColumnError) as error:
        clean_format_numerical_columns(pd.DataFrame(source))
    message = str(error.value)
    for column in NUMERIC_COLUMNS[1:]:
        assert column in message


def test_required_ll84_headers_include_bbl_and_property_use_type():
    frame = pd.DataFrame({column: [1.0] for column in NUMERIC_COLUMNS})
    with pytest.raises(MissingLl84ColumnError) as error:
        require_ll84_columns(frame, REQUIRED_LL84_COLUMNS)
    message = str(error.value)
    assert "NYC Borough, Block and Lot (BBL)" in message
    assert "Largest Property Use Type" in message


def test_numeric_coercion_converts_numbers_and_fills_non_numeric_with_zero():
    source = {column: ["12.5", "not-a-number", None, ""] for column in NUMERIC_COLUMNS}
    cleaned = clean_format_numerical_columns(pd.DataFrame(source))

    for column in NUMERIC_COLUMNS:
        assert cleaned[column].tolist() == [12.5, 0.0, 0.0, 0.0]
