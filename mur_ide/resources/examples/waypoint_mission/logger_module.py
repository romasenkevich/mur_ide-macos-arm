"""
Модуль логирования результатов движения.

Соответствует разделам 1.5, 3.5, 4.6 ТЗ:
– запись координат и параметров движения в CSV‑файл;
– фиксация моментов достижения путевых точек.
"""

from __future__ import annotations

import csv
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Sequence


LOG_HEADER = [
    "Время",
    "X",
    "Y",
    "Z",
    "Курс",
    "Целевой_курс",
    "Расстояние",
    "Мощность_0",
    "Мощность_1",
    "Мощность_2",
    "Мощность_3",
    "Номер_точки",
]


@dataclass
class Logger:
    """
    Класс для записи параметров движения в CSV‑файл.
    """

    directory: Path = Path("logs")
    filename_prefix: str = "trajectory_log_"

    _file: csv.writer | None = field(init=False, default=None)
    _handle: object | None = field(init=False, default=None)
    _start_time: float = field(init=False, default=0.0)

    def __post_init__(self) -> None:
        self.directory.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.filename_prefix}{timestamp}.csv"
        path = self.directory / filename

        handle = path.open("w", newline="", encoding="utf-8")
        writer = csv.writer(handle)
        writer.writerow(LOG_HEADER)

        self._handle = handle
        self._file = writer
        self._start_time = time.time()

    @property
    def is_open(self) -> bool:
        return self._file is not None

    def log(
        self,
        x: float,
        y: float,
        z: float,
        yaw: float,
        target_yaw: float,
        distance: float,
        motors: Sequence[float],
        waypoint_index: int,
    ) -> None:
        """
        Запись одной строки лога.
        """
        if not self._file:
            return
        current_time = time.time() - self._start_time
        m0, m1, m2, m3 = motors
        row = [
            current_time,
            x,
            y,
            z,
            yaw,
            target_yaw,
            distance,
            m0,
            m1,
            m2,
            m3,
            waypoint_index,
        ]
        self._file.writerow(row)

    def close(self) -> None:
        """
        Закрытие файла лога.
        """
        if self._handle:
            self._handle.close()
        self._file = None
        self._handle = None
        
        
