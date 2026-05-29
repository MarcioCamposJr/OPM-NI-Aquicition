"""Orchestrator for the ECG signal-processing pipeline.

``EcgProcessor`` chains multiple filters and applies them in the
correct order to each incoming data block.  It owns the filter
instances and exposes high-level ``process`` / ``reset`` methods.
"""

from __future__ import annotations

import logging

import numpy as np

from src.processing.filters import BandpassFilter, NotchFilter

logger = logging.getLogger(__name__)


class EcgProcessor:
    """Real-time ECG signal conditioning pipeline.

    The processing chain is:

    1. **Notch filter** — removes 60 Hz power-line interference.
    2. **Bandpass filter** — isolates the 2–50 Hz ECG band.

    Both filters maintain per-channel streaming state so they can be
    fed consecutive blocks without transient artefacts at the boundaries.

    Parameters
    ----------
    sample_rate : float
        Sampling rate in Hz (must match the DAQ configuration).
    num_channels : int
        Number of analog input channels.
    notch_enabled : bool
        Whether to apply the notch filter.
    bandpass_enabled : bool
        Whether to apply the bandpass filter.
    notch_low : float
        Notch filter lower edge (Hz).
    notch_high : float
        Notch filter upper edge (Hz).
    notch_order : int
        Notch filter order.
    bp_low : float
        Bandpass filter lower cut-off (Hz).
    bp_high : float
        Bandpass filter upper cut-off (Hz).
    bp_order : int
        Bandpass filter order.
    """

    def __init__(
        self,
        sample_rate: float = 1000.0,
        num_channels: int = 24,
        *,
        notch_enabled: bool = True,
        bandpass_enabled: bool = True,
        notch_low: float = 59.0,
        notch_high: float = 61.0,
        notch_order: int = 2,
        bp_low: float = 2.0,
        bp_high: float = 50.0,
        bp_order: int = 4,
    ) -> None:
        self._sample_rate = sample_rate
        self._num_channels = num_channels

        self.notch_enabled = notch_enabled
        self.bandpass_enabled = bandpass_enabled

        self._notch = NotchFilter(
            sample_rate=sample_rate,
            low_freq=notch_low,
            high_freq=notch_high,
            order=notch_order,
            num_channels=num_channels,
        )
        self._bandpass = BandpassFilter(
            sample_rate=sample_rate,
            low_freq=bp_low,
            high_freq=bp_high,
            order=bp_order,
            num_channels=num_channels,
        )
        logger.info(
            "EcgProcessor initialised: fs=%.0f Hz, %d ch, "
            "notch=%s (%.0f–%.0f Hz, order %d), "
            "bp=%s (%.0f–%.0f Hz, order %d)",
            sample_rate,
            num_channels,
            notch_enabled,
            notch_low,
            notch_high,
            notch_order,
            bandpass_enabled,
            bp_low,
            bp_high,
            bp_order,
        )

    # ── public API ──────────────────────────────────────────────────────── #

    def process(self, raw: np.ndarray) -> np.ndarray:
        """Apply the full filter chain to a raw data block.

        Parameters
        ----------
        raw : np.ndarray
            Raw voltage data, shape ``(num_channels, num_samples)``.

        Returns
        -------
        np.ndarray
            Filtered data, same shape.
        """
        data = raw

        if self.notch_enabled:
            data = self._notch.apply(data)

        if self.bandpass_enabled:
            data = self._bandpass.apply(data)

        return data

    def reset(self) -> None:
        """Reset all filter states (call before starting a new acquisition)."""
        self._notch.reset()
        self._bandpass.reset()
        logger.debug("EcgProcessor filter states reset.")

    # ── properties for UI introspection ─────────────────────────────────── #

    @property
    def notch_filter(self) -> NotchFilter:
        return self._notch

    @property
    def bandpass_filter(self) -> BandpassFilter:
        return self._bandpass

    @property
    def sample_rate(self) -> float:
        return self._sample_rate

    @property
    def num_channels(self) -> int:
        return self._num_channels
