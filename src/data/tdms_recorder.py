"""Streaming TDMS file recorder for continuous OPM data.

Uses ``nptdms.TdmsWriter`` in append mode so that each incoming data
block is written incrementally — no need to hold the entire recording
in memory.
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

import numpy as np
from nptdms import RootObject, GroupObject, ChannelObject, TdmsWriter

logger = logging.getLogger(__name__)


class TdmsRecorder:
    """Write streaming multi-channel data to a ``.tdms`` file.

    Usage
    -----
    ::

        rec = TdmsRecorder()
        rec.start(Path("recording.tdms"), channel_names=["CH-01", …])
        rec.write(block)   # np.ndarray (num_ch × num_samples)
        rec.write(block)
        rec.stop()

    Parameters
    ----------
    group_name : str
        TDMS group under which channels are stored (default ``"ECG"``).
    """

    def __init__(self, group_name: str = "OPM") -> None:
        self._group_name = group_name
        self._writer: TdmsWriter | None = None
        self._filepath: Path | None = None
        self._channel_names: list[str] = []
        self._samples_written: int = 0

    # ── public API ──────────────────────────────────────────────────────── #

    @property
    def is_recording(self) -> bool:
        return self._writer is not None

    @property
    def filepath(self) -> Path | None:
        return self._filepath

    @property
    def samples_written(self) -> int:
        return self._samples_written

    def start(
        self,
        filepath: Path,
        channel_names: list[str],
        sample_rate: float = 1000.0,
    ) -> None:
        """Open a new TDMS file for writing.

        Parameters
        ----------
        filepath : Path
            Destination ``.tdms`` file path.
        channel_names : list[str]
            One name per channel (must match ``data.shape[0]`` in ``write``).
        sample_rate : float
            Sampling rate — stored as a TDMS property for downstream tools.
        """
        if self._writer is not None:
            logger.warning("Recorder already active — stopping previous session.")
            self.stop()

        self._filepath = filepath
        self._channel_names = list(channel_names)
        self._samples_written = 0

        # Root & group metadata
        root = RootObject(properties={
            "description": "OPM OPM Acquisition",
            "datetime": datetime.now().isoformat(),
        })
        group = GroupObject(self._group_name, properties={
            "sample_rate_hz": sample_rate,
            "num_channels": len(channel_names),
        })

        self._writer = TdmsWriter(filepath)
        self._writer.open()
        self._writer.write_segment([root, group])

        logger.info("TDMS recording started → %s", filepath)

    def write(self, data: np.ndarray) -> None:
        """Append a data block to the open TDMS file.

        Parameters
        ----------
        data : np.ndarray
            Shape ``(num_channels, num_samples)``.
        """
        if self._writer is None:
            raise RuntimeError("Recorder is not active — call start() first.")

        num_ch, num_samples = data.shape
        channels = []
        for i in range(num_ch):
            name = self._channel_names[i] if i < len(self._channel_names) else f"CH-{i+1:02d}"
            ch_obj = ChannelObject(self._group_name, name, data[i])
            channels.append(ch_obj)

        self._writer.write_segment(channels)
        self._samples_written += num_samples

    def stop(self) -> None:
        """Flush and close the TDMS file."""
        if self._writer is not None:
            try:
                self._writer.close()
            except Exception:
                logger.exception("Error closing TDMS writer")
            finally:
                self._writer = None
            logger.info(
                "TDMS recording stopped. %d samples written → %s",
                self._samples_written,
                self._filepath,
            )
