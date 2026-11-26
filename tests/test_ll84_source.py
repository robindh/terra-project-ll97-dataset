import hashlib
import io
import urllib.error
from pathlib import Path

import pandas as pd
import pytest

from terra_project_ll97_dataset.dataset import ll84_source
from terra_project_ll97_dataset.util import common

BBL = common.LL84_BBL


def _csv_bytes(*rows: dict) -> bytes:
    frame = pd.DataFrame(rows)
    return frame.to_csv(index=False).encode("utf-8")


def _row(bbl: str, year: int, electricity: float) -> dict:
    return {
        BBL: bbl,
        "Calendar Year": year,
        "Electricity Use - Grid Purchase (kWh)": electricity,
    }


def test_file_hash_is_the_exact_bytes_and_row_order_does_not_change_rows_hash(tmp_path):
    first = _csv_bytes(
        _row("1000010001", 2023, 1),
        _row("2000020002", 2024, 2),
    )
    reversed_rows = _csv_bytes(
        _row("2000020002", 2024, 2),
        _row("1000010001", 2023, 1),
    )
    path = tmp_path / "ll84.csv"
    path.write_bytes(first)
    disclosure = ll84_source.load_ll84_disclosure(str(path), 2024)

    assert disclosure.file_sha256 == hashlib.sha256(first).hexdigest()
    assert disclosure.calendar_year == 2024
    assert disclosure.rows == 1
    assert disclosure.frame[BBL].tolist() == ["2000020002"]
    other = ll84_source._disclosure_from_bytes(
        reversed_rows,
        "other.csv",
        2024,
        filter_year=True,
    )
    assert other.rows_sha256 == disclosure.rows_sha256
    assert other.file_sha256 != disclosure.file_sha256


def test_download_keeps_the_latest_year_and_records_the_url(monkeypatch):
    payload = _csv_bytes(
        _row("1000010001", 2023, 1),
        _row("1000010001", 2024, 9),
        _row("2000020002", 2024, 4),
    )

    def fake_download(url=ll84_source.LL84_OPEN_DATA_CSV_URL):
        assert url == ll84_source.LL84_OPEN_DATA_CSV_URL
        return payload

    monkeypatch.setattr(ll84_source, "download_ll84_bytes", fake_download)
    disclosure = ll84_source.load_ll84_disclosure(None, None)

    assert disclosure.source == ll84_source.LL84_OPEN_DATA_CSV_URL
    assert disclosure.calendar_year == 2024
    assert disclosure.rows == 2
    assert disclosure.file_sha256 == hashlib.sha256(payload).hexdigest()
    changed = payload.replace(b"2024", b"2030", 1)
    changed_disclosure = ll84_source._disclosure_from_bytes(
        changed,
        disclosure.source,
        None,
        filter_year=True,
    )
    assert changed_disclosure.rows_sha256 != disclosure.rows_sha256


def test_missing_requested_year_names_the_available_years():
    payload = _csv_bytes(_row("1000010001", 2024, 1))
    with pytest.raises(ll84_source.Ll84SourceError, match="Available years: 2024"):
        ll84_source._disclosure_from_bytes(
            payload,
            "ll84.csv",
            1999,
            filter_year=True,
        )


def test_download_failure_names_the_url(monkeypatch):
    def fake_urlopen(request, timeout):
        raise urllib.error.URLError("timed out")

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    with pytest.raises(ll84_source.Ll84SourceError, match="5zyy-y8am"):
        ll84_source.download_ll84_bytes()


def test_manifest_uses_unfiltered_when_no_year_is_requested(tmp_path: Path):
    payload = _csv_bytes(_row("1000010001", 2024, 1))
    path = tmp_path / "ll84.csv"
    path.write_bytes(payload)
    disclosure = ll84_source.load_ll84_disclosure(str(path), None)
    text = disclosure.manifest()
    assert "calendar_year: unfiltered\n" in text
    assert f"file_sha256: {hashlib.sha256(payload).hexdigest()}\n" in text
    assert text.endswith("\n")
    assert "rows_sha256: " in text


def test_rows_hash_ignores_column_order():
    left = pd.read_csv(io.BytesIO(_csv_bytes(_row("1000010001", 2024, 5))))
    right = left.loc[:, list(reversed(left.columns))]
    assert ll84_source.rows_sha256(left) == ll84_source.rows_sha256(right)
