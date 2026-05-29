"""Tests for the DataExporter (CSV and Excel export)."""

import numpy as np
import pandas as pd
import pytest
from pathlib import Path

from src.data.exporter import DataExporter


@pytest.fixture
def sample_data() -> np.ndarray:
    """A small 4-channel × 500 sample test array."""
    np.random.seed(42)
    return np.random.randn(4, 500)


@pytest.fixture
def channel_names() -> list[str]:
    return ["CH-01", "CH-02", "CH-03", "CH-04"]


class TestCsvExport:
    """Verify CSV export produces correct files."""

    def test_creates_file(self, tmp_path: Path, sample_data, channel_names):
        filepath = tmp_path / "test_output.csv"
        DataExporter.to_csv(sample_data, filepath, channel_names, sample_rate=1000.0)
        assert filepath.exists()

    def test_correct_shape(self, tmp_path: Path, sample_data, channel_names):
        filepath = tmp_path / "test_output.csv"
        DataExporter.to_csv(sample_data, filepath, channel_names, sample_rate=1000.0)

        df = pd.read_csv(filepath, index_col=0)
        assert df.shape == (500, 4)  # 500 rows, 4 channels

    def test_correct_columns(self, tmp_path: Path, sample_data, channel_names):
        filepath = tmp_path / "test_output.csv"
        DataExporter.to_csv(sample_data, filepath, channel_names, sample_rate=1000.0)

        df = pd.read_csv(filepath, index_col=0)
        assert list(df.columns) == channel_names

    def test_data_integrity(self, tmp_path: Path, sample_data, channel_names):
        filepath = tmp_path / "test_output.csv"
        DataExporter.to_csv(sample_data, filepath, channel_names, sample_rate=1000.0)

        df = pd.read_csv(filepath, index_col=0)
        np.testing.assert_allclose(df.values, sample_data.T, atol=1e-10)

    def test_time_index(self, tmp_path: Path, sample_data, channel_names):
        filepath = tmp_path / "test_output.csv"
        sr = 1000.0
        DataExporter.to_csv(sample_data, filepath, channel_names, sample_rate=sr)

        df = pd.read_csv(filepath, index_col=0)
        expected_time = np.arange(500) / sr
        np.testing.assert_allclose(df.index.values, expected_time, atol=1e-10)

    def test_default_channel_names(self, tmp_path: Path, sample_data):
        """When no channel names are given, defaults should be used."""
        filepath = tmp_path / "test_output.csv"
        DataExporter.to_csv(sample_data, filepath, sample_rate=1000.0)

        df = pd.read_csv(filepath, index_col=0)
        assert list(df.columns) == ["CH-01", "CH-02", "CH-03", "CH-04"]


class TestExcelExport:
    """Verify Excel export produces correct files."""

    def test_creates_file(self, tmp_path: Path, sample_data, channel_names):
        filepath = tmp_path / "test_output.xlsx"
        DataExporter.to_excel(sample_data, filepath, channel_names, sample_rate=1000.0)
        assert filepath.exists()

    def test_correct_shape(self, tmp_path: Path, sample_data, channel_names):
        filepath = tmp_path / "test_output.xlsx"
        DataExporter.to_excel(sample_data, filepath, channel_names, sample_rate=1000.0)

        df = pd.read_excel(filepath, index_col=0, engine="openpyxl")
        assert df.shape == (500, 4)

    def test_data_integrity(self, tmp_path: Path, sample_data, channel_names):
        filepath = tmp_path / "test_output.xlsx"
        DataExporter.to_excel(sample_data, filepath, channel_names, sample_rate=1000.0)

        df = pd.read_excel(filepath, index_col=0, engine="openpyxl")
        np.testing.assert_allclose(df.values, sample_data.T, atol=1e-10)
