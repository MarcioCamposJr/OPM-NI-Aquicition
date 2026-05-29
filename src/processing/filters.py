"""Digital IIR filters for real-time ECG signal conditioning.

All filters use Second-Order Sections (SOS) representation for
numerical stability and maintain internal state (``zi``) so they
can be applied continuously to streaming data blocks.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

import numpy as np
from scipy.signal import iirfilter, sosfilt, sosfilt_zi


# ── Base filter ──────────────────────────────────────────────────────────── #

class _StreamingFilter:
    """Base class for a stateful SOS filter applied per-channel.

    Subclasses only need to call ``super().__init__(...)`` with the
    appropriate SOS coefficients.  The ``apply`` method handles
    multi-channel streaming with independent per-channel state.

    Parameters
    ----------
    sos : np.ndarray
        Second-order-sections coefficient array (shape ``(n_sections, 6)``).
    num_channels : int
        Number of independent channels whose state is tracked.
    """

    def __init__(self, sos: np.ndarray, num_channels: int) -> None:
        self._sos = sos
        self._num_channels = num_channels
        # ``sosfilt_zi`` returns shape (n_sections, 2).
        # We replicate it for each channel → list of (n_sections, 2) arrays.
        zi_template = sosfilt_zi(sos)  # (n_sections, 2)
        self._zi: list[np.ndarray] = [zi_template.copy() for _ in range(num_channels)]
        self._initialized = False

    def reset(self) -> None:
        """Reset filter state for all channels (e.g. on new acquisition)."""
        zi_template = sosfilt_zi(self._sos)
        self._zi = [zi_template.copy() for _ in range(self._num_channels)]
        self._initialized = False

    def apply(self, data: np.ndarray) -> np.ndarray:
        """Apply the filter to a multi-channel block.

        Parameters
        ----------
        data : np.ndarray
            Input array of shape ``(num_channels, num_samples)``.

        Returns
        -------
        np.ndarray
            Filtered array, same shape as *data*.
        """
        num_ch, num_samples = data.shape
        out = np.empty_like(data)

        # On the very first block, scale ``zi`` so the initial transient
        # matches the first sample of each channel.
        if not self._initialized:
            for ch in range(num_ch):
                self._zi[ch] = self._zi[ch] * data[ch, 0]
            self._initialized = True

        for ch in range(num_ch):
            out[ch], self._zi[ch] = sosfilt(
                self._sos, data[ch], zi=self._zi[ch]
            )
        return out


# ── Notch (Band-stop) filter — 60 Hz rejection ──────────────────────────── #

class NotchFilter(_StreamingFilter):
    """IIR Butterworth band-stop filter for power-line noise rejection.

    Default design: **order 2**, rejecting **59–61 Hz** (i.e. the 60 Hz
    fundamental of the AC power grid).

    Parameters
    ----------
    sample_rate : float
        Sampling frequency in Hz.
    low_freq : float
        Lower edge of the stop-band (Hz).
    high_freq : float
        Upper edge of the stop-band (Hz).
    order : int
        Filter order (Butterworth).
    num_channels : int
        Number of independent channels.
    """

    def __init__(
        self,
        sample_rate: float = 1000.0,
        low_freq: float = 59.0,
        high_freq: float = 61.0,
        order: int = 2,
        num_channels: int = 24,
    ) -> None:
        sos = iirfilter(
            N=order,
            Wn=[low_freq, high_freq],
            btype="bandstop",
            ftype="butter",
            fs=sample_rate,
            output="sos",
        )
        super().__init__(sos, num_channels)

        # Store design parameters for introspection / UI display.
        self.sample_rate = sample_rate
        self.low_freq = low_freq
        self.high_freq = high_freq
        self.order = order


# ── Bandpass filter — 2–50 Hz ECG band ───────────────────────────────────── #

class BandpassFilter(_StreamingFilter):
    """IIR Butterworth band-pass filter for ECG signal conditioning.

    Default design: **order 4**, passing **2–50 Hz**.

    Parameters
    ----------
    sample_rate : float
        Sampling frequency in Hz.
    low_freq : float
        Lower cut-off frequency (Hz).
    high_freq : float
        Upper cut-off frequency (Hz).
    order : int
        Filter order (Butterworth).
    num_channels : int
        Number of independent channels.
    """

    def __init__(
        self,
        sample_rate: float = 1000.0,
        low_freq: float = 2.0,
        high_freq: float = 50.0,
        order: int = 4,
        num_channels: int = 24,
    ) -> None:
        sos = iirfilter(
            N=order,
            Wn=[low_freq, high_freq],
            btype="bandpass",
            ftype="butter",
            fs=sample_rate,
            output="sos",
        )
        super().__init__(sos, num_channels)

        self.sample_rate = sample_rate
        self.low_freq = low_freq
        self.high_freq = high_freq
        self.order = order
