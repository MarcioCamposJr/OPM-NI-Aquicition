"""Tests for the signal processing filters (NotchFilter, BandpassFilter)."""

import numpy as np
import pytest

from src.processing.filters import NotchFilter, BandpassFilter


# ── Helpers ──────────────────────────────────────────────────────────────── #

def _make_signal(
    freqs: list[float],
    sample_rate: float = 1000.0,
    duration: float = 2.0,
    amplitudes: list[float] | None = None,
) -> np.ndarray:
    """Generate a multi-sine test signal (single channel, 1-D)."""
    t = np.arange(0, duration, 1.0 / sample_rate)
    if amplitudes is None:
        amplitudes = [1.0] * len(freqs)
    sig = np.zeros_like(t)
    for freq, amp in zip(freqs, amplitudes):
        sig += amp * np.sin(2 * np.pi * freq * t)
    return sig


def _power_at_freq(
    signal: np.ndarray, target_freq: float, sample_rate: float
) -> float:
    """Return the FFT magnitude at the closest bin to *target_freq*."""
    n = len(signal)
    fft_mag = np.abs(np.fft.rfft(signal)) / n
    freqs = np.fft.rfftfreq(n, d=1.0 / sample_rate)
    idx = np.argmin(np.abs(freqs - target_freq))
    return float(fft_mag[idx])


# ── NotchFilter tests ───────────────────────────────────────────────────── #

class TestNotchFilter:
    """Verify the 60 Hz notch filter."""

    def test_attenuates_60hz(self):
        """The 60 Hz component should be heavily attenuated."""
        fs = 1000.0
        sig = _make_signal([10.0, 30.0, 60.0], sample_rate=fs)
        data = sig.reshape(1, -1)  # 1 channel

        filt = NotchFilter(sample_rate=fs, num_channels=1)
        out = filt.apply(data)

        power_60_before = _power_at_freq(sig, 60.0, fs)
        power_60_after = _power_at_freq(out[0], 60.0, fs)

        # 60 Hz should be attenuated by at least 20 dB (factor of 10).
        assert power_60_after < power_60_before / 10.0

    def test_preserves_other_frequencies(self):
        """Frequencies outside the notch band should pass through."""
        fs = 1000.0
        sig = _make_signal([10.0, 30.0], sample_rate=fs)
        data = sig.reshape(1, -1)

        filt = NotchFilter(sample_rate=fs, num_channels=1)
        out = filt.apply(data)

        # Allow 10% loss due to filter rolloff at edges.
        power_10_before = _power_at_freq(sig, 10.0, fs)
        power_10_after = _power_at_freq(out[0], 10.0, fs)
        assert power_10_after > power_10_before * 0.9

    def test_multichannel(self):
        """Filter should process multiple channels independently."""
        fs = 1000.0
        num_ch = 4
        sig = _make_signal([60.0], sample_rate=fs)
        data = np.tile(sig, (num_ch, 1))

        filt = NotchFilter(sample_rate=fs, num_channels=num_ch)
        out = filt.apply(data)

        assert out.shape == data.shape
        for ch in range(num_ch):
            power = _power_at_freq(out[ch], 60.0, fs)
            assert power < 0.05  # very small

    def test_reset_clears_state(self):
        """After reset, filter behaves like a fresh instance."""
        fs = 1000.0
        sig = _make_signal([60.0], sample_rate=fs, duration=0.5)
        data = sig.reshape(1, -1)

        filt = NotchFilter(sample_rate=fs, num_channels=1)
        filt.apply(data)  # first pass — initialises state
        filt.reset()
        out = filt.apply(data)  # should behave like first pass

        assert out.shape == data.shape


# ── BandpassFilter tests ────────────────────────────────────────────────── #

class TestBandpassFilter:
    """Verify the 2–50 Hz bandpass filter."""

    def test_passes_band(self):
        """Frequencies within 2–50 Hz should pass through."""
        fs = 1000.0
        sig = _make_signal([10.0, 25.0, 40.0], sample_rate=fs, duration=2.0)
        data = sig.reshape(1, -1)

        filt = BandpassFilter(sample_rate=fs, num_channels=1)
        out = filt.apply(data)

        # After the initial transient (skip first 500 samples), the power
        # at 25 Hz should be at least 70% of the original.
        trimmed_in = sig[500:]
        trimmed_out = out[0, 500:]

        p_in = _power_at_freq(trimmed_in, 25.0, fs)
        p_out = _power_at_freq(trimmed_out, 25.0, fs)
        assert p_out > p_in * 0.7

    def test_rejects_below_band(self):
        """Frequencies below 2 Hz (e.g. DC, 0.5 Hz) should be attenuated."""
        fs = 1000.0
        # A 0.5 Hz signal
        sig = _make_signal([0.5], sample_rate=fs, duration=4.0)
        data = sig.reshape(1, -1)

        filt = BandpassFilter(sample_rate=fs, num_channels=1)
        out = filt.apply(data)

        p_before = _power_at_freq(sig, 0.5, fs)
        p_after = _power_at_freq(out[0], 0.5, fs)
        assert p_after < p_before * 0.3

    def test_rejects_above_band(self):
        """Frequencies above 50 Hz should be attenuated."""
        fs = 1000.0
        sig = _make_signal([100.0, 200.0], sample_rate=fs, duration=2.0)
        data = sig.reshape(1, -1)

        filt = BandpassFilter(sample_rate=fs, num_channels=1)
        out = filt.apply(data)

        p_before = _power_at_freq(sig, 100.0, fs)
        p_after = _power_at_freq(out[0], 100.0, fs)
        assert p_after < p_before * 0.1

    def test_output_shape(self):
        """Output shape must match input shape."""
        fs = 1000.0
        data = np.random.randn(8, 2000)
        filt = BandpassFilter(sample_rate=fs, num_channels=8)
        out = filt.apply(data)
        assert out.shape == data.shape
