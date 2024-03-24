import pandas as pd


def clean_format_numerical_columns(clean_joined_df: pd.DataFrame) -> pd.DataFrame:
    # Convert to numeric columns and coerce
    columns_to_convert = [
        "Electricity Use - Grid Purchase (kWh)",
        "Natural Gas Use (kBtu)",
        "District Steam Use (kBtu)",
        "Fuel Oil #2 Use (kBtu)",
        "Fuel Oil #4 Use (kBtu)",
        "Largest Property Use Type - Gross Floor Area (ft²)",
        "2nd Largest Property Use Type - Gross Floor Area (ft²)",
        "3rd Largest Property Use Type - Gross Floor Area (ft²)",
    ]

    for column in columns_to_convert:
        clean_joined_df[column] = pd.to_numeric(clean_joined_df[column], errors='coerce').fillna(0.0)

    return clean_joined_df


def normalise_bbl(key: str) -> str:
    return key.replace("-", "").replace("/", "").strip()
