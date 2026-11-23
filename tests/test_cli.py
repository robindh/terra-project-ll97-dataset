import os
import subprocess
import sys
from pathlib import Path

import pandas as pd
import pandas.testing as pdt

from terra_project_ll97_dataset.arguments import BuildDatasetArguments

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).resolve().parent / "fixtures"
YEARLY_NAME = "dataset_estimated_emissions_cost_penalties_for_each_year.csv"
RANGE_NAME = "dataset_estimated_emissions_cost_penalties_for_year_range.csv"


def _read_frame(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, index_col="BBL", dtype={"BBL": "string"})


def test_help_exits_zero_and_still_accepts_verbose():
    result = subprocess.run(
        [sys.executable, "-m", "terra_project_ll97_dataset.build_dataset", "--help"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "--ll97_dataset" in result.stdout
    assert "--ll84_dataset" in result.stdout
    assert "--output_dir" in result.stdout
    assert "--verbose" in result.stdout


def test_missing_output_directory_is_created(tmp_path):
    output_dir = tmp_path / "new" / "out"
    assert not output_dir.exists()
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "terra_project_ll97_dataset.build_dataset",
            "--ll97_dataset",
            str(FIXTURES / "ll97_synthetic.csv"),
            "--ll84_dataset",
            str(FIXTURES / "ll84_synthetic.csv"),
            "--output_dir",
            str(output_dir),
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    pdt.assert_frame_equal(
        _read_frame(output_dir / YEARLY_NAME),
        _read_frame(FIXTURES / YEARLY_NAME),
        check_exact=True,
    )
    pdt.assert_frame_equal(
        _read_frame(output_dir / RANGE_NAME),
        _read_frame(FIXTURES / RANGE_NAME),
        check_exact=True,
    )


def test_output_path_that_is_a_file_is_rejected(tmp_path):
    output_file = tmp_path / "not-a-directory"
    output_file.write_text("x")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "terra_project_ll97_dataset.build_dataset",
            "--ll97_dataset",
            str(FIXTURES / "ll97_synthetic.csv"),
            "--ll84_dataset",
            str(FIXTURES / "ll84_synthetic.csv"),
            "--output_dir",
            str(output_file),
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0
    assert "not a valid path" in result.stderr
    assert output_file.read_text() == "x"


def test_missing_input_file_is_rejected(tmp_path):
    output_dir = tmp_path / "out"
    output_dir.mkdir()
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "terra_project_ll97_dataset.build_dataset",
            "--ll97_dataset",
            str(tmp_path / "missing.csv"),
            "--ll84_dataset",
            str(FIXTURES / "ll84_synthetic.csv"),
            "--output_dir",
            str(output_dir),
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0
    assert "not a valid file" in result.stderr


def test_default_threshold_from_repo_root_is_the_shipped_file(tmp_path, monkeypatch):
    monkeypatch.chdir(REPO_ROOT)
    historical = os.path.abspath(
        "./terra_project_ll97_dataset/data/carbon_thresholds_by_building_type.csv"
    )
    output_dir = tmp_path / "out"
    output_dir.mkdir()
    args = BuildDatasetArguments().parser.parse_args(
        [
            "--ll97_dataset",
            str(FIXTURES / "ll97_synthetic.csv"),
            "--ll84_dataset",
            str(FIXTURES / "ll84_synthetic.csv"),
            "--output_dir",
            str(output_dir),
        ]
    )
    assert os.path.isfile(args.carbon_emissions_by_building_type)
    assert os.path.samefile(args.carbon_emissions_by_building_type, historical)


def test_run_from_another_working_directory_matches_golden(tmp_path):
    output_dir = tmp_path / "out"
    output_dir.mkdir()
    other_cwd = tmp_path / "elsewhere"
    other_cwd.mkdir()
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "terra_project_ll97_dataset.build_dataset",
            "--ll97_dataset",
            str(FIXTURES / "ll97_synthetic.csv"),
            "--ll84_dataset",
            str(FIXTURES / "ll84_synthetic.csv"),
            "--output_dir",
            str(output_dir),
            "--verbose",
        ],
        cwd=other_cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout == ""
    pdt.assert_frame_equal(
        _read_frame(output_dir / YEARLY_NAME),
        _read_frame(FIXTURES / YEARLY_NAME),
        check_exact=True,
    )
    pdt.assert_frame_equal(
        _read_frame(output_dir / RANGE_NAME),
        _read_frame(FIXTURES / RANGE_NAME),
        check_exact=True,
    )
