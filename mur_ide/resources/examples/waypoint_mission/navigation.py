"""
Модуль навигации.

Соответствует разделам 1.2, 1.4, 3.3 ТЗ:
– расчёт расстояния до цели;
– расчёт целевого курса;
– нормализация углов и ошибка по курсу.
"""

from __future__ import annotations

import math
from typing import Tuple

from waypoints import Waypoint


def calculate_distance(x1: float, y1: float, x2: float, y2: float) -> float:
    """Евклидово расстояние между двумя точками на плоскости."""
    dx = x2 - x1
    dy = y2 - y1
    return math.sqrt(dx * dx + dy * dy)


def calculate_target_yaw(x_cur: float, y_cur: float, x_tgt: float, y_tgt: float) -> float:
    """
    Расчёт целевого курса в градусах по координатам текущей и целевой точки.

    В сцене MUR горизонталь — плоскость XZ (Y — вертикаль); в CSV маршрута поля X и Y
    соответствуют мировым X и Z. Курс из симулятора — поворот вокруг оси Y (get_yaw);
    при нулевом курсе «вперёд» аппарата направлено вдоль +Z. Тогда азимут на цель:
    atan2(dX, dZ) в градусах.
    """
    dx = x_tgt - x_cur
    dz = y_tgt - y_cur
    yaw_rad = math.atan2(dx, dz)
    yaw_deg = math.degrees(yaw_rad)
    return yaw_deg


def calculate_target_yaw_near_aware(
    x_cur: float,
    y_cur: float,
    x_tgt: float,
    y_tgt: float,
    current_yaw_deg: float,
    degenerate_tol_m: float = 0.08,
) -> float:
    """
    Целевой курс по вектору к цели (как ``calculate_target_yaw``).

    Запасной вариант **только** если вектор к цели почти нулевой: ``dx²+dz² < tol²``.
    Тогда ``atan2(0,0)`` даёт 0°, что ломает регулятор курса у самой точки.

    Важно: **не** сравнивать с «расстоянием до точки в целом» (например 0.4 м):
    при подходе к (0,0) с боку нужен нормальный bearing (≈180°), иначе курс
    замораживается на текущем и расстояние до цели начинает расти.
    """
    dx = x_tgt - x_cur
    dz = y_tgt - y_cur
    if dx * dx + dz * dz < degenerate_tol_m * degenerate_tol_m:
        return float(current_yaw_deg)
    return calculate_target_yaw(x_cur, y_cur, x_tgt, y_tgt)


def normalize_angle(angle_deg: float) -> float:
    """
    Нормализация угла в диапазон [-180; 180] градусов.
    """
    while angle_deg > 180.0:
        angle_deg -= 360.0
    while angle_deg < -180.0:
        angle_deg += 360.0
    return angle_deg


def calculate_yaw_error(target_yaw: float, current_yaw: float) -> float:
    """
    Ошибка по курсу с учётом перехода через 0/360 градусов.
    """
    error = target_yaw - current_yaw
    return normalize_angle(error)


def distance_to_waypoint(
    position: Tuple[float, float], waypoint: Waypoint
) -> float:
    """Вспомогательная функция: расстояние от текущей позиции до путевой точки."""
    x, y = position
    wx, wy, _ = waypoint
    return calculate_distance(x, y, wx, wy)
    
    
