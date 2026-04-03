"""
Модуль задания и хранения путевых точек.

Соответствует разделам 1.1, 2.2, 3.2 ТЗ курсового проекта.
Содержит:
– функции для загрузки точек из CSV;
– класс WaypointManager для поэтапного обхода маршрута;
– заготовку для задания точек прямо в коде.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Optional, Iterable

import csv


Waypoint = Tuple[float, float, float]  # (x, y, depth)


def default_waypoints() -> List[Waypoint]:
    """
    Простейший маршрут в виде квадрата.

    Используется, если файл с путевыми точками не найден
    или возникла ошибка при его чтении.
    """
    return [
        (0.0, 0.0, 2.0),
        (5.0, 0.0, 2.0),
        (5.0, 5.0, 2.0),
        (0.0, 5.0, 2.0),
    ]


def load_waypoints_from_csv(path: str | Path) -> List[Waypoint]:
    """
    Загрузка путевых точек из CSV‑файла формата:
    X,Y,Z
    0,0,2
    5,0,2
    ...

    В случае ошибок ввода/формата возбуждается ValueError
    с понятным сообщением.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise ValueError(f"Файл с путевыми точками не найден: {file_path}")

    waypoints: List[Waypoint] = []

    with file_path.open("r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header_read = False
        for row in reader:
            if not row:
                continue
            # Пропускаем заголовок, если он есть
            if not header_read and any(cell.lower() in ("x", "y", "z") for cell in row):
                header_read = True
                continue
            header_read = True

            if len(row) < 3:
                raise ValueError(
                    f"Некорректная строка в файле {file_path}: ожидалось 3 столбца, получено {len(row)} ({row})"
                )
            try:
                x = float(row[0].strip())
                y = float(row[1].strip())
                z = float(row[2].strip())
            except ValueError as exc:
                raise ValueError(f"Не удалось преобразовать координаты в число: {row}") from exc

            if z < 0:
                raise ValueError(f"Глубина не может быть отрицательной: {row}")

            waypoints.append((x, y, z))

    if not waypoints:
        raise ValueError(f"В файле {file_path} не найдено ни одной путевой точки")

    return waypoints


@dataclass
class WaypointManager:
    """
    Класс для последовательного обхода маршрута по путевым точкам.

    Поддерживает:
    – несколько циклов прохождения;
    – получение текущей точки;
    – переход к следующей точке при достижении предыдущей.
    """

    waypoints: List[Waypoint]
    capture_radius: float = 0.5
    cycles: int = 1

    _current_index: int = 0
    _completed_cycles: int = 0

    def current(self) -> Optional[Waypoint]:
        """Возвращает текущую целевую точку или None, если маршрут завершён."""
        if self._completed_cycles >= self.cycles:
            return None
        if not self.waypoints:
            return None
        return self.waypoints[self._current_index]

    def is_finished(self) -> bool:
        """Возвращает True, если все циклы прохождения маршрута завершены."""
        return self.current() is None

    def advance_if_reached(self, distance_to_current: float) -> None:
        """
        Переходит к следующей точке, если расстояние до текущей меньше радиуса схватывания.
        """
        if self.current() is None:
            return

        if distance_to_current <= self.capture_radius:
            self._current_index += 1
            if self._current_index >= len(self.waypoints):
                self._current_index = 0
                self._completed_cycles += 1

    @property
    def progress(self) -> float:
        """
        Оценка прогресса выполнения миссии в процентах.
        """
        if self.cycles <= 0 or not self.waypoints:
            return 0.0
        total_points = len(self.waypoints) * self.cycles
        passed_points = self._completed_cycles * len(self.waypoints) + self._current_index
        return 100.0 * min(passed_points / total_points, 1.0)


def iter_waypoints(waypoints: Iterable[Waypoint]) -> Iterable[Waypoint]:
    """
    Простейший генератор для перебора путевых точек.
    Может использоваться в отдельных тестовых скриптах.
    """
    for wp in waypoints:
        yield wp
        
