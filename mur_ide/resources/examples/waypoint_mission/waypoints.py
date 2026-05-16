"""
Модуль задания и хранения путевых точек.

Соответствует разделам 1.1, 2.2, 3.2 ТЗ курсового проекта.
Содержит:
– функции для загрузки точек из CSV;
– класс WaypointManager для поэтапного обхода маршрута;
– заготовку для задания точек прямо в коде.
"""

from __future__ import annotations

from dataclasses import dataclass, field
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
        (2.0, 0.0, 2.0),
        (2.0, 2.0, 2.0),
        (0.0, 2.0, 2.0),
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
    – переход к следующей точке при достижении предыдущей (внутренний порог + кольцо подхода).
    """

    waypoints: List[Waypoint]
    capture_radius: float = 0.5
    # Допуск к радиусу схватывания (м): точка считается достигнутой, если
    # distance <= capture_radius + reach_slack_m (одометрия «дрожит» у цели).
    reach_slack_m: float = 0.05
    # Порог «были снаружи» (м), меньше внутреннего схвата: hysteresis между «подошли» и «схватили».
    approach_ring_m: float = 0.06
    cycles: int = 1

    _current_index: int = 0
    _completed_cycles: int = 0
    # True, если расстояние хотя бы раз превышало _outside_approach_threshold() (см. advance_if_reached).
    _was_outside_capture_for_current: bool = field(default=False, repr=False)

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

    def _reach_threshold(self) -> float:
        return self.capture_radius + max(0.0, self.reach_slack_m)

    def _outside_approach_threshold(self) -> float:
        """Порог «дальше кольца подхода»; должен быть < _reach_threshold()."""
        inner = self._reach_threshold()
        raw = self.approach_ring_m
        if raw >= inner:
            return max(0.04, inner * 0.35)
        return raw

    def advance_if_reached(self, distance_to_current: float) -> None:
        """
        Переходит к следующей точке, если ``distance <= capture_radius + reach_slack``.

        Перед этим нужно хотя бы раз уйти **за предел approach_ring_m** (типично ~6 см),
        иначе при старте в (0,0) на цели (0,0) сразу сработал бы переход. При колебаниях
        одометрии у цели (3–11 см) внешнее кольцо меньше внутреннего: раз «вылезли» за 6 см,
        можно схватить при возврате в 15 см.
        """
        if self.current() is None:
            return

        r_in = self._reach_threshold()
        r_out = self._outside_approach_threshold()

        if distance_to_current > r_out:
            self._was_outside_capture_for_current = True

        if distance_to_current > r_in:
            return

        if not self._was_outside_capture_for_current:
            return

        self._was_outside_capture_for_current = False
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
        
        
