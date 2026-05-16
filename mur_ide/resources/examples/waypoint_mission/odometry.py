"""
Плоская одометрия для симулятора: pymurapi не передаёт мировые X/Y по ZMQ.

Интегрируем смещение по текущему курсу (get_yaw) и средней команде горизонтальных
моторов 0 и 1 за шаг dt. Масштаб подбирается эмпирически (см. ODOMETRY_SPEED_SCALE).
"""

from __future__ import annotations

import math
from typing import Tuple

# Подгонка «м/с на единицу средней тяги» под базовую тягу ~40 (sim_yaw_preg).
# При необходимости измените после проверки по логу расстояний.
# Эмпирически: при ~40 на моторах длина шага должна быть сопоставима с убыванием
# «расстояния до точки» в логе; заниженный масштаб даёт «ещё далеко» при ударе о стену.
ODOMETRY_SPEED_SCALE = 0.065


def step_dead_reckoning(
    x: float,
    y: float,
    yaw_deg: float,
    motor0: int,
    motor1: int,
    dt: float,
) -> Tuple[float, float]:
    """
    Оценка положения в горизонтальной плоскости сцены MUR.

    x, y — соответственно мировые X и Z; курс yaw — из get_yaw() (поворот вокруг Y).
    Вперёд по корпусу = +Z в мире при yaw=0 (см. силы на m_forward в симуляторе).
    """
    if dt <= 0.0:
        return x, y

    yaw_rad = math.radians(yaw_deg)
    fwd = 0.5 * (float(motor0) + float(motor1))
    v = (fwd / 100.0) * ODOMETRY_SPEED_SCALE
    x += v * math.sin(yaw_rad) * dt
    y += v * math.cos(yaw_rad) * dt
    return x, y
