"""Configuration dataclass for the NI DAQ hardware.

Encapsulates all parameters needed to configure an analog input
voltage task on a National Instruments cDAQ chassis.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class DaqConfig:
    """Immutable configuration for a DAQ acquisition session.

    Attributes:
        device_name: NI-DAQmx device/module name (e.g. ``"cDAQ1Mod1"``).
        num_channels: Number of analog input channels to acquire.
        channel_prefix: Channel name prefix (e.g. ``"ai"`` → ai0, ai1, …).
        sample_rate: Sampling rate in Hz.
        samples_per_read: Number of samples read per block (per channel).
        min_voltage: Minimum expected voltage (V) of the input range.
        max_voltage: Maximum expected voltage (V) of the input range.
        terminal_config: Terminal configuration string.
            One of ``"RSE"``, ``"NRSE"``, ``"DIFF"``, ``"PSEUDO_DIFF"``.
    """

    device_name: str = "cDAQ1Mod1"
    num_channels: int = 24
    channel_prefix: str = "ai"
    sample_rate: float = 1000.0
    samples_per_read: int = 1000
    min_voltage: float = -10.0
    max_voltage: float = 10.0
    terminal_config: str = "RSE"

    # ---- derived helpers -------------------------------------------------- #

    @property
    def channel_list(self) -> list[str]:
        """Return the full list of physical channel strings.

        Example: ``["cDAQ1Mod1/ai0", "cDAQ1Mod1/ai1", …, "cDAQ1Mod1/ai23"]``
        """
        return [
            f"{self.device_name}/{self.channel_prefix}{i}"
            for i in range(self.num_channels)
        ]

    @property
    def physical_channels_str(self) -> str:
        """Return the NI-DAQmx channel range string.

        Example: ``"cDAQ1Mod1/ai0:23"``
        """
        last = self.num_channels - 1
        return f"{self.device_name}/{self.channel_prefix}0:{last}"

    @property
    def channel_names(self) -> list[str]:
        """Return human-readable channel labels.

        Example: ``["CH-01", "CH-02", …, "CH-24"]``
        """
        return [f"CH-{i + 1:02d}" for i in range(self.num_channels)]

    def validate(self) -> None:
        """Raise ``ValueError`` if any parameter is out of acceptable range."""
        if self.num_channels < 1:
            raise ValueError("num_channels must be >= 1")
        if self.sample_rate <= 0:
            raise ValueError("sample_rate must be > 0")
        if self.samples_per_read < 1:
            raise ValueError("samples_per_read must be >= 1")
        if self.min_voltage >= self.max_voltage:
            raise ValueError("min_voltage must be < max_voltage")
        valid_terminals = {"RSE", "NRSE", "DIFF", "PSEUDO_DIFF"}
        if self.terminal_config not in valid_terminals:
            raise ValueError(
                f"terminal_config must be one of {valid_terminals}, "
                f"got '{self.terminal_config}'"
            )
