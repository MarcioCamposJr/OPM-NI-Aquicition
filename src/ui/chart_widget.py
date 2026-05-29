"""Real-time chart grid for 24-channel ECG visualisation.

Uses ``pyqtgraph`` for high-performance waveform rendering with a
circular buffer for each channel to keep a configurable time window
visible (e.g. the last 5 seconds).

Styled to resemble an oscilloscope / strip-chart recorder with
minimal decoration and maximum data density.
"""

from __future__ import annotations

import numpy as np
import pyqtgraph as pg
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import Qt

from src.ui.styles import (
    CHANNEL_COLORS,
    BG_DARKEST,
    BG_INPUT,
    BORDER,
    TEXT_SECONDARY,
    TEXT_DATA,
    FONT_MONO,
)


class ChartWidget(QWidget):
    """Grid of 24 real-time PlotItems (6 rows x 4 columns).

    Each plot shows a rolling window of the most recent *N* seconds
    of data for one ECG channel.

    Parameters
    ----------
    num_channels : int
        Number of channels to display.
    sample_rate : float
        Samples per second (used to compute time axis).
    window_seconds : float
        Length of the visible time window in seconds.
    rows : int
        Number of rows in the plot grid.
    cols : int
        Number of columns in the plot grid.
    """

    def __init__(
        self,
        num_channels: int = 24,
        sample_rate: float = 1000.0,
        window_seconds: float = 5.0,
        rows: int = 6,
        cols: int = 4,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._num_channels = num_channels
        self._sample_rate = sample_rate
        self._window_seconds = window_seconds
        self._rows = rows
        self._cols = cols

        # Circular buffer: each channel stores ``window_samples`` values.
        self._window_samples = int(sample_rate * window_seconds)
        self._buffers: list[np.ndarray] = [
            np.zeros(self._window_samples, dtype=np.float64)
            for _ in range(num_channels)
        ]
        self._write_pos = 0  # position in the circular buffer

        # Time axis (shared across all plots).
        self._time_axis = np.linspace(0, window_seconds, self._window_samples)

        # ── Build the layout ──────────────────────────────────────────── #
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Configure pyqtgraph global settings — oscilloscope look.
        pg.setConfigOptions(
            antialias=False,       # faster rendering for 24 channels
            useOpenGL=False,       # avoid driver issues; still very fast
            background=BG_DARKEST,
            foreground=TEXT_SECONDARY,
        )

        self._graphics_layout = pg.GraphicsLayoutWidget()
        self._graphics_layout.setBackground(BG_DARKEST)
        layout.addWidget(self._graphics_layout)

        self._plots: list[pg.PlotItem] = []
        self._curves: list[pg.PlotDataItem] = []

        for i in range(num_channels):
            row = i // cols
            col = i % cols
            plot = self._graphics_layout.addPlot(row=row, col=col)
            self._configure_plot(plot, i)

            color = CHANNEL_COLORS[i % len(CHANNEL_COLORS)]
            curve = plot.plot(
                self._time_axis,
                self._buffers[i],
                pen=pg.mkPen(color=color, width=1.0),
            )

            self._plots.append(plot)
            self._curves.append(curve)

    # ── Public API ────────────────────────────────────────────────────── #

    def update_data(self, data: np.ndarray) -> None:
        """Append a new block of data and refresh all curves.

        Parameters
        ----------
        data : np.ndarray
            Shape ``(num_channels, num_new_samples)``.
        """
        num_ch, num_new = data.shape
        ws = self._window_samples

        if num_new >= ws:
            # Block is larger than the window -> take the tail.
            for ch in range(min(num_ch, self._num_channels)):
                self._buffers[ch][:] = data[ch, -ws:]
            self._write_pos = 0
        else:
            # Append into circular buffer.
            start = self._write_pos
            end = start + num_new
            for ch in range(min(num_ch, self._num_channels)):
                if end <= ws:
                    self._buffers[ch][start:end] = data[ch]
                else:
                    # Wrap around.
                    first_part = ws - start
                    self._buffers[ch][start:] = data[ch, :first_part]
                    self._buffers[ch][: num_new - first_part] = data[ch, first_part:]
            self._write_pos = end % ws

        # Update curves (no clear+re-plot -> reuse PlotDataItem for speed).
        for ch in range(min(num_ch, self._num_channels)):
            # Roll buffer so that the oldest sample is at x=0.
            rolled = np.roll(self._buffers[ch], -self._write_pos)
            self._curves[ch].setData(self._time_axis, rolled)

    def set_window_seconds(self, seconds: float) -> None:
        """Change the visible time window and reallocate buffers."""
        self._window_seconds = seconds
        self._window_samples = int(self._sample_rate * seconds)
        self._time_axis = np.linspace(0, seconds, self._window_samples)
        self._buffers = [
            np.zeros(self._window_samples, dtype=np.float64)
            for _ in range(self._num_channels)
        ]
        self._write_pos = 0

        for plot in self._plots:
            plot.setXRange(0, seconds, padding=0)

    def clear_data(self) -> None:
        """Zero all buffers and reset curves."""
        for ch in range(self._num_channels):
            self._buffers[ch][:] = 0.0
            self._curves[ch].setData(self._time_axis, self._buffers[ch])
        self._write_pos = 0

    # ── Internal helpers ──────────────────────────────────────────────── #

    def _configure_plot(self, plot: pg.PlotItem, channel_index: int) -> None:
        """Style a single plot widget for an instrument / oscilloscope look."""
        label = f"CH {channel_index + 1:02d}"
        color = CHANNEL_COLORS[channel_index % len(CHANNEL_COLORS)]

        # Title: channel label in its trace colour, small monospace font.
        plot.setTitle(label, color=color, size="8pt")
        plot.setXRange(0, self._window_seconds, padding=0)

        # Grid: subtle lines resembling oscilloscope graticule.
        plot.showGrid(x=True, y=True, alpha=0.1)
        plot.hideButtons()
        plot.setMenuEnabled(False)

        # Minimal axis labels — only leftmost column shows Y, bottom row shows X.
        row = channel_index // self._cols
        col = channel_index % self._cols

        ax_left = plot.getAxis("left")
        ax_bottom = plot.getAxis("bottom")

        # Axis styling — thin, muted.
        for ax in (ax_left, ax_bottom):
            ax.setPen(pg.mkPen(color=BORDER, width=1))
            ax.setTextPen(pg.mkPen(color=TEXT_SECONDARY))

        ax_left.setStyle(showValues=(col == 0), tickLength=-4)
        ax_bottom.setStyle(showValues=(row == self._rows - 1), tickLength=-4)

        if col == 0:
            ax_left.setLabel("V", color=TEXT_SECONDARY, **{"font-size": "8pt"})
        if row == self._rows - 1:
            ax_bottom.setLabel("s", color=TEXT_SECONDARY, **{"font-size": "8pt"})

        # Tight layout for maximum data density.
        plot.setContentsMargins(1, 1, 1, 1)
