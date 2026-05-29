# OPM ECG Acquisition -- 24-Channel System

> Migrated from LabVIEW VI: `AM-24 chan-convert_TDMS - ECG.vi`

Real-time 24-channel ECG acquisition system using National Instruments cDAQ-9171. Desktop application with high-performance waveform visualization, digital signal conditioning, and TDMS recording.

## Architecture

```
src/
├── hardware/          DAQ configuration + QThread worker (nidaqmx)
├── processing/        IIR filters (Notch 60 Hz + Bandpass 2-50 Hz)
├── data/              TDMS recorder + CSV/Excel exporter
└── ui/                PyQt6 interface (MainWindow, ChartWidget, ControlPanel, Settings)
```

**MVC Pattern** with clear separation of concerns:
- **Model:** `DaqConfig`, `EcgProcessor`, `TdmsRecorder`, `DataExporter`
- **View:** `ChartWidget`, `ControlPanel`, `SettingsDialog`
- **Controller:** `MainWindow`

**Multithreading:** `DaqWorker(QThread)` runs hardware I/O in a dedicated thread, communicating via Qt Signal/Slot.

## Tech Stack

| Component | Library |
|-----------|---------|
| GUI | PyQt6 |
| Waveforms | pyqtgraph (24 channels, real-time) |
| DAQ | nidaqmx (NI cDAQ-9171) |
| DSP | scipy.signal + numpy |
| Storage | nptdms (TDMS) + pandas (CSV/Excel) |

## Filter Pipeline

1. **Notch Filter** -- IIR Butterworth Bandstop, order 2, 59-61 Hz (60 Hz rejection)
2. **Bandpass Filter** -- IIR Butterworth Bandpass, order 4, 2-50 Hz

Both use SOS (Second-Order Sections) representation with maintained state for continuous streaming.

## Setup

```bash
# Install dependencies
uv sync

# Run the application
uv run python main.py

# Run tests
uv run pytest tests/ -v
```

## Configuration

All parameters are configurable via the **Settings Dialog** (SETTINGS button):

- **Hardware:** Device name, channel count, terminal config, voltage range
- **Acquisition:** Sample rate, samples per read, display window
- **Filters:** Enable/disable and configure Notch and Bandpass
- **Export:** Output directory and default format

The most frequently used parameters (sample rate and display window) are also accessible directly from the control panel.

## Hardware Requirements

- **Chassis:** NI cDAQ-9171 (USB, single-slot)
- **AI Module:** Compatible C Series module (e.g. NI-9205, NI-9215)
- **Driver:** NI-DAQmx installed and configured via NI MAX
