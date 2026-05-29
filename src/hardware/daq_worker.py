"""QThread-based worker for continuous DAQ data acquisition.

``DaqWorker`` runs in a dedicated thread, creates an NI-DAQmx analog
input task, and emits blocks of data via Qt signals so the UI thread
is never blocked by hardware I/O.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal

if TYPE_CHECKING:
    from src.hardware.daq_config import DaqConfig

logger = logging.getLogger(__name__)


# ── Terminal config mapping ──────────────────────────────────────────────── #

def _resolve_terminal_config(name: str):
    """Map a human-readable terminal config name to the nidaqmx constant.

    We import ``nidaqmx`` lazily so that the rest of the application can
    be developed and tested without the NI driver installed.
    """
    import nidaqmx.constants as nic

    _MAP = {
        "RSE": nic.TerminalConfiguration.RSE,
        "NRSE": nic.TerminalConfiguration.NRSE,
        "DIFF": nic.TerminalConfiguration.DIFFERENTIAL,
        "PSEUDO_DIFF": nic.TerminalConfiguration.PSEUDODIFFERENTIAL,
    }
    try:
        return _MAP[name.upper()]
    except KeyError:
        raise ValueError(
            f"Unknown terminal config '{name}'. "
            f"Valid options: {list(_MAP.keys())}"
        ) from None


# ── Worker Thread ────────────────────────────────────────────────────────── #

class DaqWorker(QThread):
    """Continuously reads analog input data from an NI DAQ device.

    Signals
    -------
    data_ready : np.ndarray
        Emitted for every successfully read block.  Shape is
        ``(num_channels, samples_per_read)`` — a 2-D float64 array.
    error_occurred : str
        Emitted when an unrecoverable read error happens.
    status_changed : str
        Emitted to communicate state transitions (e.g. *"Conectado"*,
        *"Lendo…"*, *"Parado"*).
    """

    data_ready = pyqtSignal(np.ndarray)
    error_occurred = pyqtSignal(str)
    status_changed = pyqtSignal(str)

    def __init__(self, config: DaqConfig, parent=None) -> None:
        super().__init__(parent)
        self._config = config
        self._running = False

    # ── public API ──────────────────────────────────────────────────────── #

    def stop(self) -> None:
        """Request the acquisition loop to stop gracefully."""
        self._running = False

    @property
    def is_running(self) -> bool:
        return self._running

    # ── thread entry-point ──────────────────────────────────────────────── #

    def run(self) -> None:  # noqa: D401 — Qt override
        """Thread main: configure task, read in a loop, clean up."""
        import nidaqmx
        from nidaqmx.stream_readers import AnalogMultiChannelReader

        cfg = self._config
        cfg.validate()

        task: nidaqmx.Task | None = None
        try:
            task = nidaqmx.Task("ECG_Acquisition")

            # ── add channels ────────────────────────────────────────────── #
            terminal = _resolve_terminal_config(cfg.terminal_config)
            task.ai_channels.add_ai_voltage_chan(
                physical_channel=cfg.physical_channels_str,
                min_val=cfg.min_voltage,
                max_val=cfg.max_voltage,
                terminal_config=terminal,
            )

            # ── configure timing (sample clock) ─────────────────────────── #
            task.timing.cfg_samp_clk_timing(
                rate=cfg.sample_rate,
                sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS,
                samps_per_chan=cfg.samples_per_read,
            )

            # ── create the multi-channel reader ─────────────────────────── #
            reader = AnalogMultiChannelReader(task.in_stream)
            buffer = np.zeros(
                (cfg.num_channels, cfg.samples_per_read), dtype=np.float64
            )

            # ── start the task ──────────────────────────────────────────── #
            task.start()
            self._running = True
            self.status_changed.emit("Adquirindo…")
            logger.info(
                "DAQ started: %s @ %.0f Hz, %d ch",
                cfg.device_name,
                cfg.sample_rate,
                cfg.num_channels,
            )

            # ── continuous read loop ────────────────────────────────────── #
            while self._running:
                try:
                    reader.read_many_sample(
                        buffer,
                        number_of_samples_per_channel=cfg.samples_per_read,
                        timeout=5.0,
                    )
                    # Emit a *copy* so downstream consumers own the memory.
                    self.data_ready.emit(buffer.copy())
                except nidaqmx.errors.DaqReadError as exc:
                    logger.warning("Read timeout/error: %s", exc)
                    # Transient errors (e.g. timeout) are logged but don't
                    # kill the loop.  The flag ``self._running`` can still
                    # be flipped externally to break out.
                    continue

        except Exception as exc:
            msg = f"DAQ error: {exc}"
            logger.exception(msg)
            self.error_occurred.emit(msg)
        finally:
            if task is not None:
                try:
                    task.stop()
                    task.close()
                except Exception:
                    logger.exception("Error while closing DAQ task")
            self._running = False
            self.status_changed.emit("Parado")
            logger.info("DAQ worker stopped.")
