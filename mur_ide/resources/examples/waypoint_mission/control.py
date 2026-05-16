"""
Модуль управления движением (симулятор).

Согласован с официальными примерами `sim_yaw_preg.py` и `sim_depth_preg.py`:
– курс: разница мощностей 0/1 как `res = er * (-0.8)`, базовая тяга как в sim_*;
– глубина: `80 * (get_depth() - целевая)` на моторы 2 и 3, как в sim_depth_preg.

На реальном аппарате (auv_yaw_preg / другие индексы моторов) этот модуль не подходит.
"""

from __future__ import annotations

from typing import Tuple

from navigation import calculate_yaw_error

MIN_POWER = -100
MAX_POWER = 100

# Как в sim_test / sim_yaw_preg (не 50 — меньше разгон к стенам в малом бассейне)
SIM_BASE_FORWARD = 40

# Как sim_yaw_preg: res = er * (-0.8); ограничиваем |res|, иначе при большой ошибке
# m0/m1 упираются в ±100 и средняя тяга ~0 — аппарат крутится на месте.
SIM_YAW_RES_GAIN = -0.8
SIM_YAW_RES_ABS_MAX = 28.0

# Как sim_depth_preg: power = 80 * (get_depth() - depth_to_set)
SIM_DEPTH_GAIN = 80.0


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def sim_motor_commands(
    current_yaw: float,
    target_yaw_deg: float,
    depth_measured: float,
    depth_target: float,
    base_forward: float = SIM_BASE_FORWARD,
) -> Tuple[int, int, int, int]:
    """
    Четыре мощности для симулятора (моторы 0–3), в духе sim_yaw_preg + sim_depth_preg.
    """
    er = calculate_yaw_error(target_yaw_deg, current_yaw)
    res = clamp(SIM_YAW_RES_GAIN * er, -SIM_YAW_RES_ABS_MAX, SIM_YAW_RES_ABS_MAX)
    m0 = int(clamp(base_forward - res, MIN_POWER, MAX_POWER))
    m1 = int(clamp(base_forward + res, MIN_POWER, MAX_POWER))

    depth_cmd = SIM_DEPTH_GAIN * (depth_measured - depth_target)
    m2 = int(clamp(depth_cmd, MIN_POWER, MAX_POWER))
    m3 = m2

    return (m0, m1, m2, m3)


def apply_motor_commands(auv, commands: Tuple[int, int, int, int]) -> None:
    """Отправка команд; в симуляторе есть ещё мотор 4 — обнуляем, чтобы не копил мусор."""
    m0, m1, m2, m3 = commands
    auv.set_motor_power(0, m0)
    auv.set_motor_power(1, m1)
    auv.set_motor_power(2, m2)
    auv.set_motor_power(3, m3)
    try:
        auv.set_motor_power(4, 0)
    except AttributeError:
        pass
    
