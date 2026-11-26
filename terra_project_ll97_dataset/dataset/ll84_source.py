"""Load an LL84 disclosure from a CSV file or NYC Open Data.

The public export stacks calendar years in one file. A download keeps
one year so the same building is not joined once per year. A local CSV
is filtered only when a year is requested.

Every load records the raw file hash and a hash of the rows actually
used. A later Open Data update changes those hashes even when the URL
stays the same.
"""

import hashlib
import io
import urllib.error
import urllib.request
from dataclasses import dataclass

import pandas as pd

from terra_project_ll97_dataset.util import common

LL84_OPEN_DATA_CSV_URL = (
    "https://data.cityofnewyork.us/api/v3/views/5zyy-y8am/"
    "export.csv?accessType=DOWNLOAD"
)
CALENDAR_YEAR = "Calendar Year"
DOWNLOAD_TIMEOUT_SECONDS = 300
UNFILTERED_YEAR = "unfiltered"


class Ll84SourceError(Exception):
    """The LL84 disclosure could not be read or limited to one year."""


@dataclass(frozen=True)
class Ll84Disclosure:
    """LL84 rows plus the fingerprint of the file they came from.

    Attributes:
        frame: Rows used by the run, after a calendar-year filter.
        source: Local path or the Open Data export URL.
        calendar_year: Year kept, or None when the file was not filtered.
        rows: Number of rows in frame.
        file_sha256: SHA-256 of the exact file bytes that were read.
        rows_sha256: SHA-256 of the rows in frame. Row and column order
            do not change this hash. A changed value means the inputs
            to the calculations changed.
    """

    frame: pd.DataFrame
    source: str
    calendar_year: int | None
    rows: int
    file_sha256: str
    rows_sha256: str

    def manifest(self) -> str:
        """Return the fingerprint written next to the output CSVs.

        Returns:
            Five labeled lines, ending in a newline. The same text is
            printed on stdout.
        """
        if self.calendar_year is None:
            year = UNFILTERED_YEAR
        else:
            year = str(self.calendar_year)
        return (
            f"source: {self.source}\n"
            f"calendar_year: {year}\n"
            f"rows: {self.rows}\n"
            f"file_sha256: {self.file_sha256}\n"
            f"rows_sha256: {self.rows_sha256}\n"
        )


def select_ll84_calendar_year(
    frame: pd.DataFrame,
    year: int | None,
) -> tuple[pd.DataFrame, int]:
    """Keep rows for one calendar year.

    Args:
        frame: LL84 rows. Must contain a Calendar Year column.
        year: Year to keep. The latest year in the file is used when
            this is None.

    Returns:
        The filtered frame and the year that was kept.

    Raises:
        Ll84SourceError: The year column is absent, has no values, or
            does not contain the requested year.
    """
    if CALENDAR_YEAR not in frame.columns:
        raise Ll84SourceError(
            "LL84 data has no 'Calendar Year' column, so a single "
            "year cannot be selected."
        )
    numeric_year = pd.to_numeric(frame[CALENDAR_YEAR], errors="coerce")
    available = sorted(
        int(value) for value in numeric_year.dropna().unique()
    )
    if not available:
        raise Ll84SourceError("LL84 data has no calendar year values.")
    chosen = available[-1] if year is None else year
    if chosen not in available:
        listed = ", ".join(str(value) for value in available)
        raise Ll84SourceError(
            f"LL84 data has no rows for calendar year {chosen}. "
            f"Available years: {listed}."
        )
    selected = frame.loc[numeric_year == chosen].copy()
    return selected, chosen


def read_ll84_csv(payload: bytes) -> pd.DataFrame:
    """Read LL84 CSV bytes, keeping the BBL column as text.

    Args:
        payload: Exact CSV bytes from disk or from the download.

    Returns:
        The disclosure rows.
    """
    return pd.read_csv(
        io.BytesIO(payload),
        dtype={common.LL84_BBL: "string"},
    )


def rows_sha256(frame: pd.DataFrame) -> str:
    """Return a hash of frame that ignores row and column order.

    Args:
        frame: Rows used by the run.

    Returns:
        SHA-256 hex digest of those rows serialized as CSV.
    """
    columns = sorted(frame.columns)
    ordered = frame.loc[:, columns].sort_values(columns, kind="mergesort")
    payload = ordered.to_csv(index=False, lineterminator="\n")
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def download_ll84_bytes(url: str = LL84_OPEN_DATA_CSV_URL) -> bytes:
    """Download the NYC Open Data LL84 export.

    Args:
        url: CSV export address. Defaults to dataset 5zyy-y8am.

    Returns:
        The export bytes, including every calendar year.

    Raises:
        Ll84SourceError: The download failed.
    """
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "terra-project-ll97-dataset"},
    )
    try:
        with urllib.request.urlopen(
            request,
            timeout=DOWNLOAD_TIMEOUT_SECONDS,
        ) as response:
            return response.read()
    except urllib.error.URLError as error:
        raise Ll84SourceError(
            f"Could not download LL84 data from {url}: {error.reason}"
        ) from error


def _disclosure_from_bytes(
    payload: bytes,
    source: str,
    year: int | None,
    filter_year: bool,
) -> Ll84Disclosure:
    """Build a disclosure from exact file bytes.

    Args:
        payload: Exact CSV bytes.
        source: Path or URL recorded in the manifest.
        year: Requested calendar year.
        filter_year: True for a download, and for a local file when a
            year was requested.

    Returns:
        Rows and the fingerprint of payload.

    Raises:
        Ll84SourceError: The requested year cannot be selected.
    """
    frame = read_ll84_csv(payload)
    chosen = None
    if filter_year:
        frame, chosen = select_ll84_calendar_year(frame, year)
    return Ll84Disclosure(
        frame=frame,
        source=source,
        calendar_year=chosen,
        rows=len(frame),
        file_sha256=hashlib.sha256(payload).hexdigest(),
        rows_sha256=rows_sha256(frame),
    )


def load_ll84_disclosure(
    path: str | None,
    year: int | None,
) -> Ll84Disclosure:
    """Load LL84 rows and the fingerprint of the file they came from.

    Args:
        path: Local CSV. None downloads the NYC Open Data export.
        year: Calendar year to keep. A download uses the latest year
            in the file when this is None. A local file is filtered
            only when this is set.

    Returns:
        The disclosure rows and hashes that identify the file and the
        rows used.

    Raises:
        Ll84SourceError: The download failed, or the requested year
            cannot be selected.
    """
    if path is None:
        return _disclosure_from_bytes(
            download_ll84_bytes(),
            LL84_OPEN_DATA_CSV_URL,
            year,
            filter_year=True,
        )
    with open(path, "rb") as handle:
        payload = handle.read()
    return _disclosure_from_bytes(
        payload,
        path,
        year,
        filter_year=year is not None,
    )
