from typing import Optional
from dataclasses import dataclass

@dataclass
class SamsungACRequest:
    power: bool
    mode: int
    temp: int
    fan: int
    timer_mode: int = 0
    timer_15m: int = 0


@dataclass
class SamsungACTimers:
    on_hours: float
    off_hours: float

@dataclass
class SamsungACState:
    power: bool
    power_str: str
    mode: int
    mode_str: str
    temp: int
    fan: int
    fan_str: str
    timers: Optional[SamsungACTimers]
