"""
Основной скрипт миссии движения по путевым точкам.

Соответствует структуре, описанной в ТЗ (файлы `ТЗ.txt` и `Бланк.txt`):
- модуль задания путевых точек;
- модуль навигации;
- модуль управления движением;
- модуль логирования;
- основной цикл с частотой 10–20 Гц;
- сохранение лога и последующая визуализация траектории.

Скрипт предназначен для запуска в среде MUR IDE в режиме Local.

Важно для симулятора
---------------------
1) В окне симулятора включите **Remote mode** (меню «Remote mode» или Ctrl+M).
   Иначе команды моторов из pymurapi не прикладываются к аппарату — он не поедет.

2) Координаты X/Y в телеметрии ZMQ **не передаются** (есть курс, глубина и др.).
   Для расчёта расстояния до waypoints используется **одометрия** (модуль odometry.py).
   Если по логу расстояние «не убывает», подстройте ODOMETRY_SPEED_SCALE в odometry.py.

   Управление моторами 0–3 (и сброс 4) приведено к логике примеров **sim_yaw_preg** и
   **sim_depth_preg**; базовая тяга как в **sim_test** (~40), не «аппаратный» auv_*.

   У цели при **почти нулевом векторе (dx,dy)** курс не берётся из atan2(0,0); порог
   порядка сантиметров по |dx|,|dy|, а не по полному расстоянию до точки (см. navigation). Плюс
   ограничение |res| в control.py.

3) WaypointManager: внутренний схват — ``distance <= capture_radius + reach_slack``; флаг
   «подошли снаружи» ставится при ``distance > approach_ring_m`` (меньше внутреннего порога).
   Так не ловим ложный старт на (0,0), но при колебаниях 3–11 см одометрия хотя бы раз
   превышает кольцо подхода (~6 см) и переход к следующей точке возможен.

Размер сцены и координаты
-------------------------
Точный «размер бассейна» задаётся геометрией **конкретной открытой сцены**. В симуляторе
MUR вертикаль — ось Y (глубина совпадает с датчиком, знак как в pymurapi); **горизонталь
маршрута — плоскость XZ**. В CSV и в коде поля X и путевой «Y» трактуются как мировые
**X и Z** (вторая координата — не ось глубины; глубина — третий столбец CSV).
Одометрия и расчёт целевого курса согласованы с курсом get_yaw() (вперёд при yaw≈0 вдоль +Z).
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Tuple

import pymurapi as mur  # type: ignore

from waypoints import WaypointManager, load_waypoints_from_csv, default_waypoints
from navigation import calculate_target_yaw_near_aware, distance_to_waypoint
from control import sim_motor_commands, apply_motor_commands, SIM_BASE_FORWARD
from logger_module import Logger
from odometry import step_dead_reckoning


WAYPOINTS_FILE = Path(__file__).resolve().parent / "waypoints.csv"

# Базовый радиус схватывания (м); к нему добавляется REACH_SLACK_M — иначе одометрия
# «крутится» у цели на 4–11 см и никогда не попадает в узкий круг.
CAPTURE_RADIUS = 0.10
REACH_SLACK_M = 0.05
# Меньше «внутреннего» схвата: разрешить «были снаружи» при типичной дрожи одометрии.
APPROACH_RING_M = 0.06
# Только если вектор к цели короче этого (м), курс не из atan2 (см. navigation).
BEARING_DEGENERATE_M = 0.08
CYCLES = 2

UPDATE_HZ = 10.0
UPDATE_DT = 1.0 / UPDATE_HZ

LOG_INTERVAL = 1.0  # сек

# Ниже этого расстояния (м) линейно снижаем базовую тягу — в малом бассейне иначе
# срыв в стену на финишном участке при том, что одометрия ещё показывает 0.3–0.5 м.
_APPROACH_RAMP_M = 0.45
_APPROACH_FWD_MIN = 22.0


def scaled_base_forward(distance_m: float) -> float:
    """Базовая тяга «вперёд»: полная далеко от точки, мягче при сближении."""
    if distance_m >= _APPROACH_RAMP_M:
        return float(SIM_BASE_FORWARD)
    if distance_m <= 0.0:
        return _APPROACH_FWD_MIN
    t = distance_m / _APPROACH_RAMP_M
    return _APPROACH_FWD_MIN + (float(SIM_BASE_FORWARD) - _APPROACH_FWD_MIN) * t


def get_position_from_api(auv) -> Tuple[float, float, float] | None:
    """
    Если в pymurapi есть реальные мировые координаты — вернуть (x, y, z);
    иначе None (тогда используется одометрия в main).
    """
    try:
        x = float(auv.get_x())
        y = float(auv.get_y())
    except AttributeError:
        return None
    z = float(auv.get_depth())
    return x, y, z


def main() -> None:
    auv = mur.mur_init()
    if auv is None:
        print("Ошибка: не удалось подключиться к симулятору")
        return

    time.sleep(0.5)

    print(
        "Симулятор: включите Remote mode (меню или Ctrl+M), иначе моторы из скрипта "
        "не управляют аппаратом."
    )

    if WAYPOINTS_FILE.exists():
        try:
            waypoints = load_waypoints_from_csv(WAYPOINTS_FILE)
            print(f"Загружено путевых точек из файла {WAYPOINTS_FILE}: {len(waypoints)}")
        except ValueError as exc:
            print(f"Предупреждение: ошибка чтения файла с точками: {exc}")
            print("Будут использованы точки по умолчанию.")
            waypoints = default_waypoints()
    else:
        print(f"Файл {WAYPOINTS_FILE} не найден. Будут использованы точки по умолчанию.")
        waypoints = default_waypoints()

    manager = WaypointManager(
        waypoints=waypoints,
        capture_radius=CAPTURE_RADIUS,
        reach_slack_m=REACH_SLACK_M,
        approach_ring_m=APPROACH_RING_M,
        cycles=CYCLES,
    )
    print(
        f"Схват точки: расстояние ≤ {CAPTURE_RADIUS + REACH_SLACK_M:.2f} м "
        f"(радиус {CAPTURE_RADIUS} м + допуск {REACH_SLACK_M} м); "
        f"кольцо подхода: > {APPROACH_RING_M:.2f} м."
    )

    logger = Logger()

    last_log_time = 0.0
    api_xy = get_position_from_api(auv)
    use_api_xy = api_xy is not None
    if use_api_xy:
        print("Координаты: используются get_x()/get_y() из API.")
    else:
        print(
            "Координаты: API без get_x/get_y — включена одометрия по курсу и моторам 0–1 "
            "(см. odometry.py, коэффициент ODOMETRY_SPEED_SCALE)."
        )

    est_x, est_y = 0.0, 0.0
    last_m0, last_m1 = 0, 0
    loop_prev = time.time()

    print("Запуск основного цикла движения по путевым точкам...")

    try:
        while not manager.is_finished():
            loop_start = time.time()

            now = time.time()
            dt = min(now - loop_prev, 0.25)
            loop_prev = now

            if use_api_xy:
                pos = get_position_from_api(auv)
                assert pos is not None
                x, y, z = pos
            else:
                est_x, est_y = step_dead_reckoning(
                    est_x, est_y, float(auv.get_yaw()), last_m0, last_m1, dt
                )
                x, y = est_x, est_y
                z = float(auv.get_depth())

            current_yaw = float(auv.get_yaw())

            current_wp = manager.current()
            if current_wp is None:
                break

            distance = distance_to_waypoint((x, y), current_wp)
            target_yaw = calculate_target_yaw_near_aware(
                x,
                y,
                current_wp[0],
                current_wp[1],
                current_yaw,
                degenerate_tol_m=BEARING_DEGENERATE_M,
            )

            motors = sim_motor_commands(
                current_yaw,
                target_yaw,
                z,
                current_wp[2],
                base_forward=scaled_base_forward(distance),
            )
            apply_motor_commands(auv, motors)
            last_m0, last_m1 = motors[0], motors[1]

            manager.advance_if_reached(distance)

            now = time.time()
            if now - last_log_time >= LOG_INTERVAL:
                logger.log(
                    x=x,
                    y=y,
                    z=z,
                    yaw=current_yaw,
                    target_yaw=target_yaw,
                    distance=distance,
                    motors=motors,
                    waypoint_index=manager._current_index,
                )
                last_log_time = now

            print(
                f"Точка {manager._current_index + 1}/{len(manager.waypoints)}, "
                f"цикл {manager._completed_cycles + 1}/{manager.cycles}, "
                f"расстояние до цели: {distance:.2f} м, "
                f"глубина: {z:.2f} м, курс: {current_yaw:.1f}°"
            )

            elapsed = time.time() - loop_start
            sleep_time = UPDATE_DT - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)

    finally:
        apply_motor_commands(auv, (0, 0, 0, 0))
        logger.close()
        print("Миссия завершена, лог сохранён.")


if __name__ == "__main__":
    main()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
