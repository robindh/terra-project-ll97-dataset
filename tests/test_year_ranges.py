from terra_project_ll97_dataset.util.common import get_year_ranges


def test_year_periods_keep_current_labels_and_ranges():
    periods = get_year_ranges()

    assert [(period.label, list(period.years)) for period in periods] == [
        ("2024-2029", list(range(2024, 2030))),
        ("2030-2034", list(range(2030, 2035))),
        ("2035-2039", list(range(2035, 2040))),
        ("2040-2049", list(range(2040, 2050))),
        ("2050+", list(range(2050, 2051))),
    ]
