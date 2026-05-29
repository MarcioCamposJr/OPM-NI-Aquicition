# OPM ECG Acquisition — 24-Channel System

> Migração do VI LabVIEW `AM-24 chan-convert_TDMS - ECG.vi` para Python.

Sistema de aquisição de ECG de 24 canais em tempo real usando National Instruments cDAQ-9171. Interface desktop com visualização de alta performance, processamento digital de sinais e gravação em TDMS.

## 🏗️ Arquitetura

```
src/
├── hardware/          # DAQ config + QThread worker (nidaqmx)
├── processing/        # Filtros IIR (Notch 60Hz + Bandpass 2-50Hz)
├── data/              # TDMS recorder + CSV/Excel exporter
└── ui/                # PyQt6 interface (MainWindow, ChartWidget, ControlPanel, Settings)
```

**Padrão MVC** com separação clara de responsabilidades:
- **Model:** `DaqConfig`, `EcgProcessor`, `TdmsRecorder`, `DataExporter`
- **View:** `ChartWidget`, `ControlPanel`, `SettingsDialog`
- **Controller:** `MainWindow`

**Multithreading:** `DaqWorker(QThread)` executa leitura do hardware em thread separada, comunicando via `Signal/Slot` do Qt.

## ⚡ Stack Tecnológico

| Componente | Biblioteca |
|-----------|-----------|
| GUI | PyQt6 |
| Gráficos | pyqtgraph (24 canais em tempo real) |
| DAQ | nidaqmx (NI cDAQ-9171) |
| Processamento | scipy.signal + numpy |
| Armazenamento | nptdms (TDMS) + pandas (CSV/Excel) |

## 🔬 Pipeline de Filtros

1. **Notch Filter** — IIR Butterworth Bandstop, ordem 2, 59–61 Hz (rejeição 60 Hz)
2. **Bandpass Filter** — IIR Butterworth Bandpass, ordem 4, 2–50 Hz

Ambos usam representação SOS (Second-Order Sections) com estado mantido para filtragem contínua em streaming.

## 🚀 Setup

```bash
# Instalar dependências com uv
uv sync

# Rodar a aplicação
uv run python main.py

# Rodar testes
uv run pytest tests/ -v
```

## ⚙️ Configuração

Todos os parâmetros são configuráveis via **Settings Dialog** (`⚙ Configurações`):

- **Hardware:** Device name, nº canais, terminal config, voltage range
- **Aquisição:** Sample rate, samples per read, janela de visualização
- **Filtros:** Ativar/desativar e configurar Notch e Bandpass
- **Exportação:** Diretório de saída e formato padrão

Os parâmetros mais usados (sample rate e janela de visualização) ficam acessíveis diretamente no painel lateral.

## 📋 Requisitos de Hardware

- **Chassis:** NI cDAQ-9171 (USB, single-slot)
- **Módulo AI:** Compatível com C Series (ex: NI-9205, NI-9215)
- **Driver:** NI-DAQmx instalado e configurado via NI MAX
