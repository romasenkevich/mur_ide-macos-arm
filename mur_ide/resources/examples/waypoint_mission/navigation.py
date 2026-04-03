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

    Угол считается от оси X, положительное направление — против часовой стрелки.
    """
    dx = x_tgt - x_cur
    dy = y_tgt - y_cur
    yaw_rad = math.atan2(dy, dx)
    yaw_deg = math.degrees(yaw_rad)
    return yaw_deg


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
    
