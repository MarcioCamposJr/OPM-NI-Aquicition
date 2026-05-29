"""Settings dialog for the ECG acquisition system.

Provides a tabbed interface to configure hardware, acquisition,
filter, and export parameters.  Settings are persisted between
sessions using ``QSettings``.
"""

from __future__ import annotations

from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
    QFileDialog,
)

from src.hardware.daq_config import DaqConfig

# ── Constants ────────────────────────────────────────────────────────────── #

_ORG = "OPM"
_APP = "ECG-Acquisition"


class SettingsDialog(QDialog):
    """Modal dialog for editing system settings.

    Tabs
    ----
    - **Hardware** : device, channels, terminal config, voltage range.
    - **Aquisição** : sample rate, samples per read, visualisation window.
    - **Filtros** : enable/disable and tune notch & bandpass filters.
    - **Exportação** : default output directory and format.

    Parameters
    ----------
    daq_config : DaqConfig
        Current DAQ configuration (used to populate initial values).
    parent : QWidget | None
        Parent widget.
    """

    def __init__(
        self,
        daq_config: DaqConfig | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("SETTINGS")
        self.setMinimumSize(520, 480)
        self.setModal(True)

        self._settings = QSettings(_ORG, _APP)
        cfg = daq_config or DaqConfig()

        # ── Main layout ───────────────────────────────────────────────── #
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)

        self._tabs = QTabWidget()
        main_layout.addWidget(self._tabs)

        # ── Build tabs ────────────────────────────────────────────────── #
        self._build_hardware_tab(cfg)
        self._build_acquisition_tab(cfg)
        self._build_filters_tab()
        self._build_export_tab()

        # ── Buttons ───────────────────────────────────────────────────── #
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
            | QDialogButtonBox.StandardButton.RestoreDefaults
        )
        buttons.accepted.connect(self._save_and_accept)
        buttons.rejected.connect(self.reject)
        restore_btn = buttons.button(QDialogButtonBox.StandardButton.RestoreDefaults)
        if restore_btn:
            restore_btn.clicked.connect(self._restore_defaults)
        main_layout.addWidget(buttons)

        # ── Load persisted values ─────────────────────────────────────── #
        self._load_settings()

    # ── Tab builders ──────────────────────────────────────────────────── #

    def _build_hardware_tab(self, cfg: DaqConfig) -> None:
        page = QWidget()
        layout = QFormLayout(page)
        layout.setSpacing(10)

        self._edit_device = QLineEdit(cfg.device_name)
        layout.addRow("Device Name:", self._edit_device)

        self._spin_num_ch = QSpinBox()
        self._spin_num_ch.setRange(1, 64)
        self._spin_num_ch.setValue(cfg.num_channels)
        layout.addRow("CHANNELS:", self._spin_num_ch)

        self._edit_prefix = QLineEdit(cfg.channel_prefix)
        layout.addRow("CH PREFIX:", self._edit_prefix)

        self._combo_terminal = QComboBox()
        self._combo_terminal.addItems(["RSE", "NRSE", "DIFF", "PSEUDO_DIFF"])
        self._combo_terminal.setCurrentText(cfg.terminal_config)
        layout.addRow("TERMINAL:", self._combo_terminal)

        self._spin_vmin = QDoubleSpinBox()
        self._spin_vmin.setRange(-100.0, 0.0)
        self._spin_vmin.setValue(cfg.min_voltage)
        self._spin_vmin.setSuffix(" V")
        self._spin_vmin.setDecimals(1)
        layout.addRow("V Min:", self._spin_vmin)

        self._spin_vmax = QDoubleSpinBox()
        self._spin_vmax.setRange(0.0, 100.0)
        self._spin_vmax.setValue(cfg.max_voltage)
        self._spin_vmax.setSuffix(" V")
        self._spin_vmax.setDecimals(1)
        layout.addRow("V Max:", self._spin_vmax)

        self._tabs.addTab(page, "Hardware")

    def _build_acquisition_tab(self, cfg: DaqConfig) -> None:
        page = QWidget()
        layout = QFormLayout(page)
        layout.setSpacing(10)

        self._spin_sr = QDoubleSpinBox()
        self._spin_sr.setRange(100.0, 51200.0)
        self._spin_sr.setValue(cfg.sample_rate)
        self._spin_sr.setSuffix(" Hz")
        self._spin_sr.setDecimals(0)
        layout.addRow("Sample Rate:", self._spin_sr)

        self._spin_spr = QSpinBox()
        self._spin_spr.setRange(10, 100000)
        self._spin_spr.setValue(cfg.samples_per_read)
        layout.addRow("Samples / Read:", self._spin_spr)

        self._spin_window = QDoubleSpinBox()
        self._spin_window.setRange(1.0, 30.0)
        self._spin_window.setValue(
            float(self._settings.value("acq/window_seconds", 5.0))
        )
        self._spin_window.setSuffix(" s")
        self._spin_window.setDecimals(1)
        self._spin_window.setSingleStep(0.5)
        layout.addRow("DISPLAY WINDOW:", self._spin_window)

        self._tabs.addTab(page, "Acquisition")

    def _build_filters_tab(self) -> None:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(12)

        # ── Notch ─────────────────────────────────────────────────────── #
        notch_group = QGroupBox("NOTCH FILTER  (60 Hz REJECTION)")
        notch_layout = QFormLayout(notch_group)

        self._chk_notch = QCheckBox("Enabled")
        self._chk_notch.setChecked(
            self._settings.value("filters/notch_enabled", True, type=bool)
        )
        notch_layout.addRow(self._chk_notch)

        self._spin_notch_low = QDoubleSpinBox()
        self._spin_notch_low.setRange(1.0, 500.0)
        self._spin_notch_low.setValue(
            float(self._settings.value("filters/notch_low", 59.0))
        )
        self._spin_notch_low.setSuffix(" Hz")
        notch_layout.addRow("LOW FREQ:", self._spin_notch_low)

        self._spin_notch_high = QDoubleSpinBox()
        self._spin_notch_high.setRange(1.0, 500.0)
        self._spin_notch_high.setValue(
            float(self._settings.value("filters/notch_high", 61.0))
        )
        self._spin_notch_high.setSuffix(" Hz")
        notch_layout.addRow("HIGH FREQ:", self._spin_notch_high)

        self._spin_notch_order = QSpinBox()
        self._spin_notch_order.setRange(1, 10)
        self._spin_notch_order.setValue(
            int(self._settings.value("filters/notch_order", 2))
        )
        notch_layout.addRow("ORDER:", self._spin_notch_order)

        layout.addWidget(notch_group)

        # ── Bandpass ──────────────────────────────────────────────────── #
        bp_group = QGroupBox("BANDPASS FILTER  (ECG BAND)")
        bp_layout = QFormLayout(bp_group)

        self._chk_bp = QCheckBox("Enabled")
        self._chk_bp.setChecked(
            self._settings.value("filters/bp_enabled", True, type=bool)
        )
        bp_layout.addRow(self._chk_bp)

        self._spin_bp_low = QDoubleSpinBox()
        self._spin_bp_low.setRange(0.01, 100.0)
        self._spin_bp_low.setValue(
            float(self._settings.value("filters/bp_low", 2.0))
        )
        self._spin_bp_low.setSuffix(" Hz")
        bp_layout.addRow("LOW FREQ:", self._spin_bp_low)

        self._spin_bp_high = QDoubleSpinBox()
        self._spin_bp_high.setRange(1.0, 500.0)
        self._spin_bp_high.setValue(
            float(self._settings.value("filters/bp_high", 50.0))
        )
        self._spin_bp_high.setSuffix(" Hz")
        bp_layout.addRow("HIGH FREQ:", self._spin_bp_high)

        self._spin_bp_order = QSpinBox()
        self._spin_bp_order.setRange(1, 10)
        self._spin_bp_order.setValue(
            int(self._settings.value("filters/bp_order", 4))
        )
        bp_layout.addRow("ORDER:", self._spin_bp_order)

        layout.addWidget(bp_group)
        layout.addStretch()

        self._tabs.addTab(page, "Filters")

    def _build_export_tab(self) -> None:
        page = QWidget()
        layout = QFormLayout(page)
        layout.setSpacing(10)

        # Output directory
        dir_row = QHBoxLayout()
        self._edit_output_dir = QLineEdit(
            self._settings.value("export/output_dir", ".")
        )
        dir_row.addWidget(self._edit_output_dir)
        btn_browse = QPushButton("...")
        btn_browse.setFixedWidth(36)
        btn_browse.clicked.connect(self._browse_output_dir)
        dir_row.addWidget(btn_browse)
        layout.addRow("OUTPUT DIR:", dir_row)

        # Default format
        self._combo_format = QComboBox()
        self._combo_format.addItems(["TDMS", "CSV", "Excel (.xlsx)"])
        self._combo_format.setCurrentText(
            self._settings.value("export/default_format", "TDMS")
        )
        layout.addRow("DEFAULT FORMAT:", self._combo_format)

        self._tabs.addTab(page, "Export")

    # ── Persistence ───────────────────────────────────────────────────── #

    def _load_settings(self) -> None:
        """Load persisted values from QSettings and apply to widgets."""
        s = self._settings

        # Hardware
        self._edit_device.setText(s.value("hw/device", self._edit_device.text()))
        self._spin_num_ch.setValue(int(s.value("hw/num_channels", self._spin_num_ch.value())))
        self._edit_prefix.setText(s.value("hw/prefix", self._edit_prefix.text()))
        self._combo_terminal.setCurrentText(
            s.value("hw/terminal", self._combo_terminal.currentText())
        )
        self._spin_vmin.setValue(float(s.value("hw/vmin", self._spin_vmin.value())))
        self._spin_vmax.setValue(float(s.value("hw/vmax", self._spin_vmax.value())))

        # Acquisition
        self._spin_sr.setValue(float(s.value("acq/sample_rate", self._spin_sr.value())))
        self._spin_spr.setValue(int(s.value("acq/samples_per_read", self._spin_spr.value())))

    def _save_settings(self) -> None:
        """Persist current widget values to QSettings."""
        s = self._settings

        # Hardware
        s.setValue("hw/device", self._edit_device.text())
        s.setValue("hw/num_channels", self._spin_num_ch.value())
        s.setValue("hw/prefix", self._edit_prefix.text())
        s.setValue("hw/terminal", self._combo_terminal.currentText())
        s.setValue("hw/vmin", self._spin_vmin.value())
        s.setValue("hw/vmax", self._spin_vmax.value())

        # Acquisition
        s.setValue("acq/sample_rate", self._spin_sr.value())
        s.setValue("acq/samples_per_read", self._spin_spr.value())
        s.setValue("acq/window_seconds", self._spin_window.value())

        # Filters
        s.setValue("filters/notch_enabled", self._chk_notch.isChecked())
        s.setValue("filters/notch_low", self._spin_notch_low.value())
        s.setValue("filters/notch_high", self._spin_notch_high.value())
        s.setValue("filters/notch_order", self._spin_notch_order.value())
        s.setValue("filters/bp_enabled", self._chk_bp.isChecked())
        s.setValue("filters/bp_low", self._spin_bp_low.value())
        s.setValue("filters/bp_high", self._spin_bp_high.value())
        s.setValue("filters/bp_order", self._spin_bp_order.value())

        # Export
        s.setValue("export/output_dir", self._edit_output_dir.text())
        s.setValue("export/default_format", self._combo_format.currentText())

    def _save_and_accept(self) -> None:
        self._save_settings()
        self.accept()

    def _restore_defaults(self) -> None:
        """Reset all widgets to factory defaults."""
        cfg = DaqConfig()
        self._edit_device.setText(cfg.device_name)
        self._spin_num_ch.setValue(cfg.num_channels)
        self._edit_prefix.setText(cfg.channel_prefix)
        self._combo_terminal.setCurrentText(cfg.terminal_config)
        self._spin_vmin.setValue(cfg.min_voltage)
        self._spin_vmax.setValue(cfg.max_voltage)

        self._spin_sr.setValue(cfg.sample_rate)
        self._spin_spr.setValue(cfg.samples_per_read)
        self._spin_window.setValue(5.0)

        self._chk_notch.setChecked(True)
        self._spin_notch_low.setValue(59.0)
        self._spin_notch_high.setValue(61.0)
        self._spin_notch_order.setValue(2)

        self._chk_bp.setChecked(True)
        self._spin_bp_low.setValue(2.0)
        self._spin_bp_high.setValue(50.0)
        self._spin_bp_order.setValue(4)

        self._edit_output_dir.setText(".")
        self._combo_format.setCurrentText("TDMS")

    def _browse_output_dir(self) -> None:
        path = QFileDialog.getExistingDirectory(
            self, "Select Output Directory", self._edit_output_dir.text()
        )
        if path:
            self._edit_output_dir.setText(path)

    # ── Public getters for MainWindow ─────────────────────────────────── #

    def get_daq_config(self) -> DaqConfig:
        """Build a ``DaqConfig`` from the current dialog values."""
        return DaqConfig(
            device_name=self._edit_device.text(),
            num_channels=self._spin_num_ch.value(),
            channel_prefix=self._edit_prefix.text(),
            sample_rate=self._spin_sr.value(),
            samples_per_read=self._spin_spr.value(),
            min_voltage=self._spin_vmin.value(),
            max_voltage=self._spin_vmax.value(),
            terminal_config=self._combo_terminal.currentText(),
        )

    def get_filter_settings(self) -> dict:
        """Return filter parameters as a dict for ``EcgProcessor``."""
        return {
            "notch_enabled": self._chk_notch.isChecked(),
            "notch_low": self._spin_notch_low.value(),
            "notch_high": self._spin_notch_high.value(),
            "notch_order": self._spin_notch_order.value(),
            "bandpass_enabled": self._chk_bp.isChecked(),
            "bp_low": self._spin_bp_low.value(),
            "bp_high": self._spin_bp_high.value(),
            "bp_order": self._spin_bp_order.value(),
        }

    def get_window_seconds(self) -> float:
        return self._spin_window.value()

    def get_output_dir(self) -> str:
        return self._edit_output_dir.text()

    def get_default_format(self) -> str:
        return self._combo_format.currentText()
