from terra_project_ll97_dataset.util.common import get_year_ranges


def test_get_year_ranges_returns_inclusive_bounds_and_open_final_period():
    # The final period is the (2050, -1) sentinel. DatasetBuilder turns that
    # into range(2050, 2051) and the label 2050+; this locks the tuple the
    # builder still consumes.
    assert get_year_ranges() == [
        (2024, 2029),
        (2030, 2034),
        (2035, 2039),
        (2040, 2049),
        (2050, -1),
    ]
