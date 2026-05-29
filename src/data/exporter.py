"""Export acquired OPM data to CSV and Excel formats.

Provides a simple, stateless utility class that converts NumPy arrays
into tabular files using ``pandas``.
"""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class DataExporter:
    """Export multi-channel OPM data to spreadsheet formats.

    All methods are stateless — they receive the data, write the file,
    and return.  The caller is responsible for accumulating the data
    buffer (e.g. from ``TdmsRecorder`` or an in-memory ring buffer).
    """

    @staticmethod
    def to_csv(
        data: np.ndarray,
        filepath: Path,
        channel_names: list[str] | None = None,
        sample_rate: float = 1000.0,
    ) -> None:
        """Save data to a CSV file.

        Parameters
        ----------
        data : np.ndarray
            Shape ``(num_channels, num_samples)``.
        filepath : Path
            Destination ``.csv`` path.
        channel_names : list[str] | None
            Column headers.  If ``None``, defaults to CH-01 … CH-NN.
        sample_rate : float
            Used to build a time-index column (seconds).
        """
        df = DataExporter._to_dataframe(data, channel_names, sample_rate)
        df.to_csv(filepath, index_label="Time_s")
        logger.info("CSV exported → %s  (%d rows × %d cols)", filepath, *df.shape)

    @staticmethod
    def to_excel(
        data: np.ndarray,
        filepath: Path,
        channel_names: list[str] | None = None,
        sample_rate: float = 1000.0,
    ) -> None:
        """Save data to an Excel (``.xlsx``) file.

        Parameters
        ----------
        data : np.ndarray
            Shape ``(num_channels, num_samples)``.
        filepath : Path
            Destination ``.xlsx`` path.
        channel_names : list[str] | None
            Column headers.
        sample_rate : float
            Used to build a time-index column (seconds).
        """
        df = DataExporter._to_dataframe(data, channel_names, sample_rate)
        df.to_excel(filepath, index_label="Time_s", engine="openpyxl")
        logger.info("Excel exported → %s  (%d rows × %d cols)", filepath, *df.shape)

    # ── internal helper ─────────────────────────────────────────────────── #

    @staticmethod
    def _to_dataframe(
        data: np.ndarray,
        channel_names: list[str] | None,
        sample_rate: float,
    ) -> pd.DataFrame:
        """Convert a (num_ch × num_samples) array to a DataFrame.

        The index is a time vector in seconds; columns are channel names.
        """
        num_ch, num_samples = data.shape
        if channel_names is None:
            channel_names = [f"CH-{i + 1:02d}" for i in range(num_ch)]

        time = np.arange(num_samples) / sample_rate
        df = pd.DataFrame(data.T, index=time, columns=channel_names)
        return df
