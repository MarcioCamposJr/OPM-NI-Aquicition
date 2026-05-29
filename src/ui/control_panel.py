"""Control panel sidebar with acquisition controls and quick settings.

Contains start/stop/record/export buttons, a status indicator, and
quick-access spinboxes for the most commonly changed parameters
(sample rate and visualisation window).
"""

from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QDoubleSpinBox,
    QSpinBox,
    QGroupBox,
    QFormLayout,
    QSizePolicy,
)

from src.ui.styles import (
    ACCENT_DANGER,
    ACCENT_INFO,
    ACCENT_PRIMARY,
    ACCENT_SUCCESS,
    ACCENT_WARNING,
    BG_CARD,
    BG_DARK,
    BORDER,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)


class ControlPanel(QWidget):
    """Sidebar panel with acquisition controls and quick settings.

    Signals
    -------
    start_clicked
        User pressed the *Start* button.
    stop_clicked
        User pressed the *Stop* button.
    save_toggled : bool
        User toggled recording on/off.
    export_clicked
        User pressed the *Export* button.
    settings_clicked
        User pressed the *Settings* button.
    sample_rate_changed : float
        Quick-access sample rate changed.
    window_seconds_changed : float
        Quick-access visualisation window changed.
    """

    start_clicked = pyqtSignal()
    stop_clicked = pyqtSignal()
    save_toggled = pyqtSignal(bool)
    export_clicked = pyqtSignal()
    settings_clicked = pyqtSignal()
    sample_rate_changed = pyqtSignal(float)
    window_seconds_changed = pyqtSignal(float)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedWidth(280)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self._is_recording = False
        self._setup_ui()

    # ── UI Construction ───────────────────────────────────────────────── #

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 16, 12, 16)
        layout.setSpacing(12)

        # ── Title ─────────────────────────────────────────────────────── #
        title = QLabel("ECG Acquisition")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("cDAQ-9171 · 24 Channels")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        layout.addSpacing(8)

        # ── Status indicator ──────────────────────────────────────────── #
        self._status_label = QLabel("● Idle")
        self._status_label.setObjectName("status")
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._status_label)

        layout.addSpacing(8)

        # ── Acquisition controls ──────────────────────────────────────── #
        acq_group = QGroupBox("Aquisição")
        acq_layout = QVBoxLayout(acq_group)
        acq_layout.setSpacing(8)

        self._btn_start = QPushButton("▶  Iniciar")
        self._btn_start.setObjectName("btn_start")
        self._btn_start.clicked.connect(self.start_clicked.emit)
        acq_layout.addWidget(self._btn_start)

        self._btn_stop = QPushButton("■  Parar")
        self._btn_stop.setObjectName("btn_stop")
        self._btn_stop.setEnabled(False)
        self._btn_stop.clicked.connect(self.stop_clicked.emit)
        acq_layout.addWidget(self._btn_stop)

        layout.addWidget(acq_group)

        # ── Recording controls ────────────────────────────────────────── #
        rec_group = QGroupBox("Gravação")
        rec_layout = QVBoxLayout(rec_group)
        rec_layout.setSpacing(8)

        self._btn_record = QPushButton("⏺  Gravar TDMS")
        self._btn_record.setObjectName("btn_record")
        self._btn_record.setCheckable(True)
        self._btn_record.setEnabled(False)
        self._btn_record.toggled.connect(self._on_record_toggled)
        rec_layout.addWidget(self._btn_record)

        self._btn_export = QPushButton("📁  Exportar CSV/Excel")
        self._btn_export.setEnabled(False)
        self._btn_export.clicked.connect(self.export_clicked.emit)
        rec_layout.addWidget(self._btn_export)

        layout.addWidget(rec_group)

        # ── Quick settings ────────────────────────────────────────────── #
        quick_group = QGroupBox("Acesso Rápido")
        quick_layout = QFormLayout(quick_group)
        quick_layout.setSpacing(8)

        self._spin_sample_rate = QDoubleSpinBox()
        self._spin_sample_rate.setRange(100.0, 51200.0)
        self._spin_sample_rate.setValue(1000.0)
        self._spin_sample_rate.setSuffix(" Hz")
        self._spin_sample_rate.setDecimals(0)
        self._spin_sample_rate.valueChanged.connect(self.sample_rate_changed.emit)
        quick_layout.addRow("Sample Rate:", self._spin_sample_rate)

        self._spin_window = QDoubleSpinBox()
        self._spin_window.setRange(1.0, 30.0)
        self._spin_window.setValue(5.0)
        self._spin_window.setSuffix(" s")
        self._spin_window.setDecimals(1)
        self._spin_window.setSingleStep(0.5)
        self._spin_window.valueChanged.connect(self.window_seconds_changed.emit)
        quick_layout.addRow("Janela:", self._spin_window)

        layout.addWidget(quick_group)

        # ── Settings button ───────────────────────────────────────────── #
        self._btn_settings = QPushButton("⚙  Configurações")
        self._btn_settings.clicked.connect(self.settings_clicked.emit)
        layout.addWidget(self._btn_settings)

        # ── Stretch to push everything to top ─────────────────────────── #
        layout.addStretch()

        # ── Footer info ───────────────────────────────────────────────── #
        footer = QLabel("OPM NI Acquisition v0.1")
        footer.setObjectName("subtitle")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(footer)

    # ── Slots ─────────────────────────────────────────────────────────── #

    def _on_record_toggled(self, checked: bool) -> None:
        self._is_recording = checked
        if checked:
            self._btn_record.setText("⏹  Parar Gravação")
        else:
            self._btn_record.setText("⏺  Gravar TDMS")
        self.save_toggled.emit(checked)

    # ── Public methods for MainWindow to update state ─────────────────── #

    def set_acquiring(self, active: bool) -> None:
        """Update button states when acquisition starts/stops."""
        self._btn_start.setEnabled(not active)
        self._btn_stop.setEnabled(active)
        self._btn_record.setEnabled(active)
        self._btn_export.setEnabled(not active)
        self._spin_sample_rate.setEnabled(not active)

        if not active:
            # Force-stop recording if acquisition stops.
            if self._btn_record.isChecked():
                self._btn_record.setChecked(False)

    def set_status(self, text: str, level: str = "info") -> None:
        """Update the status label.

        Parameters
        ----------
        text : str
            Status message.
        level : str
            One of ``"info"``, ``"success"``, ``"warning"``, ``"error"``.
        """
        color_map = {
            "info": ACCENT_INFO,
            "success": ACCENT_SUCCESS,
            "warning": ACCENT_WARNING,
            "error": ACCENT_DANGER,
        }
        color = color_map.get(level, ACCENT_INFO)
        self._status_label.setText(f"● {text}")
        self._status_label.setStyleSheet(
            f"color: {color}; border: 1px solid {color}40; "
            f"background-color: {color}15;"
        )

    def get_sample_rate(self) -> float:
        return self._spin_sample_rate.value()

    def get_window_seconds(self) -> float:
        return self._spin_window.value()

    def set_sample_rate(self, value: float) -> None:
        self._spin_sample_rate.setValue(value)

    def set_window_seconds(self, value: float) -> None:
        self._spin_window.setValue(value)
