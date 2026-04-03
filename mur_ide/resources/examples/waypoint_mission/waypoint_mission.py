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
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Tuple

import pymurapi as mur  # type: ignore

from waypoints import WaypointManager, load_waypoints_from_csv, default_waypoints
from navigation import calculate_target_yaw, calculate_yaw_error, distance_to_waypoint
from control import yaw_control, depth_control, motor_commands, apply_motor_commands, BASE_POWER
from logger_module import Logger


WAYPOINTS_FILE = Path(__file__).resolve().parent / "waypoints.csv"

CAPTURE_RADIUS = 0.5  # м
CYCLES = 2

UPDATE_HZ = 10.0
UPDATE_DT = 1.0 / UPDATE_HZ

LOG_INTERVAL = 1.0  # сек


def get_position(auv) -> Tuple[float, float, float]:
    """
    Получение текущих координат аппарата.

    В зависимости от версии pymurapi координаты могут быть доступны
    напрямую через отдельные функции. Если таких функций нет, допускается
    заглушечная реализация или использование одометрии.

    В данном варианте предполагается наличие методов get_x(), get_y(), get_depth().
    При необходимости их можно заменить на фактически доступные в используемой
    версии библиотеки pymurapi.
    """
    try:
        x = float(auv.get_x())
        y = float(auv.get_y())
    except AttributeError:
        x = 0.0
        y = 0.0
    z = float(auv.get_depth())
    return x, y, z


def main() -> None:
    auv = mur.mur_init()
    if auv is None:
        print("Ошибка: не удалось подключиться к симулятору")
        return

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

    manager = WaypointManager(waypoints=waypoints, capture_radius=CAPTURE_RADIUS, cycles=CYCLES)

    logger = Logger()

    last_log_time = 0.0

    print("Запуск основного цикла движения по путевым точкам...")

    try:
        while not manager.is_finished():
            loop_start = time.time()

            x, y, z = get_position(auv)
            current_yaw = float(auv.get_yaw())

            current_wp = manager.current()
            if current_wp is None:
                break

            distance = distance_to_waypoint((x, y), current_wp)
            target_yaw = calculate_target_yaw(x, y, current_wp[0], current_wp[1])

            yaw_err = calculate_yaw_error(target_yaw, current_yaw)
            depth_err = current_wp[2] - z

            yaw_u = yaw_control(yaw_err)
            depth_u = depth_control(depth_err)

            motors = motor_commands(yaw_u, depth_u, base_power=BASE_POWER)
            apply_motor_commands(auv, motors)

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
