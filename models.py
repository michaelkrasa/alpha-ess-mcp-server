from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class TimeSeriesEntry:
    timestamp: str
    solar_power: int
    load_power: int
    battery_soc: float
    grid_feedin: int
    grid_import: int
    ev_charging: int


@dataclass
class TimeSeriesSummary:
    total_records: int
    interval: str
    time_span_hours: int
    solar: Dict[str, Any]
    battery: Dict[str, Any]
    grid: Dict[str, Any]
    load: Dict[str, Any]


@dataclass
class TimeSeries:
    series: List[TimeSeriesEntry]
    summary: TimeSeriesSummary


@dataclass
class ConfigPeriod:
    period: int
    start_time: str
    end_time: str
    active: bool


@dataclass
class ChargeConfig:
    enabled: bool
    periods: List[ConfigPeriod]
    charge_limit_soc: int
    units: Dict[str, str]


@dataclass
class DischargeConfig:
    enabled: bool
    periods: List[ConfigPeriod]
    discharge_limit_soc: int
    units: Dict[str, str]


@dataclass
class Snapshot:
    solar: Dict[str, Any]
    battery: Dict[str, Any]
    grid: Dict[str, Any]
    load: Dict[str, Any]
    ev_charging: Dict[str, Any]
    units: Dict[str, str]


@dataclass
class SystemInfo:
    serial: str
    name: str
    status: str


@dataclass
class SystemList:
    recommended_serial: Optional[str]
    systems: List[SystemInfo]
    requires_selection: bool

