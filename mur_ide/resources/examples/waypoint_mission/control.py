"""
Модуль управления движением.

Соответствует разделам 1.3, 3.4 ТЗ:
– пропорциональные регуляторы для курса и глубины;
– формирование команд для движителей.
"""

from __future__ import annotations

from typing import Tuple


# Диапазон допустимых значений мощности движителей в pymurapi
MIN_POWER = -100
MAX_POWER = 100

# Базовая мощность для движения вперёд
BASE_POWER = 50

# Коэффициенты П‑регуляторов (могут подбираться экспериментально)
KP_YAW = 1.5
KP_DEPTH = 0.8


def clamp(value: float, lo: float, hi: float) -> float:
    """Ограничение значения в заданном диапазоне."""
    return max(lo, min(hi, value))


def yaw_control(yaw_error: float) -> float:
    """
    Управляющий сигнал регулятора курса.
    Возвращает значение в условных единицах, которое затем
    преобразуется в разность мощностей левого и правого движителей.
    """
    u = KP_YAW * yaw_error
    # Ограничиваем, чтобы поворот не был слишком резким
    return clamp(u, -50.0, 50.0)


def depth_control(depth_error: float) -> float:
    """
    Управляющий сигнал регулятора глубины.
    Положительное значение соответствует погружению, отрицательное – всплытию.
    """
    u = KP_DEPTH * depth_error
    return clamp(u, -50.0, 50.0)


def motor_commands(
    yaw_u: float,
    depth_u: float,
    base_power: float = BASE_POWER,
) -> Tuple[int, int, int, int]:
    """
    Формирование команд для четырёх движителей.

    Предполагается конфигурация MiddleAUV:
    – двигатели 0 и 1 – горизонтальные;
    – двигатели 2 и 3 – вертикальные.
    """
    # Дифференциальное управление по курсу
    m0 = base_power - yaw_u  # левый горизонтальный
    m1 = base_power + yaw_u  # правый горизонтальный

    # Одинаковые команды для вертикальных движителей
    m2 = depth_u
    m3 = depth_u

    return (
        int(clamp(m0, MIN_POWER, MAX_POWER)),
        int(clamp(m1, MIN_POWER, MAX_POWER)),
        int(clamp(m2, MIN_POWER, MAX_POWER)),
        int(clamp(m3, MIN_POWER, MAX_POWER)),
    )


def apply_motor_commands(auv, commands: Tuple[int, int, int, int]) -> None:
    """
    Отправка команд на движители через API pymurapi.

    Параметр auv – объект, полученный через mur.mur_init().
    """
    m0, m1, m2, m3 = commands
    auv.set_motor_power(0, m0)
    auv.set_motor_power(1, m1)
    auv.set_motor_power(2, m2)
    auv.set_motor_power(3, m3)
    
    
