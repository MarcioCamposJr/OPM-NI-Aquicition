"""Tests for the OpmProcessor pipeline."""

import numpy as np
import pytest

from src.processing.opm_processor import OpmProcessor


def _make_composite_signal(
    sample_rate: float = 1000.0, duration: float = 2.0
) -> np.ndarray:
    """Create a signal with components at 0.5, 10, 30, 60, and 120 Hz.

    After the full pipeline (notch 60 Hz + bandpass 2–50 Hz), only the
    10 Hz and 30 Hz components should remain.
    """
    t = np.arange(0, duration, 1.0 / sample_rate)
    sig = (
        1.0 * np.sin(2 * np.pi * 0.5 * t)   # below band — should be removed
        + 1.0 * np.sin(2 * np.pi * 10.0 * t)  # in band — should pass
        + 1.0 * np.sin(2 * np.pi * 30.0 * t)  # in band — should pass
        + 1.0 * np.sin(2 * np.pi * 60.0 * t)  # notch target — should be removed
        + 1.0 * np.sin(2 * np.pi * 120.0 * t) # above band — should be removed
    )
    return sig


def _power_at_freq(signal: np.ndarray, freq: float, fs: float) -> float:
    n = len(signal)
    fft_mag = np.abs(np.fft.rfft(signal)) / n
    freqs = np.fft.rfftfreq(n, d=1.0 / fs)
    idx = np.argmin(np.abs(freqs - freq))
    return float(fft_mag[idx])


class TestOpmProcessor:
    """Verify the full Notch → Bandpass pipeline."""

    def test_full_pipeline(self):
        """Only 2–50 Hz components (excluding 60 Hz) should survive."""
        fs = 1000.0
        num_ch = 2
        sig = _make_composite_signal(fs, duration=3.0)
        data = np.tile(sig, (num_ch, 1))

        proc = OpmProcessor(sample_rate=fs, num_channels=num_ch)
        out = proc.process(data)

        # Skip transient (first 1000 samples).
        trimmed = out[0, 1000:]

        # 10 Hz and 30 Hz should have significant power.
        p10 = _power_at_freq(trimmed, 10.0, fs)
        p30 = _power_at_freq(trimmed, 30.0, fs)
        assert p10 > 0.1
        assert p30 > 0.1

        # 0.5 Hz, 60 Hz, 120 Hz should be heavily attenuated.
        p05 = _power_at_freq(trimmed, 0.5, fs)
        p60 = _power_at_freq(trimmed, 60.0, fs)
        p120 = _power_at_freq(trimmed, 120.0, fs)
        assert p05 < 0.05
        assert p60 < 0.05
        assert p120 < 0.05

    def test_notch_disabled(self):
        """With notch disabled, 60 Hz should pass through the bandpass
        (though it's near the bandpass upper edge of 50 Hz and will be
        somewhat attenuated by the bandpass itself)."""
        fs = 1000.0
        sig_60 = np.sin(2 * np.pi * 60.0 * np.arange(0, 2.0, 1 / fs))
        data = sig_60.reshape(1, -1)

        proc_with = OpmProcessor(sample_rate=fs, num_channels=1, notch_enabled=True)
        proc_without = OpmProcessor(sample_rate=fs, num_channels=1, notch_enabled=False)

        out_with = proc_with.process(data.copy())
        out_without = proc_without.process(data.copy())

        # With notch, 60 Hz power should be lower than without.
        p_with = _power_at_freq(out_with[0, 500:], 60.0, fs)
        p_without = _power_at_freq(out_without[0, 500:], 60.0, fs)
        assert p_with < p_without

    def test_bandpass_disabled(self):
        """With bandpass disabled, only notch should apply."""
        fs = 1000.0
        sig = np.sin(2 * np.pi * 120.0 * np.arange(0, 2.0, 1 / fs))
        data = sig.reshape(1, -1)

        proc = OpmProcessor(
            sample_rate=fs, num_channels=1,
            notch_enabled=False, bandpass_enabled=False,
        )
        out = proc.process(data)

        # Should be virtually identical to input (no filtering).
        np.testing.assert_allclose(out, data, atol=1e-10)

    def test_reset(self):
        """Reset should allow re-processing without accumulated state."""
        fs = 1000.0
        data = np.random.randn(1, 1000)

        proc = OpmProcessor(sample_rate=fs, num_channels=1)
        out1 = proc.process(data.copy())
        proc.reset()
        out2 = proc.process(data.copy())

        # After reset, the output should be essentially the same as the
        # first pass (same initial conditions).
        np.testing.assert_allclose(out1, out2, atol=1e-10)

    def test_streaming_blocks(self):
        """Processing in blocks should produce identical output to
        processing the full signal at once (within floating-point tolerance)."""
        fs = 1000.0
        full_sig = np.random.randn(2, 5000) * 0.001  # small amplitude OPM-like
        block_size = 1000

        # Single pass.
        proc_single = OpmProcessor(sample_rate=fs, num_channels=2)
        out_single = proc_single.process(full_sig.copy())

        # Streaming blocks.
        proc_stream = OpmProcessor(sample_rate=fs, num_channels=2)
        out_blocks = []
        for i in range(0, full_sig.shape[1], block_size):
            block = full_sig[:, i : i + block_size]
            out_blocks.append(proc_stream.process(block.copy()))
        out_stream = np.concatenate(out_blocks, axis=1)

        np.testing.assert_allclose(out_single, out_stream, atol=1e-12)
